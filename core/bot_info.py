# core/bot_info.py

class BotInfo:
    """
    Centralized bot information including version and security state.
    """
    VERSION = "v1.3.9"  # 🔄 Updated bot version
    __service_online = True  # 🔒 Internal flag (CANNOT be modified externally)

    @classmethod
    def toggle_service_status(cls, status: bool):
        """Prevents unauthorized service state changes."""
        raise PermissionError("🚫 Unauthorized modifications to bot status are blocked!")

    @classmethod
    def get_status(cls):
        """Returns the current bot service status as a user-friendly string."""
        return "🟢 Online" if cls.__service_online else "🔴 Offline"
