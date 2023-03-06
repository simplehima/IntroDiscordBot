const fs = require('fs');
const path = require('path');
const { Client, Intents } = require('discord.js');
const { REST } = require('@discordjs/rest');
const { Routes } = require('discord-api-types/v9');
const ytdl = require('ytdl-core-discord');
const config = require('./config.js');

const commands = [];
const commandFiles = fs.readdirSync('./commands').filter(file => file.endsWith('.js'));

const client = new Client({ intents: [Intents.FLAGS.GUILDS] });
let connectionAttempts = 0;
let connectionTimer;

client.once('ready', async () => {
    console.log('Ready!');
    const rest = new REST({ version: '9' }).setToken(config.token);

    for (const file of commandFiles) {
        const command = require(`./commands/${file}`);
        commands.push(command.data.toJSON());
    }

    try {
        console.log('Started refreshing application (/) commands.');

        await rest.put(
            Routes.applicationCommands(config.clientId),
            { body: commands },
        );

        console.log('Successfully reloaded application (/) commands.');
    } catch (error) {
        console.error(error);
    }
});

client.on('interactionCreate', async interaction => {
    if (!interaction.isCommand()) return;

    const command = require(`./commands/${interaction.commandName}`);
    try {
        await command.execute(interaction, ytdl);
    } catch (error) {
        console.error(error);
        await interaction.reply({ content: 'There was an error while executing this command!', ephemeral: true });
    }
});

// Define a function to attempt to connect to the voice channel
async function connectToVoiceChannel(channel) {
    try {
        const connection = await channel.join();
        console.log(`Connected to voice channel: ${channel.name}`);
        connectionAttempts = 0; // reset the connection attempts count
        return connection;
    } catch (error) {
        console.error(`Failed to connect to voice channel: ${error}`);
        return null;
    }
}

client.on('voiceStateUpdate', async (oldState, newState) => {
    if (!oldState.channel && newState.channel) {
        // A user has joined a voice channel
        const connection = await connectToVoiceChannel(newState.channel);

        if (connection) {
            // Play audio file
            const dispatcher = connection.play(ytdl('https://www.youtube.com/watch?v=dQw4w9WgXcQ'), { type: 'opus' });
            dispatcher.on('finish', () => {
                connection.disconnect();
                console.log('Disconnected from voice channel.');
            });
        } else {
            // If connection fails, schedule a reconnection attempt
            connectionAttempts++;
            const delay = Math.min(connectionAttempts * 5000, 60000); // Increase delay between attempts up to 1 minute
            console.log(`Attempting to reconnect in ${delay / 1000} seconds...`);
            connectionTimer = setTimeout(() => {
                connectToVoiceChannel(newState.channel);
            }, delay);
        }
    }
});

client.on('disconnect', () => {
    // If the client loses connection to Discord, clear the connection timer
    console.log('Disconnected from Discord. Clearing connection timer...');
    clearTimeout(connectionTimer);
});

client.login(config.token);
