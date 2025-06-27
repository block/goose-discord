# Quick Start Guide 🦆

## Get Agent Honk Running in 5 Minutes!

### 1. Setup Project
```bash
cd discord-goose
./setup.sh
```

### 2. Create Discord Bot
1. Go to https://discord.com/developers/applications
2. Click "New Application" → Name it "Agent Honk"
3. Go to "Bot" section → Click "Add Bot"
4. Copy the Token
5. Under "Privileged Gateway Intents" → Enable "Message Content Intent"

### 3. Configure Environment
```bash
# Edit .env file
nano .env

# Add your token:
DISCORD_TOKEN=your_bot_token_here
```

### 4. Invite Bot to Server
1. In Discord Developer Portal → "OAuth2" → "URL Generator"
2. Select Scopes: `bot` and `applications.commands`
3. Select Bot Permissions:
   - Send Messages
   - Create Public Threads
   - Use Slash Commands
   - Read Message History
4. Copy the generated URL and open it to invite the bot

### 5. Run the Bot
```bash
uv run python run_bot.py
```

### 6. Test It!
In your Discord server, type:
```
/honk You are a bird enthusiast. Tell me a fun fact about penguins!
```

The bot will create a thread and Goose will respond! 🎉

## Troubleshooting

**Bot doesn't respond to /honk:**
- Wait a few seconds for slash commands to sync
- Check bot has proper permissions
- Look at bot logs for errors

**"goose command not found":**
- Install Goose: https://github.com/block/goose
- Or set GOOSE_COMMAND in .env

**Need help?**
- Check DEVELOPMENT.md for detailed info
- Look at bot logs with LOG_LEVEL=DEBUG
