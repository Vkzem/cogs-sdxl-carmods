# Install cog via curl
sudo curl -o /usr/local/bin/cog -L "https://github.com/replicate/cog/releases/latest/download/cog_$(uname -s)_$(uname -m)"
sudo chmod +x /usr/local/bin/cog

# Get docker permissions
sudo usermod -aG docker $USER
newgrp docker
sudo systemctl restart docker

#clone this repo!
git clone https://github.com/Vkzem/cog-sdxl-test.git
