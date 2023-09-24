# Install cog via curl
sudo curl -o /usr/local/bin/cog -L "https://github.com/replicate/cog/releases/latest/download/cog_$(uname -s)_$(uname -m)"
sudo chmod +x /usr/local/bin/cog

sudo apt-get install git
# sudo apt-get install docker
sudo apt update && \
sudo apt install apt-transport-https ca-certificates curl software-properties-common -y && \
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add - && \
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable" && \
sudo apt update && \
sudo apt install docker-ce -y && \
sudo systemctl enable docker && \
sudo systemctl start docker && \
sudo docker --version


# Get docker permissions
sudo usermod -aG docker $USER
newgrp docker
sudo systemctl restart docker

#clone this repo!
git clone https://github.com/Vkzem/cog-sdxl-test.git    
