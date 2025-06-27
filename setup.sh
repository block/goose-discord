#!/bin/bash

# Agent Honk Setup Script
echo "🦆 Setting up Agent Honk Discord Bot..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check if goose is installed
if ! command -v goose &> /dev/null; then
    echo "⚠️  Warning: goose command not found in PATH"
    echo "   Make sure Goose is installed and accessible"
    echo "   You can install it from: https://github.com/block/goose"
fi

# Initialize uv project
echo "📦 Installing dependencies..."
uv sync

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ Created .env file. Please edit it and add your DISCORD_TOKEN"
else
    echo "✅ .env file already exists"
fi

# Run tests to make sure everything works
echo "🧪 Running tests..."
uv run pytest tests/ -v

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your Discord bot token"
echo "2. Create a Discord application and bot at https://discord.com/developers/applications"
echo "3. Invite the bot to your server with appropriate permissions"
echo "4. Run the bot with: uv run python run_bot.py"
echo ""
echo "🦆 Happy honking!"
