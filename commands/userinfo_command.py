from discord import Embed, Color, Interaction, Object, User  # Import `User` for type annotation

async def setup(bot):
    @bot.tree.command(name="userinfo", description="Get information about a user", guild=Object(id=493120353011236905))
    async def userinfo(interaction: Interaction, user: User):  # Add `User` type annotation here
        """Get information about a user."""
        embed = Embed(title="User Information", color=Color.blue())
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="Username", value=user.name, inline=True)
        embed.add_field(name="Discriminator", value=user.discriminator, inline=True)
        embed.add_field(name="ID", value=user.id, inline=True)
        embed.add_field(name="Bot", value=user.bot, inline=True)
        embed.add_field(name="Created At", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
        embed.add_field(name="Status", value=str(user.status).capitalize(), inline=True)

        await interaction.response.send_message(embed=embed)
