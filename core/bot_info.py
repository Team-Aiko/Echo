# core/bot_info.py

class BotInfo:
    """
    Centralized information about the bot, including version and service status.
    """
    VERSION = "v1.3.8"  # Update this for new bot versions
    service_online = True  # Dynamically update based on your system's state

    @classmethod
    def toggle_service_status(cls, status: bool):
        """
        Dynamically update the service status.

        Args:
            status (bool): True for online, False for offline.
        """
        cls.service_online = status

    @classmethod
    def get_status(cls):
        """
        Retrieve the current service status as a user-friendly string.

        Returns:
            str: A string representing the current service status.
        """
        return "🟢 Online" if cls.service_online else "🔴 Offline"
