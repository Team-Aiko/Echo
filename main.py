import discord
from discord.ext import commands
import logging
import os
import importlib
from dotenv import load_dotenv
from core.bot_info import BotInfo

# Load environment variables
load_dotenv()

# Logging-Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Intents definieren
intents = discord.Intents.default()
intents.message_content = True

# Konstanten
GUILD_ID = 493120353011236905
SYNC_GUILD = discord.Object(id=GUILD_ID)
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

class MyBot(commands.Bot):
    def __init__(self, command_modules, **kwargs):
        super().__init__(**kwargs)
        self.command_modules = command_modules

    async def setup_hook(self):
        logging.info(f"Bot Version: {BotInfo.VERSION}")
        logging.info(f"Service Status: {BotInfo.get_status()}")

        # Nur Commands laden, ohne sie jedes Mal zu löschen!
        await self.load_commands()

        # Sync Commands nur bei Bedarf (z.B. nur wenn du neue Befehle hinzugefügt hast)
        # Kommentiere diese Zeile aus, wenn du keine neuen Befehle hast.
        # await self.sync_commands()

        # Optionales Logging der Commands (wenn nötig)
        await self.log_registered_commands()

    async def load_commands(self):
        logging.info("Loading command modules...")
        for module_name in self.command_modules:
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, 'setup'):
                    await module.setup(self)
                    logging.info(f"Module loaded: {module_name}")
                else:
                    logging.warning(f"Setup fehlt in {module_name}")
            except Exception as e:
                logging.error(f"Fehler beim Laden von {module_name}: {e}")

    async def sync_commands(self):
        try:
            logging.info("Syncing guild commands...")
            synced = await self.tree.sync(guild=SYNC_GUILD)
            logging.info(f"Synced {len(synced)} guild commands.")
        except Exception as e:
            logging.error(f"Fehler beim Syncen: {e}")

    async def log_registered_commands(self):
        try:
            cmds = await self.tree.fetch_commands(guild=SYNC_GUILD)
            logging.info(f"Registered guild commands: {', '.join(cmd.name for cmd in cmds)}")
        except Exception as e:
            logging.error(f"Fehler beim Loggen der Commands: {e}")

    async def on_ready(self):
        logging.info(f"{self.user.name} ist eingeloggt und läuft!")

# Bot starten
if __name__ == "__main__":
    if not TOKEN:
        logging.error("DISCORD_BOT_TOKEN nicht gefunden! Bitte in .env setzen.")
        exit(1)

    # Module für Commands
    command_modules = [
        "commands.userinfo_command",
        "commands.youtube_command",
        "commands.donate_command",
        "commands.update_latest_command",
        "commands.buy_premium_command",
    ]

    bot = MyBot(
        command_modules=command_modules,
        command_prefix="!",
        intents=intents,
        activity=discord.Game(name="Echo Bot v1.3.5"),
        status=discord.Status.online
    )

    try:
        logging.info("Bot startet jetzt...")
        bot.run(TOKEN)
    except Exception as e:
        logging.error(f"Fehler beim Starten des Bots: {e}")
