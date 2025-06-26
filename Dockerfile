# Use the official uv image with Python 3.13
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    fontconfig \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Change the working directory to the `app` directory
WORKDIR /app

# Enable bytecode compilation for better performance
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Copy the project configuration
COPY pyproject.toml ./

# Install dependencies (without lock file)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project

# Copy the project into the image
COPY . /app

# Sync the project (install the actual project)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

# Create output directory
RUN mkdir -p output

# Verify data files are present
RUN ls -la /app/data/ && python verify_data.py

# Expose port for Gradio
EXPOSE 7860

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Run the application using uv
CMD ["uv", "run", "python", "main.py"]