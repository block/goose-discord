#!/usr/bin/env python3
"""
Debug script to check slash command registration
"""

import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

class DebugBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
    
    async def on_ready(self):
        print(f'🦆 Bot logged in as {self.user}')
        print(f'🦆 Bot ID: {self.user.id}')
        print(f'🦆 Connected to {len(self.guilds)} guild(s):')
        
        for guild in self.guilds:
            print(f'   - {guild.name} (ID: {guild.id})')
        
        print(f'🦆 Bot has these permissions in guilds:')
        for guild in self.guilds:
            member = guild.get_member(self.user.id)
            if member:
                perms = member.guild_permissions
                print(f'   {guild.name}:')
                print(f'     - Use Slash Commands: {perms.use_slash_commands}')
                print(f'     - Send Messages: {perms.send_messages}')
                print(f'     - Create Public Threads: {perms.create_public_threads}')
        
        print('🦆 Attempting to sync slash commands...')
        try:
            # Try syncing to all guilds
            synced = await self.tree.sync()
            print(f'✅ Successfully synced {len(synced)} global command(s)')
            
            # Also try guild-specific sync for faster testing
            for guild in self.guilds:
                try:
                    guild_synced = await self.tree.sync(guild=guild)
                    print(f'✅ Synced {len(guild_synced)} command(s) to {guild.name}')
                except Exception as e:
                    print(f'❌ Failed to sync to {guild.name}: {e}')
                    
        except Exception as e:
            print(f'❌ Failed to sync commands: {e}')
        
        print('🦆 Current registered commands:')
        for command in self.tree.get_commands():
            print(f'   - /{command.name}: {command.description}')

# Create the slash command
@discord.app_commands.command(name="honk", description="🦆 Start a new Goose AI session")
@discord.app_commands.describe(prompt="The initial prompt for Goose")
async def debug_honk(interaction: discord.Interaction, prompt: str):
    """Debug version of honk command"""
    await interaction.response.send_message(
        f"🦆 **Debug Honk!** Got prompt: {prompt}\n"
        f"Guild: {interaction.guild.name if interaction.guild else 'DM'}\n"
        f"Channel: {interaction.channel.name if hasattr(interaction.channel, 'name') else 'Unknown'}\n"
        f"User: {interaction.user.display_name}",
        ephemeral=True
    )

async def main():
    bot = DebugBot()
    bot.tree.add_command(debug_honk)
    
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ DISCORD_TOKEN not found in environment!")
        return
    
    print("🦆 Starting debug bot...")
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
