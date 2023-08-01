import os
import shutil
import tarfile
import zipfile

from cog import BaseModel, Input, Path

from predict import SDXL_MODEL_CACHE, SDXL_URL, download_weights
from trainer_pti import main
from preprocess import preprocess


"""
Wrapper around actual trainer.
"""
OUTPUT_DIR = "training_out"


class TrainingOutput(BaseModel):
    weights: Path


from typing import Tuple


def train(
    input_images: Path = Input(
        description="A .zip or .tar file containing the image files that will be used for fine-tuning"
    ),
    seed: int = Input(
        description="Random seed for reproducible training. Leave empty to use a random seed",
        default=None,
    ),
    resolution: int = Input(
        description="Square pixel resolution which your images will be resized to for training",
        default=512,
    ),
    train_batch_size: int = Input(
        description="Batch size (per device) for training",
        default=4,
    ),
    num_train_epochs: int = Input(
        description="Number of epochs to loop through your training dataset",
        default=400,
    ),
    max_train_steps: int = Input(
        description="Number of individual training steps. Takes precedence over num_train_epochs",
        default=None,
    ),
    # gradient_accumulation_steps: int = Input(
    #     description="Number of training steps to accumulate before a backward pass. Effective batch size = gradient_accumulation_steps * batch_size",
    #     default=1,
    # ), # todo.
    unet_learning_rate: float = Input(
        description="Learning rate for the U-Net. We recommend this value to be somewhere between `1e-6` to `1e-5`.",
        default=3e-6,
    ),
    ti_learning_rate_multiplier: float = Input(
        description="Scaling of learning rate for training textual inversion embeddings. Don't alter unless you know what you're doing.",
        default=100,
    ),
    lr_scheduler: str = Input(
        description="Learning rate scheduler to use for training",
        default="constant",
        choices=[
            "constant",
            "linear",
            "cosine",
            "cosine_with_restarts",
            "polynomial",
            "constant_with_warmup",
        ],
    ),
    lr_warmup_steps: int = Input(
        description="Number of warmup steps for lr schedulers with warmups.",
        default=500,
    ),
    lr_num_cycles: int = Input(
        description="Number of hard restarts used with `cosine_with_restarts` learning rate scheduler",
        default=1,
    ),
    lr_power: float = Input(
        description="Power for polynomial learning rate scheduler", default=1.0
    ),
    token_string: str = Input(
        description="A unique string that will be trained to refer to the concept in the input images. Can be anything, but TOK works well",
        default="TOK",
    ),
    # token_map: str = Input(
    #     description="String of token and their impact size specificing tokens used in the dataset. This will be in format of `token1:size1,token2:size2,...`.",
    #     default="TOK:2",
    # ),
    caption_prefix: str = Input(
        description="Text which will be used as prefix during automatic captioning. Must contain the `token_string`. For example, if caption text is 'a photo of TOK', automatic captioning will expand to 'a photo of TOK under a bridge', 'a photo of TOK holding a cup', etc.",
        default="a photo of TOK",
    ),
    mask_target_prompts: str = Input(
        description="Prompt that describes part of the image that you will find important. For example, if you are fine-tuning your pet, `photo of a dog` will be a good prompt. Prompt-based masking is used to focus the fine-tuning process on the important/salient parts of the image",
        default=None,
    ),
    crop_based_on_salience: bool = Input(
        description="If you want to crop the image to `target_size` based on the important parts of the image, set this to True. If you want to crop the image based on face detection, set this to False",
        default=True,
    ),
    use_face_detection_instead: bool = Input(
        description="If you want to use face detection instead of CLIPSeg for masking. For face applications, we recommend using this option.",
        default=False,
    ),
    clipseg_temperature: float = Input(
        description="How blurry you want the CLIPSeg mask to be. We recommend this value be something between `0.5` to `1.0`. If you want to have more sharp mask (but thus more errorful), you can decrease this value.",
        default=1.0,
    ),
    verbose: bool = Input(description="verbose output", default=True),
) -> TrainingOutput:

    # Hard-code token_map for now. Make it configurable once we support multiple concepts or user-uploaded caption csv.
    token_map = token_string + ":2"

    # Process 'token_to_train' and 'input_data_tar_or_zip'
    inserting_list_tokens = token_map.split(",")

    token_dict = {}
    running_tok_cnt = 0
    all_token_lists = []
    for token in inserting_list_tokens:
        n_tok = int(token.split(":")[1])

        token_dict[token.split(":")[0]] = "".join(
            [f"<s{i + running_tok_cnt}>" for i in range(n_tok)]
        )
        all_token_lists.extend([f"<s{i + running_tok_cnt}>" for i in range(n_tok)])

        running_tok_cnt += n_tok

    input_dir = preprocess(
        input_zip_path=input_images,
        caption_text=caption_prefix,
        mask_target_prompts=mask_target_prompts,
        target_size=resolution,
        crop_based_on_salience=crop_based_on_salience,
        use_face_detection_instead=use_face_detection_instead,
        temp=clipseg_temperature,
        substitution_tokens=list(token_dict.keys()),
    )

    if not os.path.exists(SDXL_MODEL_CACHE):
        download_weights(SDXL_URL, SDXL_MODEL_CACHE)
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    main(
        pretrained_model_name_or_path=SDXL_MODEL_CACHE,
        instance_data_dir=os.path.join(input_dir, "captions.csv"),
        output_dir=OUTPUT_DIR,
        seed=seed,
        resolution=resolution,
        train_batch_size=train_batch_size,
        num_train_epochs=num_train_epochs,
        max_train_steps=max_train_steps,
        gradient_accumulation_steps=1,
        unet_learning_rate=unet_learning_rate,
        ti_learning_rate_multiplier=ti_learning_rate_multiplier,
        lr_scheduler=lr_scheduler,
        lr_warmup_steps=lr_warmup_steps,
        lr_num_cycles=lr_num_cycles,
        lr_power=lr_power,
        token_dict=token_dict,
        inserting_list_tokens=all_token_lists,
        verbose=verbose,
        crops_coords_top_left_h=0,
        crops_coords_top_left_w=0,
        do_cache=True,
        checkpointing_steps=500000,
        scale_lr=False,
        dataloader_num_workers=0,
        max_grad_norm=1.0,
        allow_tf32=True,
        mixed_precision="bf16",
        device="cuda:0",
    )

    directory = Path(OUTPUT_DIR)
    out_path = "trained_model.tar"

    with tarfile.open(out_path, "w") as tar:
        for file_path in directory.rglob("*"):
            print(file_path)
            arcname = file_path.relative_to(directory)
            tar.add(file_path, arcname=arcname)

    return TrainingOutput(weights=Path(out_path))
