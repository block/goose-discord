# Slash Command Troubleshooting Guide 🦆

## Why `/honk` isn't showing up?

### 1. **Most Common Issue: Bot Permissions**

Your bot needs the `applications.commands` scope when invited. If you didn't include this initially:

**Fix: Re-invite the bot with correct permissions**

1. Go to Discord Developer Portal → Your Application → OAuth2 → URL Generator
2. Select Scopes:
   - ✅ `bot`
   - ✅ `applications.commands` ← **This is crucial!**
3. Select Bot Permissions:
   - ✅ Send Messages
   - ✅ Create Public Threads  
   - ✅ Use Slash Commands
   - ✅ Read Message History
4. Use the new invite URL (even if bot is already in server)

### 2. **Command Sync Delay**

Slash commands can take up to **1 hour** to appear globally. For faster testing:

**Quick Fix: Run the debug bot**
```bash
cd discord-goose
uv run python debug_bot.py
```

This will:
- Show bot permissions
- Force sync commands to your specific server
- Show detailed error messages

### 3. **Check Bot Status**

**Run this to see what's happening:**
```bash
cd discord-goose
LOG_LEVEL=DEBUG uv run python run_bot.py
```

Look for these log messages:
- ✅ `Synced X command(s)` - Commands registered successfully
- ❌ `Failed to sync commands: ...` - Permission or other error

### 4. **Discord Client Issues**

Sometimes Discord doesn't refresh slash commands:
- **Restart Discord completely** (not just refresh)
- **Try Discord web version** at discord.com
- **Check in different channels** (some channels might have restrictions)

### 5. **Server-Specific Issues**

**Administrator Override:**
- Server admins can disable slash commands for specific bots
- Check Server Settings → Integrations → Agent Honk
- Make sure slash commands are enabled

**Channel Permissions:**
- Bot needs "Use Application Commands" permission in the channel
- Check channel-specific permission overrides

### 6. **Force Refresh Commands**

If commands still don't appear, try this debug sequence:

```bash
# 1. Run debug bot to force sync
uv run python debug_bot.py

# 2. Check the output for errors

# 3. If successful, restart main bot
uv run python run_bot.py
```

## Quick Diagnostic Checklist

Run through this list:

- [ ] Bot invited with `applications.commands` scope?
- [ ] Bot has "Use Application Commands" permission?
- [ ] Waited at least 5 minutes after bot startup?
- [ ] Tried restarting Discord client?
- [ ] Checked bot logs for sync errors?
- [ ] Tested in different channels?
- [ ] Server admin hasn't disabled bot slash commands?

## Still Not Working?

**Try the debug bot:**
```bash
uv run python debug_bot.py
```

**Check the logs and look for:**
1. Permission errors
2. Sync failures  
3. Missing scopes

**Common Error Messages:**
- `Missing Access` → Bot needs `applications.commands` scope
- `Missing Permissions` → Bot needs "Use Application Commands" permission
- `Command already exists` → Normal, just means it's registered

## Manual Command Registration

If automatic sync fails, you can try manual registration:

```python
# Add this to your bot for testing
@bot.event
async def on_ready():
    # Force sync to specific guild for testing
    guild = discord.Object(id=YOUR_GUILD_ID)  # Replace with your server ID
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)
```

## Need Your Server ID?

Enable Developer Mode in Discord:
1. User Settings → Advanced → Developer Mode ✅
2. Right-click your server name → Copy Server ID

Then use it in the debug bot or manual sync code above.

---

**Most likely fix:** Re-invite bot with `applications.commands` scope! 🎯
