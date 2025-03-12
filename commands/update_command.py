from discord.ext import commands
from discord import Embed, Color, Interaction, Object
import time
import logging

async def setup(bot):
    @bot.tree.command(name="update", description="Update bot commands", guild=Object(id=493120353011236905))
    @commands.has_permissions(administrator=True)
    async def update(interaction: Interaction):
        start_time = time.time()
        try:
            changes_detected, added, removed = await bot.update_commands()

            if not changes_detected:
                await interaction.response.send_message("No changes detected.")
                return

            embed = Embed(title="Command Update Summary", color=Color.green())
            if added:
                embed.add_field(name="Added Commands", value="\n".join(added), inline=False)
            if removed:
                embed.add_field(name="Removed Commands", value="\n".join(removed), inline=False)

            elapsed_time = time.time() - start_time
            embed.set_footer(text=f"Update completed in {elapsed_time:.2f} seconds.")
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            logging.error(f"Error during update: {e}")
            await interaction.response.send_message(f"Failed to update commands: {e}")
