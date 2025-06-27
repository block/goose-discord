import os
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv
from .goose_client import GooseClient
from .thread_manager import ThreadManager

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentHonk(commands.Bot):
    """Discord bot that wraps Goose AI functionality"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        
        self.goose_client = GooseClient()
        self.thread_manager = ThreadManager()
    
    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'{self.user} has landed! 🦆')
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")

    async def on_message(self, message):
        """Handle incoming messages"""
        # Ignore bot messages
        if message.author == self.user:
            return
        
        # Handle thread messages
        if isinstance(message.channel, discord.Thread):
            thread_id = str(message.channel.id)
            if self.thread_manager.is_goose_thread(thread_id):
                await self.handle_thread_message(message)
        
        await self.process_commands(message)
    
    async def handle_thread_message(self, message):
        """Handle messages in existing Goose threads"""
        thread_id = str(message.channel.id)
        logger.info(f"Handling message in thread {thread_id}")
        
        try:
            # Get full thread history
            thread_history = await self.get_thread_history(message.channel)
            
            # Send to Goose
            async with message.channel.typing():
                response = await self.goose_client.run_with_history(
                    thread_id, 
                    thread_history
                )
                
                if response:
                    await message.channel.send(response)
                else:
                    await message.channel.send("🦆 *Honk!* Sorry, I couldn't process that right now.")
                    
        except Exception as e:
            logger.error(f"Error handling thread message: {e}")
            await message.channel.send("🦆 *Confused honking* - Something went wrong!")
    
    async def get_thread_history(self, thread):
        """Get the full message history of a thread"""
        messages = []
        try:
            async for msg in thread.history(limit=None, oldest_first=True):
                # Skip system messages and only include user/assistant messages
                if not msg.content.strip():
                    continue
                    
                if msg.author == self.user:
                    # Bot message (assistant)
                    messages.append({
                        "role": "assistant",
                        "content": msg.content
                    })
                elif not msg.author.bot:
                    # Human message (user)
                    messages.append({
                        "role": "user", 
                        "content": msg.content
                    })
        except Exception as e:
            logger.error(f"Error getting thread history: {e}")
            
        return messages


# Slash command for /honk
@discord.app_commands.command(name="honk", description="🦆 Start a new Goose AI session")
@discord.app_commands.describe(prompt="The initial prompt for Goose")
async def honk(interaction: discord.Interaction, prompt: str):
    """Create a new Goose thread with the given prompt"""
    logger.info(f"User {interaction.user} started new session with prompt: {prompt[:50]}...")
    
    try:
        # Create a new thread
        thread = await interaction.channel.create_thread(
            name=f"🦆 Goose Session - {interaction.user.display_name}",
            type=discord.ChannelType.public_thread
        )
        
        # Register the thread
        bot = interaction.client
        thread_id = str(thread.id)
        bot.thread_manager.register_thread(thread_id, interaction.user.id)
        
        # Send initial response
        await interaction.response.send_message(
            f"🦆 **Honk!** Created a new Goose session in {thread.mention}", 
            ephemeral=True
        )
        
        # Send initial prompt to Goose
        async with thread.typing():
            response = await bot.goose_client.run_initial(thread_id, prompt)
            
            if response:
                await thread.send(f"**Initial Prompt:** {prompt}\n\n{response}")
            else:
                await thread.send("🦆 *Sad honking* - I couldn't connect to Goose right now. Please try again!")
                
    except Exception as e:
        logger.error(f"Error in honk command: {e}")
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "🦆 *Error honking* - Something went wrong creating the session!", 
                ephemeral=True
            )


async def main():
    """Main entry point for the bot"""
    bot = AgentHonk()
    bot.tree.add_command(honk)
    
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN environment variable is required")
        raise ValueError("DISCORD_TOKEN environment variable is required")
    
    logger.info("Starting Agent Honk...")
    await bot.start(token)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
