import discord
from discord.ext import commands
import logging
import os
import importlib
from dotenv import load_dotenv
from core.bot_info import BotInfo

# Load environment variables
load_dotenv()

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Intents Setup
intents = discord.Intents.default()
intents.message_content = True

# Constants
GUILD_ID = 493120353011236905
SYNC_GUILD = discord.Object(id=GUILD_ID)
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

class MyBot(commands.Bot):
    def __init__(self, command_modules, **kwargs):
        super().__init__(**kwargs)
        self.command_modules = command_modules

    async def setup_hook(self):
        logging.info(f"🔹 Bot Version: {BotInfo.VERSION}")
        logging.info(f"🔹 Service Status: {BotInfo.get_status()}")

        # Load all commands dynamically
        await self.load_commands()

        # Force a sync on startup (ensures all new commands are registered!)
        await self.sync_commands(force=True)

        # Log registered commands
        await self.log_registered_commands()

    async def load_commands(self):
        logging.info("📥 Loading command modules...")
        for module_name in self.command_modules:
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, 'setup'):
                    await module.setup(self)
                    logging.info(f"✅ Successfully loaded: {module_name}")
                else:
                    logging.warning(f"⚠️ `setup()` function missing in {module_name}")
            except Exception as e:
                logging.error(f"❌ Error loading {module_name}: {e}")

    async def sync_commands(self, force=False):
        try:
            logging.info("🔄 Syncing guild commands...")
            synced = await self.tree.sync(guild=SYNC_GUILD)
            logging.info(f"✅ Synced {len(synced)} commands successfully.")

            if force:
                logging.info("🔄 **Forced sync completed** to ensure all commands are up to date.")

        except Exception as e:
            logging.error(f"❌ Error syncing commands: {e}")

    async def log_registered_commands(self):
        try:
            cmds = await self.tree.fetch_commands(guild=SYNC_GUILD)
            command_list = ', '.join(cmd.name for cmd in cmds) if cmds else "No commands found."
            logging.info(f"📜 Registered commands: {command_list}")
        except Exception as e:
            logging.error(f"❌ Error fetching registered commands: {e}")

    async def on_ready(self):
        logging.info(f"🚀 {self.user.name} is online and ready!")

# Start the bot
if __name__ == "__main__":
    if not TOKEN:
        logging.error("❌ DISCORD_BOT_TOKEN not found! Please set it in the .env file.")
        exit(1)

    # Command Modules (Make sure all files are listed)
    command_modules = [
        "commands.userinfo_command",
        "commands.youtube_command",
        "commands.donate_command",
        "commands.update_latest_command",
        "commands.buy_premium_command",
        "commands.play_command",
    ]

    bot = MyBot(
        command_modules=command_modules,
        command_prefix="!",
        intents=intents,
        activity=discord.Game(name="Echo Bot v1.3.7"),
        status=discord.Status.online
    )

    try:
        logging.info("🟢 Bot is starting...")
        bot.run(TOKEN)
    except Exception as e:
        logging.error(f"❌ Fatal error while starting bot: {e}")
