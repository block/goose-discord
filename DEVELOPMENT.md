# Development Guide for Agent Honk 🦆

## Project Structure

```
discord-goose/
├── src/agent_honk/          # Main bot package
│   ├── __init__.py
│   ├── bot.py              # Discord bot main logic
│   ├── goose_client.py     # Goose CLI interface
│   └── thread_manager.py   # Thread state management
├── tests/                  # Test files
├── pyproject.toml          # Project configuration
├── run_bot.py             # Simple bot runner
├── setup.sh               # Setup script
├── Dockerfile             # Docker container
└── docker-compose.yml     # Docker Compose config
```

## Development Setup

1. **Prerequisites**:
   - Python 3.13+
   - uv package manager
   - Goose CLI installed
   - Discord bot token

2. **Quick Setup**:
   ```bash
   ./setup.sh
   ```

3. **Manual Setup**:
   ```bash
   uv sync
   cp .env.example .env
   # Edit .env with your Discord token
   ```

## Running the Bot

### Local Development
```bash
# Using uv
uv run python run_bot.py

# Or directly
uv run python -m src.agent_honk.bot
```

### Docker
```bash
docker-compose up --build
```

## Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/agent_honk

# Run specific test
uv run pytest tests/test_thread_manager.py -v
```

## Code Quality

```bash
# Format code
uv run black src/ tests/

# Lint code
uv run ruff check src/ tests/

# Type checking (if mypy is added)
uv run mypy src/
```

## Architecture

### Bot Flow
1. User runs `/honk <prompt>` slash command
2. Bot creates a new Discord thread
3. Thread is registered in ThreadManager
4. Initial prompt sent to GooseClient
5. Goose response posted in thread
6. Subsequent messages in thread continue the conversation

### Key Components

#### `bot.py`
- Main Discord bot class
- Handles slash commands and message events
- Manages thread creation and message routing

#### `goose_client.py`
- Interface to Goose CLI
- Manages session directories
- Handles command execution and response parsing

#### `thread_manager.py`
- Tracks active Goose threads
- Manages thread ownership and metadata
- Provides statistics and cleanup utilities

## Adding Features

### New Slash Commands
Add commands to `bot.py`:
```python
@discord.app_commands.command(name="newcommand", description="Description")
async def new_command(interaction: discord.Interaction, param: str):
    # Implementation
    pass

# Register in main()
bot.tree.add_command(new_command)
```

### Enhanced Goose Integration
Modify `goose_client.py` to:
- Add new Goose command options
- Implement session persistence
- Add file upload/download support

### Thread Management Features
Extend `thread_manager.py` for:
- Thread archiving
- User permissions
- Session sharing

## Deployment

### Environment Variables
- `DISCORD_TOKEN`: Required Discord bot token
- `LOG_LEVEL`: Optional logging level (DEBUG, INFO, WARNING, ERROR)
- `GOOSE_COMMAND`: Optional path to goose binary

### Production Considerations
- Use proper logging configuration
- Implement session cleanup for long-running deployments
- Monitor memory usage for active sessions
- Consider rate limiting for heavy usage

## Troubleshooting

### Common Issues

1. **"goose command not found"**
   - Ensure Goose is installed and in PATH
   - Set GOOSE_COMMAND environment variable

2. **Discord permissions errors**
   - Bot needs "Send Messages", "Create Threads", "Use Slash Commands"
   - Check bot is invited with correct permissions

3. **Session directories filling up**
   - Implement cleanup in production
   - Monitor /tmp directory usage

### Debug Mode
Set `LOG_LEVEL=DEBUG` for verbose logging:
```bash
export LOG_LEVEL=DEBUG
uv run python run_bot.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run code quality checks
5. Submit a pull request

## Future Enhancements

- [ ] Web dashboard for session management
- [ ] Persistent session storage
- [ ] Multi-server support
- [ ] Form/poll creation features
- [ ] Scheduled task system
- [ ] Web scraping integration
- [ ] File upload/download support
- [ ] Session sharing between users
