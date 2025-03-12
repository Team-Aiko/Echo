import os
import requests
from discord import Embed, Interaction, ui, Object, ButtonStyle
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")  # Load the API key from the .env file

async def setup(bot):
    @bot.tree.command(
        name="youtube",
        description="Fetch details about a YouTube video link",
        guild=Object(id=493120353011236905)  # Replace with your Guild ID
    )
    async def youtube(interaction: Interaction, link: str):
        video_id = link.split("v=")[-1].split("&")[0]
        url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={video_id}&key={YOUTUBE_API_KEY}"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "items" in data and len(data["items"]) > 0:
                video = data["items"][0]
                snippet = video["snippet"]
                stats = video["statistics"]

                description = snippet.get("description", "No description available.")
                formatted_description = description if len(description) <= 2048 else description[:2045] + "..."

                embed = Embed(
                    title=snippet["title"],
                    description=formatted_description,
                    url=link,
                    color=0xFF0000
                )
                embed.set_thumbnail(url=snippet["thumbnails"]["high"]["url"])
                embed.set_author(name=snippet["channelTitle"], url=f"https://www.youtube.com/channel/{snippet['channelId']}")
                embed.add_field(name="Views", value=f"{int(stats['viewCount']):,}", inline=True)
                embed.add_field(name="Likes", value=f"{int(stats.get('likeCount', '0')):,}", inline=True)
                embed.add_field(name="Comments", value=f"{int(stats.get('commentCount', '0')):,}", inline=True)
                embed.set_footer(text=f"Published on {snippet['publishedAt'][:10]}")

                view = ui.View()
                view.add_item(ui.Button(
                    label="Watch Video",
                    url=link,
                    style=ButtonStyle.link
                ))

                await interaction.response.send_message(embed=embed, view=view)
            else:
                await interaction.response.send_message("Video not found or unavailable.")
        else:
            await interaction.response.send_message("Failed to fetch video details. Please try again later.")
