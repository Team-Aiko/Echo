import discord
from discord.ext import commands
import logging
import os
from dotenv import load_dotenv
import importlib
from core.bot_info import BotInfo  # Import the centralized bot info module

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Intents for the bot
intents = discord.Intents.default()
intents.message_content = True

# Guild ID for command registration (Replace with your server's guild ID)
GUILD_ID = 493120353011236905


class MyBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.command_modules = [
            "commands.userinfo_command",
            "commands.youtube_command",
            "commands.update_command",
            "commands.donate_command",
            "commands.update_latest_command",
            "commands.buy_premium_command",
        ]
        self.sync_guild = discord.Object(id=GUILD_ID)  # Create a reusable guild object for syncing

    async def setup_hook(self):
        """
        Setup the bot, including clearing phantom commands, loading new commands, syncing, and logging status.
        """
        logging.info("Starting bot setup...")

        # Log bot version and service status
        logging.info(f"Bot Version: {BotInfo.VERSION}")
        logging.info(f"Service Status: {BotInfo.get_status()}")

        # Clear all existing commands (global and guild-specific) to prevent phantom commands
        await self.clear_all_commands()

        # Load commands dynamically
        await self.load_commands()

        # Sync commands for the specific guild
        await self.sync_commands()

        # Log currently registered commands for debugging
        await self.fetch_and_log_commands()

    async def clear_all_commands(self):
        """
        Clears all global and guild-specific commands to ensure no phantom commands remain.
        """
        try:
            logging.info("Clearing all commands...")

            # Clear guild-specific commands
            guild_commands = await self.tree.fetch_commands(guild=self.sync_guild)
            if guild_commands:
                logging.info(f"Found {len(guild_commands)} guild-specific commands to delete.")
                for command in guild_commands:
                    await self.tree.remove_command(command.id, guild=self.sync_guild)
                logging.info("Guild-specific commands cleared successfully.")

            # Clear global commands (if any exist)
            global_commands = await self.tree.fetch_commands()
            if global_commands:
                logging.info(f"Found {len(global_commands)} global commands to delete.")
                for command in global_commands:
                    await self.tree.remove_command(command.id)
                logging.info("Global commands cleared successfully.")

        except Exception as e:
            logging.error(f"Error clearing commands: {e}")

    async def load_commands(self):
        """
        Load all commands dynamically from the commands folder.
        Modules are imported and their setup functions are called.
        """
        logging.info("Loading commands from modules...")
        for module_name in self.command_modules:
            try:
                # Dynamically import the module
                module = importlib.import_module(module_name)

                # Call the module's `setup` function and pass the bot instance
                await module.setup(self)
                logging.info(f"Successfully loaded {module_name}")
            except ModuleNotFoundError:
                logging.warning(f"Module {module_name} not found. Skipping...")
            except AttributeError:
                logging.warning(f"Module {module_name} is missing a `setup` function. Skipping...")
            except Exception as e:
                logging.error(f"Error loading {module_name}: {e}")

    async def sync_commands(self):
        """
        Sync commands to Discord for the specific guild to reduce startup time.
        """
        try:
            logging.info("Syncing commands with Discord...")
            synced_commands = await self.tree.sync(guild=self.sync_guild)
            logging.info(f"Commands synced successfully. Total commands: {len(synced_commands)}")
        except Exception as e:
            logging.error(f"Error syncing commands: {e}")

    async def fetch_and_log_commands(self):
        """
        Log all currently registered commands for debugging.
        """
        try:
            commands = await self.tree.fetch_commands(guild=self.sync_guild)
            command_names = [cmd.name for cmd in commands]
            logging.info(f"Registered commands: {', '.join(command_names)}")
        except Exception as e:
            logging.error(f"Error fetching registered commands: {e}")


# Retrieve the bot token from the environment variables
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

if __name__ == "__main__":
    if TOKEN:
        # Create an instance of the bot with fewer intents for better performance
        bot = MyBot(command_prefix="!", intents=intents)

        # Run the bot
        try:
            logging.info("Starting the bot...")
            logging.info(f"Bot Version: {BotInfo.VERSION}")  # Log version at startup
            logging.info(f"Service Status: {BotInfo.get_status()}")  # Log service status at startup
            bot.run(TOKEN)
        except Exception as e:
            logging.error(f"Error while running the bot: {e}")
    else:
        logging.error("Bot token not found! Please set DISCORD_BOT_TOKEN in your .env file.")
