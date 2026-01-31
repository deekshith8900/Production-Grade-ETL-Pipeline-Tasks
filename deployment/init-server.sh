#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Production Setup...${NC}"

# 1. Update OS
echo -e "${GREEN}Updating System Packages...${NC}"
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y curl git

# 2. Install Docker
if ! command -v docker &> /dev/null; then
    echo -e "${GREEN}Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker ubuntu
    echo "Docker installed. Please log out and back in for group changes to take effect, or run 'newgrp docker'."
else
    echo "Docker already installed."
fi

# 3. Clone Repository
REPO_DIR="Production-Grade-ETL-Pipeline-Tasks"
if [ -d "$REPO_DIR" ]; then
    echo "Repository already exists. Pulling latest..."
    cd $REPO_DIR
    git pull
else
    echo -e "${GREEN}Cloning Repository...${NC}"
    git clone https://github.com/deekshith8900/Production-Grade-ETL-Pipeline-Tasks.git
    cd $REPO_DIR
fi

# 4. Configure Environment
if [ ! -f .env ]; then
    echo -e "${GREEN}Configuring Environment...${NC}"
    echo "Please enter your GITHUB_TOKEN:"
    read -r GITHUB_TOKEN
    
    cat <<EOF > .env
GITHUB_TOKEN=$GITHUB_TOKEN
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
AWS_REGION=us-east-1
AWS_ENDPOINT_URL=http://localhost:9000
EOF
    echo ".env file created."
fi

# 5. Start Services
echo -e "${GREEN}Starting Containers...${NC}"
# Use current user group context
newgrp docker << END
    docker compose up -d --build
END

echo -e "${GREEN}Setup Complete! Access Airflow at http://$(curl -s ifconfig.me):8080${NC}"
