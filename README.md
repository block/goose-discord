# Agent Honk 🦆

A Discord bot wrapper around Goose AI that brings the power of Goose to your Discord server!

## Features

- **Slash Command Integration**: Use `/honk` to start a new Goose session
- **Persistent Threads**: Each session runs in its own Discord thread with full context
- **Interactive Conversations**: Continue chatting in threads and Goose maintains context
- **Easy Setup**: Built with Python 3.13 and uv for modern dependency management

## Quick Start

1. **Clone and Setup**:
   ```bash
   cd discord-goose
   uv sync
   ```

2. **Configure Discord Bot**:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application and bot
   - Copy the bot token
   - Enable "Message Content Intent" in bot settings

3. **Environment Setup**:
   ```bash
   cp .env.example .env
   # Edit .env and add your DISCORD_TOKEN
   ```

4. **Run the Bot**:
   ```bash
   uv run python -m src.agent_honk.bot
   ```

## Usage

1. Invite the bot to your Discord server with appropriate permissions
2. Use `/honk <your prompt>` to start a new Goose session
3. Continue the conversation in the created thread
4. Goose will respond with full context awareness!

## Example

```
/honk You are a bird enthusiast. You'll answer all of my questions and also tell me fun bird facts. Start by telling me a bird fact.
```

This creates a new thread where Goose will roleplay as a bird enthusiast and provide fun facts!

## Requirements

- Python 3.13+
- uv package manager
- Discord bot token
- Goose CLI installed and accessible

## Architecture

- **bot.py**: Main Discord bot with slash commands and message handling
- **goose_client.py**: Interface to Goose CLI for running sessions
- **thread_manager.py**: Manages Discord thread state and ownership

## Future Features

- Dynamic form creation
- Scheduled polls and tasks
- Web scraping capabilities
- Multi-server session management

## Contributing

This is part of the Goose ecosystem. Feel free to contribute improvements and new features!
