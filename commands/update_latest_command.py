from discord import Embed, Color, Interaction, Object, ButtonStyle
from discord.ui import View, Button
from version_tracker import VERSION_TRACKER
import logging
import discord

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def setup(bot):
    @bot.tree.command(
        name="update_latest",
        description="Check out the latest Echo Bot update details.",
        guild=Object(id=493120353011236905)
    )
    async def update_latest(interaction: Interaction):
        try:
            version = VERSION_TRACKER["version"]
            changelog = VERSION_TRACKER["changelog"]

            embed = Embed(
                title=f"Echo Bot v{version} - What's New?",
                description="Here's a quick summary of the latest improvements:",
                color=Color.green()
            )

            embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
            embed.set_footer(text="Thank you for using Echo Bot!", icon_url=interaction.client.user.display_avatar.url)

            # Clean, subtle emojis for readability
            formatted_changelog = "\n".join([f"• {item}" for item in changelog])

            embed.add_field(
                name="Changelog:",
                value=formatted_changelog,
                inline=False
            )

            # Interactive Buttons (small emojis, clear labels)
            view = discord.ui.View()

            documentation_button = Button(
                label="Full Documentation",
                url="https://yourbotdocumentation.com",
                style=discord.ButtonStyle.link
            )

            feedback_button = Button(
                label="Feedback",
                emoji="📝",
                style=ButtonStyle.secondary
            )

            async def feedback_callback(inter: Interaction):
                await inter.response.send_message(
                    "Your feedback matters! [Feedback Form](https://forms.gle/yourformlink)",
                    ephemeral=True
                )

            feedback_button.callback = feedback_callback

            view.add_item(feedback_button)
            view.add_item(donate_button := discord.ui.Button(
                label="Support Us",
                emoji="❤️",
                url="https://www.paypal.com/donate/?hosted_button_id=2G82JW353011236905",
                style=ButtonStyle.link
            ))

            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(
                "Something went wrong fetching update details.",
                ephemeral=True
            )
