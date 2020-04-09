import random
import re
import itertools

# First argument specifies number of teams. Other arguments are player names.
# Players are then randomly divided over equally large teams.
async def run(message):
    channel_team_re = re.compile('\?teams (?P<n_teams>\d+) \"(?P<channel_name>.+)\"')

    if channel_team_re.match(message.content):
        num_teams = int(channel_team_re.search(message.content).group('n_teams'))
        channel_name = channel_team_re.search(message.content).group('channel_name')

        voice_channels = [channel for channel in message.guild.voice_channels if channel.name == channel_name]
        if voice_channels:
            options = [member.name for member in voice_channels[0].members if member.bot is False]
        else:
            response = 'Could not find that channel'
            await message.channel.send(response)
            return
    else:
        try:
            num_teams = int(message.content.split()[1])
            options = message.content.split()[2:]
        except (ValueError, IndexError):
            response = "Give me the number of teams you need and the names of the people you are with. I'll make you some teams."
            await message.channel.send(response)
            return

        if num_teams < 1:
            response = "How do you expect me to make {} teams?".format(num_teams)
            await message.channel.send(response)
            return
        elif len(options) == 0:
            response = "It's a bit difficult making teams without any people, isn't it?"
            await message.channel.send(response)
            return
        elif len(options) < num_teams:
            if len(options) == 1:
                response = "{} teams for {} person? Well, that's not going to work...".format(num_teams, len(options))
                await message.channel.send(response)
                return
            else:
                response = "{} teams for {} people? Well, that's not going to work...".format(num_teams, len(options))
                await message.channel.send(response)
                return
    
    
    random.shuffle(options)

    teams = [[] for _ in range(num_teams)]
    it = itertools.cycle(range(num_teams))

    for name in options:
        teams[next(it)].append(name)

    random.shuffle(teams)

    response = ''

    for idx in range(num_teams):
        response += 'Team {}: '.format(idx+1) + ', '.join(teams[idx]) + '\n'

    await message.channel.send(response)
