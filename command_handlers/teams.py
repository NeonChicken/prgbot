import random
import re
import itertools

# First argument specifies number of teams. Other arguments are player names.
# Players are then randomly divided over equally large teams.
def respond(message):
    channel_team_re = re.compile('\?teams (?P<n_teams>\d+) \"(?P<channel_name>.+)\"')

    if channel_team_re.match(message.content):
        num_teams = int(channel_team_re.search(message.content).group('n_teams'))
        channel_name = channel_team_re.search(message.content).group('channel_name')

        voice_channels = [channel for channel in message.guild.voice_channels if channel.name == channel_name]
        if voice_channels:
            options = [member.name for member in voice_channels[0].members if member.bot is False]
        else:
            return 'Could not find that channel'
    else:
        try:
            num_teams = int(message.content.split()[1])
            options = message.content.split()[2:]
        except (ValueError, IndexError):
            return "Give me the number of teams you need and the names of the people you are with. I'll make you some teams."

        if num_teams < 1:
            return "How do you expect me to make {} teams?".format(num_teams)
        elif len(options) == 0:
            return "It's a bit difficult making teams without any people, isn't it?"
        elif len(options) < num_teams:
            if len(options) == 1:
                return "{} teams for {} person? Well, that's not going to work...".format(num_teams, len(options))
            else:
                return "{} teams for {} people? Well, that's not going to work...".format(num_teams, len(options))
    
    
    random.shuffle(options)

    teams = [[] for _ in range(num_teams)]
    it = itertools.cycle(range(num_teams))

    for name in options:
        teams[next(it)].append(name)

    random.shuffle(teams)

    response = ''

    for idx in range(num_teams):
        response += 'Team {}: '.format(idx+1) + ', '.join(teams[idx]) + '\n'

    return response
