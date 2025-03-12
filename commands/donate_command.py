from discord import Embed, Interaction, ui, Object
import discord

async def setup(bot):
    @bot.tree.command(
        name="donate",
        description="Support the bot via donation",
        guild=Object(id=493120353011236905)  # Replace with your Guild ID
    )
    async def donate(interaction: Interaction):
        """Provide a link to donate to the bot."""
        embed = Embed(
            title="Support Us ❤️",
            description="If you'd like to support the development of this bot, consider donating using the button below!",
            color=0xFFD700  # Gold color
        )

        # Add a "Donate" button with the correct style
        view = ui.View()
        view.add_item(ui.Button(
            label="Donate",
            url="https://www.paypal.com/donate/?hosted_button_id=2G82JWEXMF7LY",
            style=discord.ButtonStyle.link  # Use the correct ButtonStyle attribute
        ))

        await interaction.response.send_message(embed=embed, view=view)
