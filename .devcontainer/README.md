# FamilyHuddle Dev Container Setup

This dev container provides a complete development environment for FamilyHuddle with:
- Python 3.11 with UV package manager
- Docker-in-Docker support for running Supabase locally
- Pre-configured VS Code extensions
- Automatic Supabase and Streamlit startup

## Features

### 1. UV Package Manager
The modern Python package manager UV is pre-installed and configured to work with the project's `pyproject.toml`.

### 2. Docker-in-Docker
Enables running Supabase's Docker containers inside the dev container, providing a fully isolated development environment.

### 3. Supabase Local Development
The local Supabase stack (PostgreSQL, Auth, Storage, Realtime) runs inside the container with ports forwarded:
- **54321**: Supabase Studio (Database UI)
- **54322**: Inbucket (Email testing)
- **54323**: PostgreSQL database

### 4. Auto-configured VS Code
Includes Python extensions, formatters (Black), linters (Ruff), and Docker tools.

## Usage

1. **Open in Dev Container**: 
   - VS Code: Use "Reopen in Container" command
   - Or use the Dev Containers extension

2. **Automatic Setup**:
   - UV installs all Python dependencies
   - Supabase starts automatically
   - Streamlit launches on port 8501

3. **Initialize Database**:
   ```bash
   make init-data
   ```

4. **Access Services**:
   - Streamlit App: http://localhost:8501
   - Supabase Studio: http://localhost:54321
   - Email Testing: http://localhost:54322

## Environment Variables

The container automatically uses `.env.local` if present. To switch environments:
```bash
make use-local      # Use local Supabase
make use-production # Use production Supabase
```

## Common Commands

```bash
# Supabase management
make supabase-studio  # Open database UI
make supabase-stop    # Stop Supabase
make supabase-reset   # Reset database

# Development
make run             # Run Streamlit app
make test            # Run tests
make lint            # Run linting
make format          # Format code
```

## Troubleshooting

### Port Conflicts
If you have Supabase running on your host machine, stop it first:
```bash
supabase stop
```

### Rebuilding the Container
To rebuild with latest changes:
1. Command Palette → "Dev Containers: Rebuild Container"
2. Or: `docker-compose -f .devcontainer/docker-compose.yml down && docker-compose -f .devcontainer/docker-compose.yml up`

### UV Issues
UV is installed for the `vscode` user. If you have PATH issues:
```bash
export PATH="/home/vscode/.cargo/bin:${PATH}"
```