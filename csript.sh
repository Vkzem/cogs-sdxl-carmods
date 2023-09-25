# Install cog via curl
sudo curl -o /usr/local/bin/cog -L "https://github.com/replicate/cog/releases/latest/download/cog_$(uname -s)_$(uname -m)"
sudo chmod +x /usr/local/bin/cog

# sudo apt-get install git
# # sudo apt-get install docker
# sudo apt update && \
# sudo apt install apt-transport-https ca-certificates curl software-properties-common -y && \
# curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add - && \
# sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable" && \
# sudo apt update && \
# sudo apt install docker-ce -y && \
# sudo systemctl enable docker && \
# sudo systemctl start docker && \
# su



#clone this repo!
sudo curl -o /usr/local/bin/cog -L "https://github.com/replicate/cog/releases/latest/download/cog_$(uname -s)_$(uname -m)"
sudo chmod +x /usr/local/bin/cog

mkdir working
cd working

git clone https://github.com/Vkzem/cog-sdxl-carmods.git    
cd cog-sdxl-carmods


cog predict -i prompt='a red car'

cog train -i input_images=@data.zip