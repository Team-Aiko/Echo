from discord import Embed, Interaction, Object, ButtonStyle
from discord.ui import View, Button

async def setup(bot):
    @bot.tree.command(
        name="donate",
        description="💖 Support Echo Bot with your generous donation!",
        guild=Object(id=493120353011236905)
    )
    async def donate(interaction: Interaction):
        embed = Embed(
            title="🌟 Support Echo Bot! 🌟",
            description=(
                "Your donation helps us continuously improve the bot, add exciting new features, "
                "and maintain excellent support!\n\n"
                "**Thank you so much for your generosity! ❤️**"
            ),
            color=0xFFD700  # Gold
        )

        embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
        embed.set_image(url="https://i.imgur.com/Yv6JpX7.png")  # Replace with your own appealing banner image
        embed.set_footer(text="Every donation matters!", icon_url=interaction.client.user.display_avatar.url)

        view = View()
        
        donate_button = Button(
            label="💖 Donate via PayPal",
            url="https://www.paypal.com/donate/?hosted_button_id=2G82JWEXMF7LY",
            style=ButtonStyle.link
        )

        community_button = Button(
            label="🎉 Join Community",
            url="https://discord.gg/yourcommunity",  # Replace with your community link
            style=ButtonStyle.link
        )

        # Add a quick-feedback button
        feedback_button = Button(
            label="✉️ Leave Feedback",
            style=ButtonStyle.secondary
        )

        async def feedback_callback(inter: Interaction):
            await inter.response.send_message(
                "We love hearing from our supporters! Share your feedback directly with the team: [Feedback Form](https://forms.gle/yourformlink)",
                ephemeral=True
            )

        feedback_button.callback = feedback_callback

        view.add_item(donate_button)
        view.add_item(community_button)
        view.add_item(feedback_button)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
