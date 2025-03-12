from discord import Embed, Color, Interaction, Object, User, ButtonStyle
from discord.ui import View, Button
import logging
import discord

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def setup(bot):
    @bot.tree.command(
        name="userinfo",
        description="📌 Get detailed information about a user.",
        guild=Object(id=493120353011236905)
    )
    async def userinfo(interaction: Interaction, user: discord.User):
        embed = Embed(
            title=f"User Info: {user.name}",
            color=0x3498DB  # Softer blue
        )

        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="👤 Username", value=f"{user} (`{user.id}`)", inline=False)
        embed.add_field(name="📆 Account Created", value=user.created_at.strftime("%B %d, %Y at %H:%M:%S"), inline=True)

        # Check if the user is a bot or not clearly
        embed.add_field(name="🤖 Bot?", value="Yes" if user.bot else "No", inline=True)

        # If member information (guild-specific) is available
        member = interaction.guild.get_member(user.id)
        if member := interaction.guild.get_member(user.id):
            embed.add_field(name="🔰 Joined Server", value=member.joined_at.strftime("%B %d, %Y at %H:%M:%S"), inline=True)
            roles = [role.mention for role in member.roles if role.name != "@everyone"]
            embed.add_field(name="🎖️ Roles", value=", ".join(roles) if roles else "None", inline=False)
            embed.color = member.top_role.color if member.roles else discord.Color.blue()

            status = str(member.status).capitalize()
            embed.add_field(name="💬 Status", value=status_mapping(status), inline=True)
        else:
            embed.add_field(name="ℹ️ Note", value="This user is not a member of this server.", inline=False)

        embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        embed.set_thumbnail(url=user.display_avatar.url)

        # Button for quick actions or feedback
        view = discord.ui.View()

        avatar_button = discord.ui.Button(
            label="🖼️ Avatar URL",
            url=user.display_avatar.url,
            style=discord.ButtonStyle.link
        )

        view.add_item(view_profile := discord.ui.Button(
            label="🔗 View Profile",
            url=f"https://discord.com/users/{user.id}",
            style=discord.ButtonStyle.link
        ))

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        logging.info(f"{interaction.user} requested user info for {user}")

def status_mapping(status):
    statuses = {
        "online": "🟢 Online",
        "offline": "⚫ Offline",
        "idle": "🌙 Idle",
        "dnd": "⛔ Do Not Disturb",
        "invisible": "⚫ Invisible"
    }
    return statuses.get(status.lower(), "❔ Unknown")
