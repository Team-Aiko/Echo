import discord
from discord import Embed, Interaction, Object
from discord.ui import View, Select
import logging

# Set up logging to track command usage
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Replace this with a real check for your service availability
service_online = False  # Example: dynamically update based on your system's state

async def setup(bot):
    @bot.tree.command(
        name="buy_premium",
        description="💎 Learn how to purchase premium access for exclusive features!",
        guild=Object(id=493120353011236905)  # Replace with your Guild ID
    )
    async def buy_premium(interaction: Interaction):
        """
        This command provides information on buying premium and outlines its features.
        """
        # Log command usage
        logging.info(f"User {interaction.user} used /buy_premium at {interaction.created_at}")

        # Dynamic embed creation based on service status
        embed = Embed(
            title="Buy Premium 🚀",
            description=(
                "Unlock exclusive features with a premium subscription!\n\n"
                "**Status:**"
                f" {'🟢 Online - Ready to Purchase!' if service_online else '🔴 Offline - Please check back later.'}"
            ),
            color=0x1abc9c if service_online else 0x808080
        )

        # Add premium features list to the embed
        embed.add_field(
            name="💎 Premium Features Include:",
            value=(
                "- Full access to **YouTube API commands**\n"
                "- Advanced **custom bot commands**\n"
                "- Priority support for bug fixes and feature requests\n"
                "- Early access to **new updates and beta features**\n"
                "- Special **premium-only roles** and perks in the community"
            ),
            inline=False
        )

        embed.set_footer(text="Thank you for your support!")

        # Add interactive dropdown or dynamic button
        view = View()

        if service_online:
            # Button for active service
            view.add_item(discord.ui.Button(
                label="Buy Premium Now!",
                url="https://www.example.com",  # Replace with your purchase link
                style=discord.ButtonStyle.link,
                disabled=False
            ))
        else:
            # Disabled button with placeholder text
            view.add_item(discord.ui.Button(
                label="Buy Premium (Offline)",
                url="https://www.example.com",  # Placeholder for the future link
                style=discord.ButtonStyle.link,
                disabled=True
            ))

        # Dropdown menu for future plan selections
        class PremiumDropdown(Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label="Basic", description="Access core features", value="basic"),
                    discord.SelectOption(label="Pro", description="Unlock advanced features", value="pro"),
                    discord.SelectOption(label="Ultimate", description="All features included!", value="ultimate")
                ]
                super().__init__(placeholder="Choose your premium plan", options=options)

            async def callback(self, interaction: Interaction):
                await interaction.response.send_message(
                    f"You selected the {self.values[0]} plan. 🚀 Thank you for your interest!", ephemeral=True
                )

        # Add the dropdown to the view if the service is online
        if service_online:
            view.add_item(PremiumDropdown())

        # Send the embed with the interactive view
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
