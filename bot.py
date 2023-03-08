import discord
import asyncio
from discord.ext import commands
from discord.voice_client import VoiceClient
import config

intents = discord.Intents.all()
intents.members = True
intents.guild_messages = True
intents.voice_states = True

client = commands.Bot(command_prefix='!', intents=intents)

connected_voice_channels = {}  # keep track of connected voice channels
played_first_file = set()  # keep track of guilds where the bot has already played the first file

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
            if channel.guild.id not in played_first_file:
                played_first_file.add(channel.guild.id)
                vc.play(discord.FFmpegPCMAudio('file1.mp3'))
                while vc.is_playing():
                    await asyncio.sleep(1)
            else:
                await asyncio.sleep(0.5)  # Wait half a second before playing the second file
            await vc.disconnect()
            del connected_voice_channels[channel.guild.id]
            played_first_file.remove(channel.guild.id)
        except asyncio.TimeoutError:
            print("Connection to voice channel timed out.")
        except Exception as e:
            print(f"Failed to connect to voice channel: {e}")
    elif before.channel is not None and after.channel is None and member.id != client.user.id:
        # Someone left the voice channel
        voice = connected_voice_channels.get(before.channel.guild.id)
        if voice and voice.is_connected():
            voice.play(discord.FFmpegPCMAudio('file2.mp3'))
            while voice.is_playing():
                await asyncio.sleep(1)
            await voice.disconnect()
            del connected_voice_channels[before.channel.guild.id]
        else:
            # Bot is not connected to any voice channel, connect to the one the user left from
            channel = before.channel
            try:
                vc = await channel.connect()
                connected_voice_channels[channel.guild.id] = vc
                vc.play(discord.FFmpegPCMAudio('file2.mp3'))
                while vc.is_playing():
                    await asyncio.sleep(1)
                await vc.disconnect()
                del connected_voice_channels[channel.guild.id]
            except asyncio.TimeoutError:
                print("Connection to voice channel timed out.")
            except Exception as e:
                print(f"Failed to connect to voice channel: {e}")


client.run(config.BOT_TOKEN)
