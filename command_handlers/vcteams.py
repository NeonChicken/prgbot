import random
import os
import math
import asyncio

prefix = '!'
timeout_time = 20

# Generate Team
async def run(client, message):
    # help message
    def help_msg():
        filename = str(os.path.basename(__file__))
        commandname = filename.replace('.py', '')
        response = "{}".format(message.author.mention) + "" \
                   "\n\n**" + prefix +  "{}** ***(amount of teams)***" \
                                        "\nMakes teams based on your current voice channel.".format(commandname) + "" \
                                        "\n\nIf you want a *seperate amount of players* in each team;\nAfter (amount of teams) you can type **true**. Example:" \
                                        "\n" + prefix +  "{} 2 true".format(commandname)

        return response

    if len(message.content.split()) < 2:
        await message.channel.send(help_msg())
        return

    if len(message.content.split()) >= 2:
        try:
            if message.content.split()[2].lower() == 'true':
                if int(message.content.split()[1]):
                    if message.author.voice and message.author.voice.channel:
                        team_amt = int(message.content.split()[1])
                        player_amt_per_team = []

                        channel = message.author.voice.channel
                        users = []
                        for member in channel.members:
                            users.append(member.name)
                        # custom teams:
                        # users = ['a', 'b', 'c', 'd', 'e']
                        user_amt = len(users)

                        # More teams than players
                        if (team_amt > user_amt):
                            await message.channel.send(
                                "{}, I cannot create **more teams than there are players**!\n".format(message.author.mention))
                            return

                        for team in range(team_amt):
                            await message.channel.send("How many players in team {}?".format(team+1))

                            def check(msg):
                                return msg.author == message.author

                            try:
                                msg = await client.wait_for('message', check=check, timeout=timeout_time)
                            except asyncio.TimeoutError:
                                await message.channel.send(
                                    "{} didn't respond in time! The game hasn't been shown:zzz:".format(
                                        message.author.mention))
                                return
                            else:
                                if msg.content.isdigit():
                                    player_amt_per_team.append(msg.content)
                                else:
                                    await message.channel.send(
                                        "{}, that wasn't a digit! Try again...".format(message.author.mention))
                                    return
                        # player_amt_per_team > index is the team, index key is the amount of players

                        # checking if player total exceeds players in VoiceChat
                        playerTotal = 0
                        for teamTotal in player_amt_per_team:
                            playerTotal += int(teamTotal)
                        print(playerTotal)
                        if playerTotal > user_amt:
                            await message.channel.send(
                                "{}, your input exceeds the players present in your voicechat!\n".format(message.author.mention))
                            return

                        msg = "{}, teams generated from *{}:*\n\n".format(message.author.mention, channel)
                        temp_users = users
                        temp_team_amt = team_amt
                        for team in range(team_amt):
                            msg += "**Team {}:** ".format(team + 1)
                            # players in this team is ceiled users that are LEFT, divided by the team amount that's LEFT
                            playersInThisTeam = int(player_amt_per_team[team])

                            for teamPlayers in range(playersInThisTeam):
                                choice = random.choice(temp_users)
                                if teamPlayers + 1 >= playersInThisTeam:
                                    msg += "*{}* ".format(choice)
                                else:
                                    msg += "*{}* | ".format(choice)
                                temp_users.remove(choice)

                            msg += "\n"

                            # Removing the amount of users that are put in this loop
                            user_amt -= playersInThisTeam
                            temp_team_amt -= 1
                        await message.channel.send(msg)
                        return

                    else:
                        await message.channel.send("{}, you are not connected to a voice channel.".format(message.author.mention))
                        return
                pass
        except IndexError:
            pass
        try:
            if int(message.content.split()[1]):
                team_amt = int(message.content.split()[1])
                if message.author.voice and message.author.voice.channel:
                    channel = message.author.voice.channel
                    users = []
                    for member in channel.members:
                        users.append(member.name)
                    # custom teams:
                    # users = ['a', 'b', 'c']
                    user_amt = len(users)
                    
                    # More teams than players
                    if (team_amt > user_amt):
                        await message.channel.send("{}, I cannot create **more teams than there are players**!\n".format(message.author.mention))
                        return

                    msg = "{}, teams generated from *{}:*\n\n".format(message.author.mention, channel)
                    temp_users = users
                    temp_team_amt = team_amt
                    for team in range(team_amt):
                        msg += "**Team {}:** ".format(team + 1)
                        # players in this team is ceiled users that are LEFT, divided by the team amount that's LEFT
                        playersInThisTeam = math.ceil(user_amt / temp_team_amt)

                        for teamPlayers in range(playersInThisTeam):
                            choice = random.choice(temp_users)
                            if teamPlayers+1 >= playersInThisTeam:
                                msg += "*{}* ".format(choice)
                            else:
                                msg += "*{}* | ".format(choice)
                            temp_users.remove(choice)

                        msg += "\n"

                        # Removing the amount of users that are put in this loop
                        user_amt -= playersInThisTeam
                        temp_team_amt -= 1
                    await message.channel.send(msg)


                else:
                    await message.channel.send("{}, you are not connected to a voice channel.".format(message.author.mention))
                    return
        except ValueError:
            commandname = str(os.path.basename(__file__)).replace('.py', '')
            await message.channel.send("{}\n*".format(message.author.mention) + prefix + "{}* ***(amount of teams)*** should be an number divisible by the amount of players in your chat!".format(commandname))
            return