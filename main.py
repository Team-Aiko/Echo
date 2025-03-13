import discord
from discord.ext import commands
import logging
import os
import importlib
import asyncio
from dotenv import load_dotenv

# Core Security Features
from core.anti_nuke import AntiNuke          # 🛡 Nuke Protection
from core.anti_spam import AntiSpamRaid      # 🛡 Spam & Raid Protection
from core.anti_predator import AntiPredator  # 🛡 Predator Protection
from core.bot_info import BotInfo            # 🔹 Bot Information Tracker

# 1. Load Environment Variables (ensure this happens early)
load_dotenv()

# 2. Set Up Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# 3. Discord Intents Setup (Enable reading messages, members, moderation, etc.)
intents = discord.Intents.default()
intents.message_content = True  # Required to read messages
intents.guilds = True
intents.members = True
intents.moderation = True  # Remove/comment out if your library doesn't support `moderation`

# 4. Bot Configuration
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
logging.info(f"DEBUG: Token from .env is: {TOKEN!r}")

GUILD_ID = os.getenv("DISCORD_GUILD_ID")
SYNC_GUILD = None
if GUILD_ID:
    try:
        guild_id_int = int(GUILD_ID)
        SYNC_GUILD = discord.Object(id=guild_id_int)
    except ValueError:
        logging.error("❌ DISCORD_GUILD_ID is not a valid integer!")

# Channel ID for test message
TEST_CHANNEL_ID = 1349704119849320482  # Replace with your desired channel ID

class MyBot(commands.Bot):
    """
    Custom Bot class that:
      - Lists all guilds
      - Checks if a target GUILD_ID is found
      - Loads security features (async)
      - Dynamically imports command modules
      - Syncs slash commands
      - Tests message readability
    """

    def __init__(self, command_modules, **kwargs):
        super().__init__(**kwargs)
        self.command_modules = command_modules
        
        # Placeholders for Security Features
        self.anti_nuke = None
        self.anti_spam = None
        self.anti_predator = None

    async def setup_hook(self):
        """Called automatically by discord.py before the bot is ready."""
        # 1. Log basic info
        self.log_startup_info()

        # 2. List all guilds (might be partial if the bot is large or the server is large)
        logging.info("🔎 [setup_hook] Checking partial guild info:")
        self.list_all_guilds()

        # 3. Load security features (awaitable now)
        await self.load_security_features()

        # 4. Dynamically load all command modules
        await self.load_command_modules()

        # We'll do slash-command sync in on_ready() to ensure the bot sees all guild data.

    def log_startup_info(self):
        logging.info(f"🔹 Bot Version: {BotInfo.VERSION}")
        logging.info(f"🔹 Service Status: {BotInfo.get_status()}")

        logging.info("🔍 Checking Intents:")
        logging.info(f"✔️ Intents.guilds: {self.intents.guilds}")
        logging.info(f"✔️ Intents.members: {self.intents.members}")
        logging.info(f"✔️ Intents.message_content: {self.intents.message_content}")
        logging.info(f"✔️ Intents.moderation: {self.intents.moderation}")

    def list_all_guilds(self):
        if not self.guilds:
            logging.info("🔎 The bot is not in any guilds yet.")
            return
        for g in self.guilds:
            logging.info(f" - {g.name} (ID: {g.id})")

    def get_target_guild(self) -> discord.Guild | None:
        """Returns the Guild matching GUILD_ID, or None if not found."""
        if not SYNC_GUILD:
            return None
        return self.get_guild(SYNC_GUILD.id)

    async def test_message_readability(self, guild: discord.Guild, channel_id: int):
        """Sends a test message to a channel by ID and verifies the bot can read it."""
        test_channel = guild.get_channel(channel_id)
        if not test_channel:
            logging.warning(f"⚠️ Could not find channel with ID {channel_id} in '{guild.name}'.")
            return

        try:
            logging.info(f"📢 Sending test message to <#{channel_id}>...")
            msg = await test_channel.send("🔍 **Testing message readability** (This will NOT be deleted)")
            await asyncio.sleep(2)

            # Check the last few messages
            async for recent_msg in test_channel.history(limit=5):
                if recent_msg.id == msg.id:
                    logging.info("✅ Bot successfully read its own test message!")
                    # Commented out the delete so you can see the message remain
                    # await msg.delete()
                    return

            logging.error("❌ Bot could not detect its own message! Check perms or intents.")
        except discord.Forbidden:
            logging.error(f"❌ Bot lacks permission to send messages in channel ID {channel_id}!")
        except Exception as e:
            logging.error(f"⚠️ Unexpected error while testing message readability: {e}")

    async def load_security_features(self):
        """Instantiate each security feature Cog as an async function."""
        # 1. Anti-Nuke
        try:
            self.anti_nuke = AntiNuke(self)
            logging.info("✅ Anti-Nuke Protection Loaded Successfully.")
        except Exception as e:
            logging.error(f"❌ Failed to load Anti-Nuke: {e}")

        # 2. Anti-Spam
        try:
            self.anti_spam = AntiSpamRaid(self)
            logging.info("✅ Anti-Spam & Raid Protection Loaded Successfully.")
        except Exception as e:
            logging.error(f"❌ Failed to load Anti-Spam/Raid: {e}")

        # 3. Anti-Predator
        try:
            self.anti_predator = AntiPredator(self)
            # Now that add_cog is async in discord.py 2.x, we must await it:
            await self.add_cog(self.anti_predator)
            logging.info("✅ Anti-Predator Protection Loaded Successfully.")
        except Exception as e:
            logging.error(f"❌ Failed to load Anti-Predator: {e}")

    async def load_command_modules(self):
        """Dynamically imports and loads each command module specified."""
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

    async def sync_commands(self, guild: discord.Guild, force: bool = False):
        """Sync slash (application) commands with the Discord API, for a single guild."""
        try:
            logging.info(f"🔄 Syncing guild commands for: {guild.name} (ID: {guild.id})")
            synced = await self.tree.sync(guild=guild)
            logging.info(f"✅ Synced {len(synced)} commands successfully to '{guild.name}'.")

            if force:
                logging.info("🔄 **Forced sync** to ensure commands are up to date.")
        except Exception as e:
            logging.error(f"❌ Error syncing commands: {e}")

    async def on_ready(self):
        """Triggered when the bot has successfully connected and is ready."""
        logging.info(f"🚀 {self.user} is online and ready!")
        logging.info("🔐 **Security Features Status:**")
        logging.info(f"🛡 Anti-Nuke: {'✅ Active' if self.anti_nuke else '❌ Failed'}")
        logging.info(f"🛡 Anti-Spam/Raid: {'✅ Active' if self.anti_spam else '❌ Failed'}")
        logging.info(f"🛡 Anti-Predator: {'✅ Active' if self.anti_predator else '❌ Failed'}")

        # Once the bot is truly ready, let's do final slash command sync
        target_guild = self.get_target_guild()
        if target_guild:
            await self.sync_commands(target_guild, force=True)
            # Test message readability
            await self.test_message_readability(target_guild, TEST_CHANNEL_ID)
        else:
            logging.warning("⚠️ No valid GUILD_ID or the bot isn't in that server.")

async def main():
    """The asynchronous entry point for the bot."""
    if not TOKEN:
        logging.error("❌ DISCORD_BOT_TOKEN not found! Please set it in your .env file.")
        return

    command_modules = [
        "commands.userinfo_command",
        "commands.youtube_command",
        "commands.donate_command",
        "commands.update_latest_command",
        "commands.buy_premium_command",
        "commands.play_command",
    ]

    # Instantiate our custom bot
    bot = MyBot(
        command_modules=command_modules,
        command_prefix="!",
        intents=intents,
        activity=discord.Game(name=f"Echo Bot v{BotInfo.VERSION}"),
        status=discord.Status.online
    )

    try:
        logging.info("🟢 Bot is starting...")
        await bot.start(TOKEN)
    except KeyboardInterrupt:
        logging.info("🛑 Shutting down bot gracefully...")
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
