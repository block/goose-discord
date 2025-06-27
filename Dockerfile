FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/
COPY run_bot.py ./

# Install dependencies
RUN uv sync --frozen

# Create non-root user
RUN useradd -m -u 1000 honk
USER honk

# Set environment variables
ENV PYTHONPATH=/app/src

# Run the bot
CMD ["uv", "run", "python", "run_bot.py"]
