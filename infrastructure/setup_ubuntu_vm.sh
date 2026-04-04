#!/bin/bash
# Automates the setup of the Oracle Ubuntu VM for the local LLM.

echo "Starting local LLM setup..."

# 1. Update system packages
echo "Updating system..."
sudo apt update && sudo apt upgrade -y

# 2. Install Python tools (Added python3-full to comply with PEP 668 and prevent externally-managed errors)
echo "Installing Python, pip, and venv tools..."
sudo apt install python3-full python3-pip python3-venv -y

# 3. Install Ollama
echo "Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# 4. Pull the Gemma 4 E4B model
echo "Pulling Gemma-4-E4B model..."
ollama pull gemma4:e4b

# 5. Pull the Embedding Model
echo "Pulling Nomic Embed Text model..."
ollama pull nomic-embed-text

echo "======================================================="
echo "Setup complete! Ollama is running as a background service."
echo "======================================================="
