import torch
from diffusers import DiffusionPipeline

from safetensors import safe_open
from dataset_and_utils import TokenEmbeddingsHandler
from diffusers.models import AutoencoderKL

pipe = DiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=torch.float16,
        variant="fp16",
).to("cuda")

with safe_open("training_out/unet.safetensors", framework="pt", device="cuda") as f:
    for key in f.keys():
       tensors[key] = f.get_tensor(key)

pipe.unet.load_state_dict(tensors, strict=False) # should take < 2 seconds

text_encoders = [pipe.text_encoder, pipe.text_encoder_2]
tokenizers = [pipe.tokenizer, pipe.tokenizer_2]

embhandler = TokenEmbeddingsHandler(text_encoders, tokenizers)
embhandler.load_embeddings("training_out/embeddings.pti")


pipe(prompt="A photo of <s0><s1>").images[0].save("testout.png")

