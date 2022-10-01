# PRG Bot
PRG Bot is a bot made for the PRG Discord Server. It has simple functionality and will execute simple commands that are custom-made for the PRG community.

## Getting Started
To get a copy of PRG Bot running on your own system, follow these instructions.

### Prerequisites
#### Python 3
To be able to run PRG Bot, you will need Python 3.5.3 or higher. We will assume you already have Python installed on your system. If you don't, have a look [here](https://realpython.com/installing-python/) to see how you can install it.

#### Discord<span></span>.py
We will be using the Python package [discord.py](https://discordpy.readthedocs.io/) to allow Python to interact with Discord. You can install it with `pip install discord.py` or `pip3 install discord.py`. I recommend installing it in a virtual environment. For more information on this, have a look [here](https://docs.python.org/3/tutorial/venv.html).

### Running your own test server

1. Clone or download this repository to your computer.
2. In Discord, create your own Discord server where you want to test the bot, if you haven't already done so.
3. Log in to your Discord account on discordapp.com/developers.
4. Click 'New Application'.
5. Choose a name for your bot and click 'Create'.
6. In the menu on the left, click 'Bot'.
7. Click 'Add Bot' and confirm you want to do this by clicking 'Yes, do it!'.
8. Under 'Token', click 'Copy'.
9. Store your token in an environment variable called `TOKEN`: `export TOKEN=<your-token>`
10. Back in your Application settings on the Discord website, click on 'OAuth2' and check the 'bot' box under 'Scopes'. 
11. Under 'Bot permissions', you can specify which permissions your bot will need. If you are only going to run the bot on your own Discord server, it won't hurt to give your bot admin rights. To do so, check the 'Administrator' box.
12. Under 'Scopes, you will now see your bot's invite link. Paste this link in the address bar of your browser to invite the bot. Choose your server and click 'Continue'. Check the 'Administrator' box and click 'Authorize'. Click 'I am not a robot' to continue.
13. Now, start your bot server with `python3 PRGbot.py`, and you can use to bot in your Discord server!

## Authors
- **Marco Breemhaar** - *Framework* - www.marcobreemhaar.nl
- **Luuk van Dort** - *Commands and games* - www.neondeluxe.nl/

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
