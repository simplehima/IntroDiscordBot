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
        # Someone joined the voice channel
        channel = after.channel

        # Check if the bot is already connected to a voice channel in this guild
        if channel.guild.id in connected_voice_channels:
            voice = connected_voice_channels[channel.guild.id]
            if voice.is_connected():  # Check if the bot is already connected
                if voice.channel == channel:
                    return  # Already connected to the same channel
                else:
                    await voice.move_to(channel)  # Move to the new channel
                    return

        # Bot is not connected to a voice channel in this guild, connect to the new one
        try:
            vc = await channel.connect()
            connected_voice_channels[channel.guild.id] = vc
            vc.play(discord.FFmpegPCMAudio('file1.mp3'))
            while vc.is_playing():
                await asyncio.sleep(1)
        except asyncio.TimeoutError:
            print("Connection to voice channel timed out.")
        except Exception as e:
            print(f"Failed to connect to voice channel: {e}")
    elif before.channel is not None and after.channel is None:
        # Someone left the voice channel
        voice = connected_voice_channels.get(before.channel.guild.id)
        if voice and voice.is_connected():
            voice.play(discord.FFmpegPCMAudio('file2.mp3'))
            while voice.is_playing():
                await asyncio.sleep(1)
            await voice.disconnect()
            del connected_voice_channels[before.channel.guild.id]

client.run(config.BOT_TOKEN)
