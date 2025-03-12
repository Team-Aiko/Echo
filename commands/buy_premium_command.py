import discord
from discord import Embed, Interaction, Object
from discord.ui import View, Select, Button
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Example: Dynamically update this variable based on your actual service state
service_online = True

async def setup(bot):
    @bot.tree.command(
        name="buy_premium",
        description="💎 Unlock exclusive premium features!",
        guild=Object(id=493120353011236905)
    )
    async def buy_premium(interaction: Interaction):
        logging.info(f"User {interaction.user} used /buy_premium at {interaction.created_at}")

        # Embed with enhanced visuals
        embed = Embed(
            title="✨ Premium Membership ✨",
            description=(
                "Take your experience to the **next level!**\n"
                f"**Current Status:** {'🟢 Online - Ready to purchase!' if service_online else '🔴 Offline - Currently unavailable.'}"
            ),
            color=0x5865F2 if service_online else 0xFF0000
        )

        embed.set_thumbnail(url=interaction.client.user.display_avatar.url)

        # Highlight features with emojis for better readability
        premium_features = (
            "✅ Full access to **YouTube API commands**\n"
            "⚙️ Advanced **custom commands**\n"
            "🚑 Priority **support and bug fixes**\n"
            "🆕 Early **beta access to updates**\n"
            "🏅 Exclusive **premium-only roles**"
        )

        embed.add_field(name="🌟 Premium Benefits:", value=premium_features, inline=False)

        embed.set_image(url="https://i.imgur.com/4M7IWwP.png")  # Replace with a custom promotional banner
        embed.set_footer(text="Thanks for supporting Echo Bot!", icon_url=interaction.client.user.display_avatar.url)

        # Interactive Buttons & Dropdown
        view = View()

        if service_online:
            # Active purchase button
            buy_button = Button(
                label="🚀 Buy Premium Now",
                url="https://www.example.com",  # Your real purchase URL here
                style=discord.ButtonStyle.link
            )
            view.add_item(buy_button)

            # Informational "Learn More" button
            learn_more_button = Button(
                label="📚 Learn More",
                style=discord.ButtonStyle.secondary
            )

            async def learn_more_callback(inter: Interaction):
                more_info_embed = Embed(
                    title="📚 More about Premium Plans",
                    description=(
                        "**Basic:** Access core premium features.\n"
                        "**Pro:** Unlock advanced commands and perks.\n"
                        "**Ultimate:** Full access, early beta features, and exclusive roles."
                    ),
                    color=0x2ECC71
                )
                more_info_embed.set_footer(text="Choose the plan that suits you best!")
                await inter.response.send_message(embed=more_info_embed, ephemeral=True)

            learn_more_button.callback = learn_more_callback
            view.add_item(learn_more_button)

            # Dropdown for premium plan selection
            class PremiumPlanSelect(Select):
                def __init__(self):
                    super().__init__(
                        placeholder="✨ Select a Premium Plan",
                        options=[
                            discord.SelectOption(
                                label="Basic",
                                description="Core premium features",
                                emoji="🔹"
                            ),
                            discord.SelectOption(
                                label="Pro",
                                description="Advanced premium features",
                                emoji="🔸"
                            ),
                            discord.SelectOption(
                                label="Ultimate",
                                description="All features and perks included",
                                emoji="💠"
                            )
                        ]
                    )

                async def callback(self, inter: Interaction):
                    selected_plan = self.values[0]
                    await inter.response.send_message(
                        f"🎉 You've selected the **{selected_plan}** plan! Visit our [purchase page](https://www.example.com) to proceed.", 
                        ephemeral=True
                    )

            view.add_item(PremiumPlanSelect())

        else:
            # Disabled button when offline
            offline_button = Button(
                label="🔴 Premium Offline",
                style=discord.ButtonStyle.secondary,
                disabled=True
            )
            view.add_item(offline_button)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
