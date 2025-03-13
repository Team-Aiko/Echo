# 📌 core/bot_info.py

import datetime

class BotInfo:
    """
    Centralized information about the bot, including version, service status,
    and additional metadata for monitoring and updates.
    """

    VERSION = "v1.3.9"  # 🔄 Update this for new bot releases
    RELEASE_DATE = "2025-03-14"  # 🗓 Optional: Date of the current version release
    SERVICE_ONLINE = True  # ✅ Service status (can be dynamically updated)

    @classmethod
    def toggle_service_status(cls, status: bool):
        """
        Dynamically update the service status.

        Args:
            status (bool): True for online, False for offline.
        """
        cls.SERVICE_ONLINE = status
        status_text = "🟢 Online" if status else "🔴 Offline"
        print(f"🔄 Service status updated: {status_text}")

    @classmethod
    def get_status(cls):
        """
        Retrieve the current service status as a user-friendly string.

        Returns:
            str: A string representing the current service status.
        """
        return "🟢 Online" if cls.SERVICE_ONLINE else "🔴 Offline"

    @classmethod
    def get_version_info(cls):
        """
        Retrieves detailed bot version and release information.

        Returns:
            str: Formatted version details for logging or commands.
        """
        return (
            f"🔹 **Echo Bot - Version {cls.VERSION}**\n"
            f"📅 **Release Date:** {cls.RELEASE_DATE}\n"
            f"🛠 **Service Status:** {cls.get_status()}\n"
        )

    @classmethod
    def get_uptime(cls, start_time: datetime.datetime):
        """
        Calculates and returns the bot's uptime since launch.

        Args:
            start_time (datetime.datetime): The datetime when the bot was started.

        Returns:
            str: Formatted uptime string.
        """
        uptime_duration = datetime.datetime.now() - start_time
        days, remainder = divmod(uptime_duration.total_seconds(), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, _ = divmod(remainder, 60)

        return f"⏳ **Uptime:** {int(days)}d {int(hours)}h {int(minutes)}m"

# ✅ Display bot information when run directly
if __name__ == "__main__":
    print(BotInfo.get_version_info())
