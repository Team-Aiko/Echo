import discord
from discord.ext import commands
import logging
import importlib
import asyncio
import os
from secure_storage import load_encrypted_data  # Import secure credential loader
from core.anti_nuke import AntiNuke
from core.anti_spam import AntiSpamRaid
from core.anti_predator import AntiPredator
from core.bot_info import BotInfo

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load encrypted bot credentials
bot_config = load_encrypted_data()

if not bot_config:
    logging.critical("❌ Failed to load encrypted bot credentials. Run `secure_storage.py /encrypt` first.")
    exit(1)

TOKEN = bot_config.get("DISCORD_BOT_TOKEN")
GUILD_ID = bot_config.get("DISCORD_GUILD_ID")
EXPECTED_CLIENT_ID = bot_config.get("DISCORD_CLIENT_ID")

if not TOKEN or not GUILD_ID or not EXPECTED_CLIENT_ID:
    logging.critical("❌ Missing required bot credentials.")
    exit(1)

# Convert IDs to integers
try:
    GUILD_ID = int(GUILD_ID)
    EXPECTED_CLIENT_ID = int(EXPECTED_CLIENT_ID)
    logging.info(f"🔢 Converted GUILD_ID: {GUILD_ID}, CLIENT_ID: {EXPECTED_CLIENT_ID}")
except ValueError:
    logging.critical(f"❌ Invalid ID format in encrypted credentials. Ensure they are integers.")
    exit(1)

SYNC_GUILD = discord.Object(id=GUILD_ID)
TEST_CHANNEL_ID = 1349704119849320482  # Channel for test messages

# Set up bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # Required to fetch members


class MyBot(commands.Bot):
    """Custom Bot class with enhanced security and optimized startup."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Security feature placeholders
        self.anti_nuke = None
        self.anti_spam = None
        self.anti_predator = None

    async def setup_hook(self):
        """Executed before bot is fully ready."""
        logging.info("✅ Step 1: Inside setup_hook()")

        # Ensure bot is in the correct guild
        target_guild = await self.ensure_correct_guild()
        if not target_guild:
            logging.error("❌ The bot is not inside the correct guild! Exiting.")
            exit(1)

        logging.info("✅ Step 2: Loading security features...")
        await self.load_security_features()

        logging.info("✅ Step 3: Loading command modules...")
        await self.load_command_modules()

        logging.info("✅ Step 4: Finished setup_hook()")

    async def load_security_features(self):
        """Instantiate and load each security feature."""
        logging.info("🔒 Initializing security features...")

        try:
            self.anti_nuke = AntiNuke(self)
            logging.info("✅ Anti-Nuke Protection Loaded Successfully.")
        except Exception as e:
            logging.error(f"❌ Failed to load Anti-Nuke: {e}")

        try:
            self.anti_spam = AntiSpamRaid(self)
            logging.info("✅ Anti-Spam & Raid Protection Loaded Successfully.")
        except Exception as e:
            logging.error(f"❌ Failed to load Anti-Spam/Raid: {e}")

        try:
            self.anti_predator = AntiPredator(self)
            await self.add_cog(self.anti_predator)
            logging.info("✅ Anti-Predator Protection Loaded Successfully.")
        except Exception as e:
            logging.error(f"❌ Failed to load Anti-Predator: {e}")

    async def load_command_modules(self):
        """Dynamically import and load command modules from the `commands` folder."""
        logging.info("📥 Loading command modules...")
        command_path = "commands"

        for filename in os.listdir(command_path):
            if filename.endswith("_command.py"):
                module_name = f"{command_path}.{filename[:-3]}"  # Remove ".py"
                try:
                    module = importlib.import_module(module_name)
                    if hasattr(module, 'setup'):
                        await module.setup(self)
                        logging.info(f"✅ Successfully loaded: {module_name}")
                    else:
                        logging.warning(f"⚠️ `setup()` function missing in {module_name}")
                except Exception as e:
                    logging.error(f"❌ Error loading {module_name}: {e}")

    async def ensure_correct_guild(self):
        """Ensures the bot is inside the correct Discord server before proceeding."""
        await asyncio.sleep(2)  # Small delay for bot to load properly

        logging.info("🔎 Checking if bot is inside the correct guild...")

        # ✅ Convert async generator to a list
        self._guilds = [guild async for guild in self.fetch_guilds(limit=100)]
        found_guilds = {guild.id: guild.name for guild in self._guilds}

        if found_guilds:
            for guild in self._guilds:
                logging.info(f"✅ Bot is in: {guild.name} (ID: {guild.id})")

            if GUILD_ID not in found_guilds:
                logging.error(f"❌ Expected Guild ID: {GUILD_ID}, but bot is only in: {list(found_guilds.keys())}")
                logging.error("💡 Make sure the bot is in the correct server or re-invite it.")
                return None
            else:
                logging.info(f"✅ Confirmed: Bot is in the correct guild '{found_guilds[GUILD_ID]}' (ID: {GUILD_ID})")
        else:
            logging.error("❌ Bot is not in any servers! Please check if it has been invited.")
            return None

        # ✅ Use fetch_guild() instead of get_guild()
        try:
            target_guild = await self.fetch_guild(GUILD_ID)
            logging.info(f"✅ Successfully fetched guild: {target_guild.name} (ID: {target_guild.id})")
        except discord.NotFound:
            logging.error(f"❌ Guild with ID {GUILD_ID} not found! The bot might have been removed.")
            return None
        except discord.Forbidden:
            logging.error(f"❌ Bot lacks permissions to fetch guild info for ID {GUILD_ID}.")
            return None

        return target_guild

    async def on_ready(self):
        """Triggered when the bot is fully ready."""
        logging.info(f"🚀 {self.user} is online and ready!")

        # Fetch and log actual Client ID
        client_id = self.user.id
        logging.info(f"🤖 Detected Bot Client ID: {client_id}")

        if client_id != EXPECTED_CLIENT_ID:
            logging.warning(f"⚠️ WARNING: Expected Client ID {EXPECTED_CLIENT_ID}, but got {client_id}.")
            logging.warning("💡 Make sure you are running the correct bot.")
        else:
            logging.info(f"✅ Bot Client ID matches expected ID ({EXPECTED_CLIENT_ID}).")

        # Ensure bot is in the correct server
        await self.ensure_correct_guild()


async def main():
    """Main entry point for the bot."""
    bot = MyBot(
        command_prefix="!",
        intents=intents,
        activity=discord.Game(name="Secure Bot"),
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
