from discord import Embed, Color, Interaction, Object
from version_tracker import VERSION_TRACKER

async def setup(bot):
    @bot.tree.command(name="update_latest", description="Show the latest version and changelog", guild=Object(id=493120353011236905))
    async def update_latest(interaction: Interaction):
        try:
            version = VERSION_TRACKER["version"]
            changelog = VERSION_TRACKER["changelog"]

            embed = Embed(
                title="Latest Version Details",
                description=f"**Version**: {version}",
                color=Color.blue()
            )
            embed.add_field(
                name="Changelog",
                value="\n".join([f"- {change}" for change in changelog]),
                inline=False
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Failed to fetch version details: {e}")
