# Discord Bot

This is a Discord bot that plays a sound when a user joins a voice channel and plays another sound when someone leaves.

## Requirements

- Python 3.x
- discord.py

## Installation

1. Clone this repository to your local machine.
2. Install the required dependencies by running `pip install -r requirements.txt`.
3. Create a new Discord bot account and get the bot token.
4. Copy the token to the `config.py` file.
5. Place Your File.mp3 in same folder of the bot.py
6. Replace `'file1.mp3'` & `'file2.mp3' with the name of the mp3 file you want to play in line 36 & 48.
7. Run the bot by running `python bot.py`.

## Usage

- When a user joins a voice channel, the bot will play a sound in that channel.
- To stop the bot, type `!stop` in any text channel.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
