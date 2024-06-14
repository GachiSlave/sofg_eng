# For telegram_utils.py

# Download base image ubuntu 22.04
FROM ubuntu:22.04

# LABEL about the custom image
LABEL maintainer="organismus22@gmail.com"
LABEL version="1.0"
LABEL description="docker agent for jenkins"

# Disable Prompt During Packages Installation
ARG DEBIAN_FRONTEND=noninteractive

# Update Ubuntu Software repository and install required packages
RUN apt update && apt-get install -y \
  git \
  python3 \
  python3-venv \
  python3-pip \
  && apt-get clean

# Install necessary Python packages
RUN pip3 install --no-cache-dir requests

# Add Jenkins user
RUN useradd -ms /bin/bash Jenkins

# Switch to Jenkins user
USER Jenkins
WORKDIR /home/Jenkins

# Copy repository content
COPY . .

# Run the test script
CMD ["python3", "telegram_utils.py"]
