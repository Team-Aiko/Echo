import discord
from discord import Interaction, Object, FFmpegPCMAudio
from discord.ext import commands
import yt_dlp as youtube_dl

# FFmpeg Options
FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -analyzeduration 0 -probesize 32M",
    "options": "-vn -ac 2 -b:a 192k -ar 48000"
}


async def setup(bot):
    @bot.tree.command(
        name="play",
        description="🎵 Play a YouTube video’s audio in your current voice channel.",
        guild=Object(id=493120353011236905)
    )
    async def play(interaction: Interaction, link: str):
        """Joins the user's voice channel and plays YouTube audio."""

        # ✅ Defer the interaction to prevent timeouts
        await interaction.response.defer()

        # Ensure the user is in a voice channel
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.followup.send("❌ You need to be in a voice channel first!", ephemeral=True)
            return

        voice_channel = interaction.user.voice.channel

        # Connect bot to the voice channel
        if interaction.guild.voice_client is None:
            vc = await voice_channel.connect()
        else:
            vc = interaction.guild.voice_client

        # Download audio source
        ydl_opts = {
            "format": "bestaudio[ext=webm]/bestaudio/best",
            "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True,
    }

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=False)
                url = info["url"]

            # ✅ Ensure FFmpeg is working before trying to play
            try:
                vc.play(FFmpegPCMAudio(url, **FFMPEG_OPTIONS))
                await interaction.followup.send(f"🎶 Now playing: **{info['title']}**")
            except discord.errors.ClientException as e:
                await interaction.followup.send("❌ Error: FFmpeg is not installed or not found!", ephemeral=True)
                return

        except Exception as e:
            await interaction.followup.send(f"❌ Error: Could not play audio.\n```{str(e)}```", ephemeral=True)
