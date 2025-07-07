FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Note: Node.js is installed via devcontainer features
# Install Supabase CLI via npm (will be installed after Node.js feature is applied)
# This is handled in postCreateCommand instead

# Create vscode user if it doesn't exist
RUN if ! id -u vscode > /dev/null 2>&1; then \
        useradd -m -s /bin/bash vscode && \
        echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers; \
    fi

# Switch to vscode user for UV installation
USER vscode

# Install UV for vscode user
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/home/vscode/.cargo/bin:${PATH}"

# Set working directory
WORKDIR /workspace

# Copy UV path to vscode's profile
RUN echo 'export PATH="/home/vscode/.cargo/bin:${PATH}"' >> /home/vscode/.bashrc