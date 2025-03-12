import os
import requests
import logging
from discord import Embed, Interaction, Object, ButtonStyle
from discord.ui import View, Button
from dotenv import load_dotenv

# Load environment variables and setup logging
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

async def setup(bot):
    @bot.tree.command(
        name="youtube",
        description="🎬 Fetch detailed information about a YouTube video.",
        guild=Object(id=493120353011236905)
    )
    async def youtube(interaction: Interaction, link: str):
        video_id = link.split("v=")[-1].split("&")[0]
        api_url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&part=snippet,statistics&key={YOUTUBE_API_KEY}"

        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()

            if data["items"]:  # Ensure there is data
                video_data = data["items"][0]  # Correct reference
                snippet = video_data["snippet"]  # Fix: Access the correct variable
                stats = video_data.get("statistics", {})

                description = snippet.get("description", "No description provided.")
                if len(description) > 500:
                    description = description[:497] + "..."

                embed = Embed(
                    title=snippet["title"],
                    description=description,
                    url=f"https://youtu.be/{video_id}",
                    color=0xFF0000
                )

                embed.set_thumbnail(url=snippet["thumbnails"]["high"]["url"])
                embed.add_field(name="👀 Views", value=f"{int(stats.get('viewCount', 0)):,}", inline=True)
                embed.add_field(name="👍 Likes", value=f"{int(stats.get('likeCount', 0)):,}", inline=True)
                embed.add_field(name="💬 Comments", value=f"{int(stats.get('commentCount', 0)):,}", inline=True)
                embed.add_field(name="📅 Published On", value=snippet["publishedAt"][:10], inline=True)
                embed.add_field(name="🎬 Channel", value=f"[{snippet['channelTitle']}](https://www.youtube.com/channel/{snippet['channelId']})", inline=True)

                embed.set_footer(text="Powered by YouTube API", icon_url="https://i.imgur.com/7sc0GYe.png")

                # Button linking directly to the YouTube video
                view = View()
                view.add_item(Button(label="Watch on YouTube", url=f"https://youtu.be/{video_id}", style=ButtonStyle.link))

                await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
                logging.info(f"{interaction.user} requested YouTube info: {video_id}")

            else:
                await interaction.response.send_message("⚠️ Video not found or unavailable.", ephemeral=True)

        except requests.exceptions.RequestException as e:
            logging.error(f"API Request Error: {e}")
            await interaction.response.send_message("🚫 Unable to retrieve video details. Please check your link and try again.", ephemeral=True)
