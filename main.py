import discord
from discord.ext import commands
import logging
import importlib
import asyncio
import os
from secure_storage import decrypt_data
from core.anti_nuke import AntiNuke
from core.anti_spam import AntiSpamRaid
from core.anti_predator import AntiPredator
from core.bot_info import BotInfo

# 🔐 Secure Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def secure_mask(value, visible_digits=4):
    """
    Masks sensitive data before logging.
    """
    value = str(value)
    masked_length = len(value) - visible_digits
    return "*" * masked_length + value[-visible_digits:] if masked_length > 0 else value

# ✅ Securely Decrypt Bot Credentials
try:
    bot_config = decrypt_data()
    logging.info("🔓 Bot credentials successfully decrypted.")
except Exception as e:
    logging.critical(f"❌ Failed to decrypt bot credentials: {e}")
    exit(1)

# ✅ Extract and Validate Bot Credentials
TOKEN = bot_config.get("DISCORD_BOT_TOKEN", "").strip()
GUILD_ID = bot_config.get("DISCORD_GUILD_ID", "").strip()
CLIENT_ID = bot_config.get("DISCORD_CLIENT_ID", "").strip()

if not TOKEN or not GUILD_ID or not CLIENT_ID:
    logging.critical("❌ Missing required bot credentials. Exiting...")
    exit(1)

# Debugging - Ensure the token is retrieved correctly
logging.info(f"DEBUG: Retrieved Token Length: {len(TOKEN)}")
logging.info(f"🔢 GUILD_ID: {secure_mask(GUILD_ID)}, CLIENT_ID: {secure_mask(CLIENT_ID)}")

# ✅ Convert IDs to Integers & Validate
try:
    GUILD_ID = int(GUILD_ID)
    CLIENT_ID = int(CLIENT_ID)
except ValueError:
    logging.critical("❌ Invalid ID format in encrypted credentials. Ensure they are integers.")
    exit(1)

# ✅ Ensure Token is Properly Formatted
if len(TOKEN) < 50:  # Discord bot tokens are usually 59+ characters
    logging.critical("🚨 Decrypted bot token is invalid! Check encryption.")
    exit(1)

# ✅ Define Secure Bot Intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

class MyBot(commands.Bot):
    """Custom Bot Class with Secure Startup"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.anti_nuke = None
        self.anti_spam = None
        self.anti_predator = None

    async def setup_hook(self):
        logging.info("✅ Step 1: Inside setup_hook()")
        target_guild = await self.ensure_correct_guild()
        if not target_guild:
            logging.critical("❌ The bot is not inside the correct guild! Exiting.")
            exit(1)

        logging.info("✅ Step 2: Loading security features...")
        await self.load_security_features()

        logging.info("✅ Step 3: Loading command modules...")
        await self.load_command_modules()

        logging.info("✅ Step 4: Finished setup_hook()")

    async def load_security_features(self):
        """Loads security protections."""
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
        """Dynamically imports and loads all command modules securely."""
        logging.info("📥 Loading command modules...")
        command_path = "commands"
        
        for filename in os.listdir(command_path):
            if filename.endswith("_command.py"):
                module_name = f"{command_path}.{filename[:-3]}"
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
        """Ensures the bot is running in the correct guild."""
        await asyncio.sleep(2)  # Delay for bot to load properly
        logging.info("🔎 Verifying bot is inside the correct guild...")
        
        try:
            target_guild = await self.fetch_guild(GUILD_ID)
            logging.info(f"✅ Successfully verified guild: {target_guild.name} (ID: {secure_mask(GUILD_ID)})")
            return target_guild
        except discord.NotFound:
            logging.critical(f"❌ Guild with ID {secure_mask(GUILD_ID)} not found! The bot may have been removed.")
        except discord.Forbidden:
            logging.critical(f"❌ Bot lacks permissions to verify the guild ID {secure_mask(GUILD_ID)}.")
        except Exception as e:
            logging.error(f"⚠️ Unexpected error while fetching guild: {e}")
        
        return None

    async def on_ready(self):
        logging.info(f"🚀 {self.user} is online and fully operational!")
        detected_client_id = self.user.id
        logging.info(f"🤖 Detected Bot Client ID: {secure_mask(detected_client_id)}")

async def main():
    """Main entry point for securely running the bot."""
    bot = MyBot(
        command_prefix="!",
        intents=intents,
        activity=discord.Game(name="Secure Bot"),
        status=discord.Status.online
    )

    try:
        logging.info("🟢 Secure bot startup initiated...")
        await bot.start(TOKEN)
    except discord.errors.LoginFailure:
        logging.critical("❌ Login failed! Check your bot token and Discord Developer Portal.")
    except KeyboardInterrupt:
        logging.info("🛑 Secure shutdown initiated...")
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())