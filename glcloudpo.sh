for zone in asia-east1-a asia-east1-b asia-east1-c asia-northeast1-a asia-northeast1-c asia-northeast3-b asia-northeast3-c asia-south1-a asia-south1-b asia-southeast1-a asia-southeast1-b asia-southeast1-c asia-southeast2-a asia-southeast2-b asia-southeast2-c australia-southeast1-b australia-southeast1-c europe-west1-b europe-west1-c europe-west1-d europe-west2-a europe-west2-b europe-west3-b europe-west4-a europe-west4-b europe-west4-c northamerica-northeast1-a northamerica-northeast1-b northamerica-northeast1-c southamerica-east1-c us-central1-a us-central1-b us-central1-c us-central1-f us-east1-b us-east1-c us-east1-d us-east4-a us-east4-b us-east4-c us-west1-a us-west1-b us-west2-b us-west2-c us-west4-a us-west4-b
do
  gcloud compute instances create "gpu-machine-$zone" \
    --project=peak-haven-396503 \
    --zone="$zone" \
    --machine-type=n1-standard-1
done
