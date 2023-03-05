import discord
import asyncio
from discord.ext import commands
from discord.voice_client import VoiceClient
import config

intents = discord.Intents.default()
intents.members = True
intents.guild_messages = True
intents.voice_states = True

client = commands.Bot(command_prefix='!', intents=intents)

connected_voice_channels = {}  # keep track of connected voice channels

@client.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        channel = after.channel

        # check if the bot is already connected to the voice channel
        if channel.guild.id in connected_voice_channels:
            voice = connected_voice_channels[channel.guild.id]
            if voice.channel == channel:
                return  # already connected to the same channel

            await voice.move_to(channel)
        else:
            try:
                vc = await channel.connect()
                connected_voice_channels[channel.guild.id] = vc
                vc.play(discord.FFmpegPCMAudio('file.mp3')) #change file.mp3 with your file.mp3
                while vc.is_playing():
                    await asyncio.sleep(1)
                await vc.disconnect()
                del connected_voice_channels[channel.guild.id]
            except asyncio.TimeoutError:
                print("Connection to voice channel timed out.")
            except Exception as e:
                print(f"Failed to connect to voice channel: {e}")

client.run(config.BOT_TOKEN)
