import random
import asyncio
import json
import os
import io
import re
import discord
import operator
import math

prefix = '!'

timeout_time = 600.0  # message.author response time in seconds
player_limit = 20  # the player limit of uno participation

global_leaderboard_entrypoint = 10

# global dict for ELO ranking multiplier
rank_multiplier = {
    "1st": 1,
    "2nd": 0.5,
    "3rd": -0.25,
    "4+": -0.75,
    "last": -2,
}

# global dict for rank icons
# key: [file-location, RANK]
rank_icons = {
    "1copper" : [discord.File('resources/ranks/1copper.png'), 940],
    "1silver": [discord.File('resources/ranks/1silver.png'), 950],
    "1gold": [discord.File('resources/ranks/1gold.png'), 960],
    "1sub": [discord.File('resources/ranks/1sublime.png'), 970],
    "2copper": [discord.File('resources/ranks/2copper.png'), 980],
    "2silver": [discord.File('resources/ranks/2silver.png'), 990],
    "2gold": [discord.File('resources/ranks/2gold.png'), 1000],
    "2sub": [discord.File('resources/ranks/2sublime.png'), 1010],
    "3copper": [discord.File('resources/ranks/3copper.png'), 1020],
    "3silver": [discord.File('resources/ranks/3silver.png'), 1030],
    "3gold": [discord.File('resources/ranks/3gold.png'), 1040],
    "3sub": [discord.File('resources/ranks/3sublime.png'), 1050],
    "4ult": [discord.File('resources/ranks/4ult.png'), 1060]
}

data = {}
data['games'] = []


def create_json_uno():
    with io.open(os.path.join('./resources/battle', 'uno.json'), 'w') as file:
        json.dump(data, file, indent=4)
    with open('./resources/battle/uno.json') as file:
        first_file = json.load(file)
        first_file['games'].append({'name': 'null'})
        with open('./resources/battle/uno.json', 'w') as f:
            json.dump(first_file, f, indent=4)


# Flip a coin and send the result.
async def run(client, message):
    leaderboard_limit = 5  # the amount of players displayed on the leaderboard
    leaderboard_entrypoint = 10  # the amount of UNO games you must have played before you can show up on the leaderboard

    # help message
    def help_msg():
        filename = str(os.path.basename(__file__))
        commandname = filename.replace('.py', '')
        response = "{}, welcome to **".format(message.author.mention) + prefix + "{}** ".format(
            commandname) + "database!" \
                           "\n\nAfter **" + prefix + "{}** ".format(commandname) \
                   + "you can use: " \
                     "\n**wins** *{year}* *{players}* *{games}* *{reverse}* - The leaderboard" \
                     "\n**leb** *{year}* *{players}* *{games}* - The leaderboard" \
                     "\n**lob** *{year}* *{players}* *{games}* - The loserboard" \
                     "\n**name** *{name}* *{year}* *{games}* - Ranking by name" \
                     "\n**show** - Show a game by ID" \
                     "\n\n*{name}* = name of a player" \
                     "\n*{year}* = *2018* | *2019* | *2020* | *N/A* | *ALL*" \
                     "\n*{players}* = amount of players to show *(in digits)*, default = 5" \
                     "\n*{games}* = minimum amount of games needed on record *(in digits)*, default = 10" \
                     "\n*{reverse}* = reverse the sorting order *(true/false)*" \
                     "\n\n\n*(Admin only):*" \
                     "\n**add** - Add a game" \
                     "\n**dl** - Request & download .json data" \
                     "\n**edit** - Edit date" \
                     "\n**delete** - Delete data"

        return response

    # loading save files
    if not os.path.isfile('./resources/battle/uno.json'):
        # if file not found, make uno.json with create_json_uno function
        create_json_uno()
        await message.channel.send('*uno.json has been created. Please try again.*')
        return
    else:
        with open('./resources/battle/uno.json') as file:
            uno_file = json.load(file)
            if str(uno_file) == '' or str(uno_file) == '[]' or str(uno_file) == '{}':
                create_json_uno()
                await message.channel.send('*uno.json was empty. Please try again.*')
                return

    if len(message.content.split()) < 2:
        await message.channel.send(help_msg())
        return

    def has_numbers(inputString):
        return any(char.isdigit() for char in inputString)

    if len(message.content.split()) >= 2:
        if 'add' in '{}'.format(message.content.lower()):
            if 'UNO-Datist' in str(message.author.roles):

                # Make array empty every time when adding a game (as some sort of global variable)
                player_array = []

                await message.channel.send("Input the date in this format: 2020-6-26 ("
                                           "Year-Month-Day) *\nIf you don't "
                                           "know the exact date, precisely type N/A or na")

                def check(msg):
                    return msg.author == message.author

                try:
                    msg = await client.wait_for('message', check=check, timeout=timeout_time)
                except asyncio.TimeoutError:
                    await message.channel.send(
                        "{} didn't respond in time! The game hasn't been added:zzz:".format(
                            message.author.mention))
                    return
                else:
                    if msg.content.lower() == 'n/a' or msg.content.lower() == 'na':
                        msg_date = 'N/A'
                    else:
                        temp = str(msg.content)
                        temp = temp.strip('[]')
                        temp = temp.strip("'")

                        msg_date = ''
                        r = re.compile('\d{4}-\d{1,2}-\d{1,2}')  # date format
                        if r.match(temp) is not None:
                            msg_date = temp
                        else:
                            await message.channel.send(
                                "Please try again!\nSubmit a date as N/A or in this format: 2020-6-26")
                            return

                        year_of_post = str(message.created_at)
                        year_of_post = year_of_post.split()[0]
                        year_post, month_post, day_post = year_of_post.split('-')

                        try:
                            year, month, day = temp.split('-')
                        except ValueError:
                            await message.channel.send(
                                "Please try again!\nSubmit a date as N/A or in this format: 2020-6-26")
                            return

                        # Checking if the date is possible
                        if int(year) < 2017:
                            await message.channel.send("We didn't start playing Uno until 2017!")
                            return
                        if int(month) > 12:
                            await message.channel.send("There's only 12 months in a year!")
                            return
                        if int(day) > 31:
                            await message.channel.send("There can only be a maximum of 31 days in a year!")
                            return
                        # Checking if the date input exceeds the date of submission, preventing false game reports
                        if int(year) > int(year_post) or (
                                int(month) > int(month_post) and int(year) == int(year_post)) or (
                                int(month) == int(month_post) and int(year) == int(year_post) and int(day) > int(
                            day_post)):
                            await message.channel.send("You can't submit games that haven't been played yet!")
                            return

                    await message.channel.send("Input the total amount of players for this game")

                    def check(msg):
                        return msg.author == message.author

                    try:
                        msg = await client.wait_for('message', check=check, timeout=timeout_time)
                    except asyncio.TimeoutError:
                        await message.channel.send(
                            "{} didn't respond in time! The game hasn't been added:zzz:".format(message.author.mention))
                        return
                    else:
                        if has_numbers(msg.content):
                            if int(msg.content) > 2 and int(msg.content) < player_limit:
                                msg_player_count = int(msg.content)

                                await message.channel.send("Input the total amount of rounds that were played")

                                def check(msg):
                                    return msg.author == message.author

                                try:
                                    msg = await client.wait_for('message', check=check, timeout=timeout_time)
                                except asyncio.TimeoutError:
                                    await message.channel.send(
                                        "{} didn't respond in time! The game hasn't been added:zzz:".format(
                                            message.author.mention))
                                    return
                                else:
                                    if has_numbers(msg.content):
                                        msg_round_count = int(msg.content)

                                        live_count = msg_player_count
                                        await message.channel.send(
                                            "Insert data for {} players, use **%** as a separator\nExample: Name "
                                            "20 79 79 82 % Name 0 0 7 15 % Name 15 25 72 103".format(
                                                live_count))

                                        def check(msg):
                                            return msg.author == message.author

                                        try:
                                            msg = await client.wait_for('message', check=check,
                                                                        timeout=timeout_time)
                                        except asyncio.TimeoutError:
                                            await message.channel.send(
                                                "{} didn't respond in time! The game hasn't been added:zzz:".format(
                                                    message.author.mention))
                                            return
                                        else:
                                            if msg.content:
                                                test_str = msg.content.split("%")
                                                if len(test_str) is not int(msg_player_count):
                                                    await message.channel.send(
                                                        "Not the right amount of players! There should be **{}** players, but you entered data for "
                                                        "**{}** players!\n\n*(Perhaps a seperator* ***%*** "
                                                        "*is present where it shouldn't)*".format(
                                                            int(msg_player_count),
                                                            len(test_str)))
                                                    return

                                                for every in test_str:
                                                    # Split[0] is the first word (name)
                                                    msg_string_player = \
                                                        every.lower().replace("-", "").replace(",", "").replace(":",
                                                                                                                "").replace(
                                                            ".",
                                                            "").split()[
                                                            0]
                                                    # Split[1:len] is everything that comes after the first word & (remove dashes: -)
                                                    msg_string_score = every.lower().replace("-", "").replace(",",
                                                                                                              "").replace(
                                                        ":",
                                                        "").replace(
                                                        ".", "").split()[
                                                                       1:len(msg.content.lower().split())]

                                                    # Checking if there's only digits in the score
                                                    for ints in msg_string_score:
                                                        if not ints.isdigit():
                                                            await message.channel.send(
                                                                "You've entered a wrong character! "
                                                                "Please try again.\n"
                                                                "The character: **{}** should be a digit, it's present in **{}** their score".format(
                                                                    ints, msg_string_player.capitalize()))
                                                            return
                                                    # Checking if entered score equals the amount of rounds
                                                    if len(msg_string_score) is not msg_round_count:
                                                        await message.channel.send(
                                                            "You've entered the wrong amount of rounds for player *{}*!"
                                                            "\nThere should be: **{}** rounds.. "
                                                            "{} couldn't have played **{}** rounds!".format(
                                                                msg_string_player,
                                                                msg_round_count, msg_string_player.capitalize(),
                                                                len(msg_string_score)))
                                                        return
                                                    player_array.append({
                                                        'player': '{}'.format(msg_string_player),
                                                        "score": msg_string_score
                                                    })

                                                # todo add notions [after score in brackets (detect brackets as string)]

                                            total_games_in_file = 0
                                            # Just getting the loop, no need to store anything. For = none
                                            for none in uno_file['games']:
                                                total_games_in_file = total_games_in_file + 1

                                            # Making player_array look neat in a string
                                            player_array_msg = player_array
                                            final_msg = ''
                                            for pl in player_array_msg:
                                                str_scores = str(pl['score'])
                                                str_scores = str_scores.replace("'", "")
                                                str_scores = str_scores.replace("[", "")
                                                str_scores = str_scores.replace("]", "")
                                                final_msg = final_msg + '**{}**: *{}*\n'.format(
                                                    pl['player'].capitalize(),
                                                    str_scores)

                                            await message.channel.send("Received all player data! Do you wish to "
                                                                       "submit the following game? **Y/N**\n\n"
                                                                       "*Game ID* : **{}**\n"
                                                                       "*Submitted By* : {}\n"
                                                                       "*Submission Date* : {}\n"
                                                                       "*Total Players* : **{}**\n"
                                                                       "*Total Rounds* : **{}**\n"
                                                                       "*Game Date* : {}\n\n"
                                                                       "*Players* : \n{}".format(
                                                int(uno_file['games'][len(uno_file['games']) - 1]['game_id']) + 1,
                                                message.author.mention,
                                                message.created_at,
                                                msg_player_count,
                                                msg_round_count,
                                                msg_date,
                                                final_msg))

                                            def check(msg):
                                                return msg.author == message.author

                                            try:
                                                msg = await client.wait_for('message', check=check,
                                                                            timeout=timeout_time)
                                            except asyncio.TimeoutError:
                                                await message.channel.send(
                                                    "{} didn't respond in time! The game hasn't been added:zzz:".format(
                                                        message.author.mention))
                                                return
                                            else:
                                                if 'yes' in msg.content.lower() or 'ye' in msg.content.lower() or 'y' in msg.content.lower():
                                                    uno_file['games'].append({
                                                        'game_id': '{}'.format(int(
                                                            uno_file['games'][len(uno_file['games']) - 1][
                                                                'game_id']) + 1),  # grab last known id and add one
                                                        'submitted_by': '{}'.format(message.author.id),
                                                        'submission_date_UTC': '{}'.format(message.created_at),
                                                        'player_total': '{}'.format(msg_player_count),
                                                        'rounds': '{}'.format(msg_round_count),
                                                        'date': '{}'.format(msg_date),
                                                        'players': player_array
                                                    })
                                                    with open('./resources/battle/uno.json', 'w') as f:
                                                        json.dump(uno_file, f, indent=4)

                                                    await message.channel.send('Game has been submitted!')
                                                    return
                                                elif 'no' in msg.content.lower() or 'n' in msg.content.lower():
                                                    await message.channel.send('Alrighty then!')
                                                    return
                                                else:
                                                    await message.channel.send(
                                                        "I can only understand **yes**, **ye**, **y**, **n** and **no**")
                                                    return
                                    else:
                                        await message.channel.send("You can only input integers!")
                                        return

                            elif int(msg.content) >= 0 and int(msg.content) <= 2:
                                await message.channel.send(
                                    "Uno games with {} players aren't official!".format(int(msg.content)))
                            elif int(msg.content) >= player_limit:
                                await message.channel.send("{} is too many players!".format(int(msg.content)))
                            else:
                                await message.channel.send("Something went wrong...")
                        else:
                            await message.channel.send("You can only input integers!")
                            return

            else:
                response = "Only users with the **UNO-Datist** role can add data!!"
                await message.channel.send(response)

        elif 'leb' in '{}'.format(message.content.lower()):
            try:
                if message.content.split()[3].isdigit():
                    leaderboard_limit = int(message.content.split()[3])
            except IndexError:
                leaderboard_limit = 5  # the amount of players displayed on the leaderboard
            try:
                if message.content.split()[4].isdigit():
                    leaderboard_entrypoint = int(message.content.split()[4])
            except IndexError:
                leaderboard_entrypoint = 10  # the amount of UNO games you must have played before you can show up on the leaderboard

            year = ''
            try:
                years = range(2018, 2200)
                str_years = []
                for i in years:
                    str_years.append(f"{i}")

                if message.content.split()[2].lower() == 'na' or message.content.split()[2].lower() == 'n/a':
                    year = 'n/a'
                elif message.content.split()[2].lower() == 'all':
                    year = 'all'
                elif message.content.split()[2].isdigit():
                    if message.content.split()[2] in str_years:
                        year = int(message.content.split()[2])
                    else:
                        response = "I can only accept: **2018+** | **N/A** | **ALL**"
                        await message.channel.send(response)
                        return
            except IndexError:
                year = 'all'

            year_player_list = []
            for i in uno_file['games']:
                # Don't count the first value because it's null
                if i is not uno_file['games'][0]:
                    # Create empty list > used for storing player names from uno.json
                    if str(year) in i['date'].lower():
                        year_player_list.append(i)
                    elif str(year) == 'all':
                        year_player_list.append(i)

            total_player_list = []
            for y in year_player_list:
                for p in y['players']:
                    if p['player'] not in total_player_list:
                        # Append unknown players into list
                        total_player_list.append({
                            '{}'.format(p['player']): [],
                        })

                    for idx, s in enumerate(p['score']):
                        if idx == len(p['score']) - 1:
                            for pkey in total_player_list:
                                if p['player'] in pkey:
                                    # If name is found in array of players, append their last round score > (s)
                                    total_player_list[total_player_list.index(pkey)][p['player']].append(s)
                                    # total_player_list PRINTS:
                                    # [{'karst': ['18', '101']}, {'vincent': ['40']},
                                    # {'toon': ['104', '67']}, {'luuk': ['8', '17']}]

            # Getting all player names again
            known_players = []
            leader_names = []
            leader_games = []
            leader_average = []
            for y in year_player_list:
                for p in y['players']:
                    for players in total_player_list:
                        try:
                            if players[p['player']] and p['player'] not in known_players:
                                # Put player in a list so we can check if we already iterated over this player.
                                known_players.append(p['player'])
                                total_score = 0
                                for single_score in players[p['player']]:
                                    total_score = total_score + int(single_score)
                                if len(players[p['player']]) >= leaderboard_entrypoint:
                                    leader_names.append(p['player'].capitalize())
                                    leader_games.append(len(players[p['player']]))
                                    leader_average.append(total_score / len(players[p['player']]))
                        except KeyError:
                            continue

            leader_names_sorted = [x for _, x in sorted(zip(leader_average, leader_names))]
            leader_games_sorted = [x for _, x in sorted(zip(leader_average, leader_games))]
            leader_average_sorted = [x for _, x in sorted(zip(leader_average, leader_average))]
            leader_msg_final = ["***WINNERS***\n*Year: {}*\n\n".format(year)]
            leader_count = len(leader_average_sorted)
            for l in range(leader_count):
                if l < leaderboard_limit:
                    leader_msg_final.append("**{}.** ***{}*** has played ".format(l + 1, leader_names_sorted[l]))
                    leader_msg_final.append("**{}** games with an average of: ".format(leader_games_sorted[l]))
                    leader_msg_final.append("**{}** points!\n".format(round(leader_average_sorted[l], 2)))
            if len(str(leader_msg_final)) >= 2000:
                await message.channel.send("There's more than 2000 characters in my message, try to reduce the amount of players.")
                return
            leader_msg = "".join(map(str, leader_msg_final))
            await message.channel.send("{}".format(leader_msg))
            return

        elif 'lob' in '{}'.format(message.content.lower()):
            try:
                if message.content.split()[3].isdigit():
                    leaderboard_limit = int(message.content.split()[3])
            except IndexError:
                leaderboard_limit = 5  # the amount of players displayed on the leaderboard
            try:
                if message.content.split()[4].isdigit():
                    leaderboard_entrypoint = int(message.content.split()[4])
            except IndexError:
                leaderboard_entrypoint = 10  # the amount of UNO games you must have played before you can show up on the leaderboard

            year = ''
            try:
                years = range(2018, 2200)
                str_years = []
                for i in years:
                    str_years.append(f"{i}")

                if message.content.split()[2].lower() == 'na' or message.content.split()[2].lower() == 'n/a':
                    year = 'n/a'
                elif message.content.split()[2].lower() == 'all':
                    year = 'all'
                elif message.content.split()[2].isdigit():
                    if message.content.split()[2] in str_years:
                        year = int(message.content.split()[2])
                    else:
                        response = "I can only accept: **2018+** | **N/A** | **ALL**"
                        await message.channel.send(response)
                        return
            except IndexError:
                year = 'all'

            year_player_list = []
            for i in uno_file['games']:
                # Don't count the first value because it's null
                if i is not uno_file['games'][0]:
                    # Create empty list > used for storing player names from uno.json
                    if str(year) in i['date'].lower():
                        year_player_list.append(i)
                    elif str(year) == 'all':
                        year_player_list.append(i)

            total_player_list = []
            for y in year_player_list:
                for p in y['players']:
                    if p['player'] not in total_player_list:
                        # Append unknown players into list
                        total_player_list.append({
                            '{}'.format(p['player']): [],
                        })

                    for idx, s in enumerate(p['score']):
                        if idx == len(p['score']) - 1:
                            for pkey in total_player_list:
                                if p['player'] in pkey:
                                    # If name is found in array of players, append their last round score > (s)
                                    total_player_list[total_player_list.index(pkey)][p['player']].append(s)
                                    # total_player_list PRINTS:
                                    # [{'karst': ['18', '101']}, {'vincent': ['40']},
                                    # {'toon': ['104', '67']}, {'luuk': ['8', '17']}]
            # Getting all player names again
            known_players = []
            leader_names = []
            leader_games = []
            leader_average = []
            for y in year_player_list:
                for p in y['players']:
                    for players in total_player_list:
                        try:
                            if players[p['player']] and p['player'] not in known_players:
                                # Put player in a list so we can check if we already iterated over this player.
                                known_players.append(p['player'])
                                total_score = 0
                                for single_score in players[p['player']]:
                                    total_score = total_score + int(single_score)
                                if len(players[p['player']]) >= leaderboard_entrypoint:
                                    leader_names.append(p['player'].capitalize())
                                    leader_games.append(len(players[p['player']]))
                                    leader_average.append(total_score / len(players[p['player']]))
                        except KeyError:
                            continue

            leader_names_sorted = [x for _, x in sorted(zip(leader_average, leader_names), reverse=True)]
            leader_games_sorted = [x for _, x in sorted(zip(leader_average, leader_games), reverse=True)]
            leader_average_sorted = [x for _, x in sorted(zip(leader_average, leader_average), reverse=True)]
            leader_msg_final = [":x: ***LOSERS*** :x:\n*Year: {}*\n\n".format(year)]
            leader_count = len(leader_average_sorted)
            for l in range(leader_count):
                if l < leaderboard_limit:
                    leader_msg_final.append("**{}.** ***{}*** has played ".format(l + 1, leader_names_sorted[l]))
                    leader_msg_final.append("**{}** games with an average of: ".format(leader_games_sorted[l]))
                    leader_msg_final.append("**{}** points!\n".format(round(leader_average_sorted[l], 2)))
            if len(str(leader_msg_final)) >= 2000:
                await message.channel.send("There's more than 2000 characters in my message, try to reduce the amount of players.")
                return
            leader_msg = "".join(map(str, leader_msg_final))
            await message.channel.send("{}".format(leader_msg))
            return

        elif 'wins' in '{}'.format(message.content.lower()):
            try:
                if message.content.split()[3].isdigit():
                    leaderboard_limit = int(message.content.split()[3])
            except IndexError:
                leaderboard_limit = 5  # the amount of players displayed on the leaderboard
            try:
                if message.content.split()[4].isdigit():
                    leaderboard_entrypoint = int(message.content.split()[4])
            except IndexError:
                leaderboard_entrypoint = 10  # the amount of UNO games you must have played before you can show up on the leaderboard

            sort_rev = False
            try:
                if message.content.split()[5] == 'true':
                    sort_rev = True
            except IndexError:
                sort_rev = False

            year = ''
            try:
                years = range(2018, 2200)
                str_years = []
                for i in years:
                    str_years.append(f"{i}")

                if message.content.split()[2].lower() == 'na' or message.content.split()[2].lower() == 'n/a':
                    year = 'n/a'
                elif message.content.split()[2].lower() == 'all':
                    year = 'all'
                elif message.content.split()[2].isdigit():
                    if message.content.split()[2] in str_years:
                        year = int(message.content.split()[2])
                    else:
                        response = "I can only accept: **2018+** | **N/A** | **ALL**"
                        await message.channel.send(response)
                        return
            except IndexError:
                year = 'all'

            year_player_list = []
            for i in uno_file['games']:
                # Don't count the first value because it's null
                if i is not uno_file['games'][0]:
                    # Create empty list > used for storing player names from uno.json
                    if str(year) in i['date'].lower():
                        year_player_list.append(i)
                    elif str(year) == 'all':
                        year_player_list.append(i)

            total_player_list = []
            player_checklist = []
            for y in year_player_list:
                win_names = []
                for p in y['players']:
                    # If player not found, add to total_player_list for storing game info and checklist for checking
                    if p['player'] not in player_checklist:
                        # Append unknown players into list
                        total_player_list.append({
                            '{}'.format(p['player']): [],
                        })
                        player_checklist.append(p['player'])

                    for idx, s in enumerate(p['score']):
                        if idx == len(p['score']) - 1:
                            for pkey in total_player_list:
                                if p['player'] in pkey:
                                    # If name is found in array of players, and it's the first game, make first key 1
                                    if total_player_list[total_player_list.index(pkey)][p['player']] == []:
                                        # Add to player: games, wins, losses, last score
                                        total_player_list[total_player_list.index(pkey)][p['player']] = [1, 0, 0, 0]

                                        total_player_list[total_player_list.index(pkey)][p['player']][3] = int(s)

                                    # If first game key exists, add 1 per played game to get total played games
                                    else:
                                        total_player_list[total_player_list.index(pkey)][p['player']][0] = \
                                            total_player_list[total_player_list.index(pkey)][p['player']][0] + 1

                                        total_player_list[total_player_list.index(pkey)][p['player']][3] = int(s)
                                    win_names.append(total_player_list[total_player_list.index(pkey)])

                # Making new list per game to sort
                one_game = []
                for p in y['players']:
                    for w in win_names:
                        if p['player'] in w:
                            one_game.append((
                                '{}'.format(p['player']),
                                w[p['player']][3],
                            ))
                sorted_game = sorted(one_game, key=operator.itemgetter(1))

                # Making new list to check if player key matches win or lose position.
                for p in y['players']:
                    # If this player key is in first place
                    if p['player'] == sorted_game[0][0]:
                        for pp in total_player_list:
                            if p['player'] in pp:
                                # Add 1 won game to player
                                total_player_list[total_player_list.index(pp)][p['player']][1] = \
                                    total_player_list[total_player_list.index(pp)][p['player']][1] + 1
                        # FIRST PLACE
                    elif p['player'] == sorted_game[len(sorted_game) - 1][0]:
                        for pp in total_player_list:
                            if p['player'] in pp:
                                # Add 1 lost game to player
                                total_player_list[total_player_list.index(pp)][p['player']][2] = \
                                    total_player_list[total_player_list.index(pp)][p['player']][2] + 1
                        # LAST PLACE

            # Getting all player names again
            known_players = []
            leader_names = []
            for y in year_player_list:
                for p in y['players']:
                    for players in total_player_list:
                        try:
                            if p['player'] not in known_players:
                                if players[p['player']][0] >= leaderboard_entrypoint:
                                    # Append name > total > wins > losses
                                    leader_names.append((
                                        p['player'].capitalize(),
                                        players[p['player']][0],
                                        players[p['player']][1],
                                        players[p['player']][2],
                                        round(((players[p['player']][1] - players[p['player']][2]) /
                                               players[p['player']][0] + 1), 2)
                                    ))
                                # Put player in a list so we can check if we already iterated over this player.
                                known_players.append(p['player'])
                        except KeyError:
                            pass

            leader_sum = lambda playerw: (playerw[2] - playerw[3]) / playerw[1]
            if sort_rev == True:
                leader_names_sorted = sorted(leader_names, key=leader_sum)
            else:
                leader_names_sorted = sorted(leader_names, key=leader_sum, reverse=True)
            leader_msg_final = ["***UNO WINS***\n*Year: {}*\n```css\n".format(year)]
            leader_count = len(leader_names_sorted)
            for l in range(leader_count):
                if l < leaderboard_limit:
                    leader_msg_final.append("{}. #{} has a ratio of [{}]\nWon: {}/{} Lost: {}/{}\n\n".format(l + 1,
                                                                                                             leader_names_sorted[
                                                                                                                 l][0],
                                                                                                             leader_names_sorted[
                                                                                                                 l][4],
                                                                                                             leader_names_sorted[
                                                                                                                 l][2],
                                                                                                             leader_names_sorted[
                                                                                                                 l][1],
                                                                                                             leader_names_sorted[
                                                                                                                 l][3],
                                                                                                             leader_names_sorted[
                                                                                                                 l][1]))
            if len(str(leader_msg_final)) >= 2000:
                await message.channel.send("There's more than 2000 characters in my message, try to reduce the amount of players.")
                return
            leader_msg_final.append("\n```")
            leader_msg = "".join(map(str, leader_msg_final))
            await message.channel.send("{}".format(leader_msg))
            return

        elif 'show' in '{}'.format(message.content.lower()):
            await message.channel.send("Which game do you want to see? Give me the ID digits.")

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
                    game_count = 0
                    for g in uno_file['games']:
                        # Don't count the first value because it's null
                        if g is not uno_file['games'][0]:
                            game_count = game_count + 1
                            if int(msg.content) > len(uno_file['games']):
                                await message.channel.send("Couldn't find that ID!")
                                return
                            elif g['game_id'] == msg.content:
                                # Making player_array look neat in a string
                                player_array_msg = g['players']
                                final_msg = ''
                                for pl in player_array_msg:
                                    str_scores = str(pl['score'])
                                    str_scores = str_scores.replace("'", "")
                                    str_scores = str_scores.replace("[", "")
                                    str_scores = str_scores.replace("]", "")
                                    final_msg = final_msg + '**{}**: *{}*\n'.format(
                                        pl['player'].capitalize(),
                                        str_scores)
                                await message.channel.send(
                                    "*Game ID* : **{}**\n"
                                    "*Submitted By* : {}\n"
                                    "*Submission Date* : {}\n"
                                    "*Total Players* : **{}**\n"
                                    "*Total Rounds* : **{}**\n"
                                    "*Game Date* : {}\n\n"
                                    "*Players* : \n{}".format(g['game_id'],
                                                              g['submitted_by'],
                                                              g['submission_date_UTC'],
                                                              g['player_total'],
                                                              g['rounds'],
                                                              g['date'],
                                                              final_msg))
                                return
                            elif game_count >= len(uno_file['games']) - 1:
                                await message.channel.send("That ID doesn't exist!")
                                return
                else:
                    await message.channel.send("That ID doesn't exist!")
                    return

        elif 'name' in '{}'.format(message.content.lower()):
            try:
                if message.content.split()[4].isdigit():
                    leaderboard_entrypoint = int(message.content.split()[4])
            except IndexError:
                leaderboard_entrypoint = 10  # the amount of UNO games you must have played before you can show up on the leaderboard

            year = ''
            try:
                years = range(2018, 2200)
                str_years = []
                for i in years:
                    str_years.append(f"{i}")

                if message.content.split()[2].lower() == 'na' or message.content.split()[2].lower() == 'n/a':
                    year = 'n/a'
                elif message.content.split()[2].lower() == 'all':
                    year = 'all'
                elif message.content.split()[2].isdigit():
                    if message.content.split()[2] in str_years:
                        year = int(message.content.split()[2])
                    else:
                        response = "I can only accept: **2018+** | **N/A** | **ALL**"
                        await message.channel.send(response)
                        return
            except IndexError:
                year = 'all'

            year_player_list = []
            for i in uno_file['games']:
                # Don't count the first value because it's null
                if i is not uno_file['games'][0]:
                    # Create empty list > used for storing player names from uno.json
                    if str(year) in i['date'].lower():
                        year_player_list.append(i)
                    elif str(year) == 'all':
                        year_player_list.append(i)

            total_player_list = []
            for y in year_player_list:
                for p in y['players']:
                    if p['player'] not in total_player_list:
                        # Append unknown players into list
                        total_player_list.append({
                            '{}'.format(p['player']): [],
                        })

                    for idx, s in enumerate(p['score']):
                        if idx == len(p['score']) - 1:
                            for pkey in total_player_list:
                                if p['player'] in pkey:
                                    # If name is found in array of players, append their last round score > (s)
                                    total_player_list[total_player_list.index(pkey)][p['player']].append(s)
                                    # total_player_list PRINTS:
                                    # [{'karst': ['18', '101']}, {'vincent': ['40']},
                                    # {'toon': ['104', '67']}, {'luuk': ['8', '17']}]

            name = ''
            name_meets_entrypoint = True
            new_entrypoint = 0
            for idx, players in enumerate(total_player_list):
                if message.content.split()[2] == list(players.keys())[0] and int(idx) != int(len(total_player_list) - 1):
                    name = message.content.split()[2].lower()
                    if len(total_player_list[idx][list(players.keys())[0]]) < leaderboard_entrypoint:
                        # If the total amount of games from the entered player is less than the entrypoint:
                        name_meets_entrypoint = False
                        new_entrypoint = len(total_player_list[idx][list(players.keys())[0]])
                        leaderboard_entrypoint = len(total_player_list[idx][list(players.keys())[0]])
                    break
                elif message.content.split()[2] != list(players.keys())[0] and int(idx) == int(len(total_player_list) - 1) and name == '':
                    await message.channel.send("That name does not exist in the list!")
                    return

            # Getting all player names again
            known_players = []
            leader_names = []
            leader_games = []
            leader_average = []
            for y in year_player_list:
                for p in y['players']:
                    for players in total_player_list:
                        try:
                            if players[p['player']] and p['player'] not in known_players:
                                # Put player in a list so we can check if we already iterated over this player.
                                known_players.append(p['player'])
                                total_score = 0
                                for single_score in players[p['player']]:
                                    total_score = total_score + int(single_score)
                                if len(players[p['player']]) >= leaderboard_entrypoint:
                                    leader_names.append(p['player'].capitalize())
                                    leader_games.append(len(players[p['player']]))
                                    leader_average.append(total_score / len(players[p['player']]))

                        except KeyError:
                            continue

            leader_names_sorted = [x for _, x in sorted(zip(leader_average, leader_names))]
            leader_games_sorted = [x for _, x in sorted(zip(leader_average, leader_games))]
            leader_average_sorted = [x for _, x in sorted(zip(leader_average, leader_average))]
            if name_meets_entrypoint == False:
                leader_msg_final = ["```css\n{} has not played enough games yet! ({}/{})\nAdjusting the entrypoint to {} games\n\n[These ranks are unofficial!]```\n".format(name.capitalize(), new_entrypoint, global_leaderboard_entrypoint, new_entrypoint)]
                pass
            else:
                leader_msg_final = ["With an entrypoint of {} games\n*Year: {}*\n\n".format(leaderboard_entrypoint, year)]

            leader_msg_final.append("***UNO AVERAGE***\n")
            leader_count = len(leader_average_sorted)
            for l in range(leader_count):
                if name == leader_names_sorted[l].lower():
                    leader_msg_final.append("Rank **{}**:medal:\n***{}*** played ".format(l + 1, leader_names_sorted[l]))
                    leader_msg_final.append("*{}* games with an average of: ".format(leader_games_sorted[l]))
                    leader_msg_final.append("**{}** points!\n".format(round(leader_average_sorted[l], 2)))
            leader_msg = "".join(map(str, leader_msg_final))


            total_player_list = []
            player_checklist = []
            for y in year_player_list:
                win_names = []
                for p in y['players']:
                    # If player not found, add to total_player_list for storing game info and checklist for checking
                    if p['player'] not in player_checklist:
                        # Append unknown players into list
                        total_player_list.append({
                            '{}'.format(p['player']): [],
                        })
                        player_checklist.append(p['player'])

                    for idx, s in enumerate(p['score']):
                        if idx == len(p['score']) - 1:
                            for pkey in total_player_list:
                                if p['player'] in pkey:
                                    # If name is found in array of players, and it's the first game, make first key 1
                                    if total_player_list[total_player_list.index(pkey)][p['player']] == []:
                                        # Add to player: games, wins, losses, last score
                                        total_player_list[total_player_list.index(pkey)][p['player']] = [1, 0, 0, 0]

                                        total_player_list[total_player_list.index(pkey)][p['player']][3] = int(s)

                                    # If first game key exists, add 1 per played game to get total played games
                                    else:
                                        total_player_list[total_player_list.index(pkey)][p['player']][0] = \
                                            total_player_list[total_player_list.index(pkey)][p['player']][0] + 1

                                        total_player_list[total_player_list.index(pkey)][p['player']][3] = int(s)
                                    win_names.append(total_player_list[total_player_list.index(pkey)])

                # Making new list per game to sort
                one_game = []
                for p in y['players']:
                    for w in win_names:
                        if p['player'] in w:
                            one_game.append((
                                '{}'.format(p['player']),
                                w[p['player']][3],
                            ))
                sorted_game = sorted(one_game, key=operator.itemgetter(1))

                # Making new list to check if player key matches win or lose position.
                for p in y['players']:
                    # If this player key is in first place
                    if p['player'] == sorted_game[0][0]:
                        for pp in total_player_list:
                            if p['player'] in pp:
                                # Add 1 won game to player
                                total_player_list[total_player_list.index(pp)][p['player']][1] = \
                                    total_player_list[total_player_list.index(pp)][p['player']][1] + 1
                        # FIRST PLACE
                    elif p['player'] == sorted_game[len(sorted_game) - 1][0]:
                        for pp in total_player_list:
                            if p['player'] in pp:
                                # Add 1 lost game to player
                                total_player_list[total_player_list.index(pp)][p['player']][2] = \
                                    total_player_list[total_player_list.index(pp)][p['player']][2] + 1
                        # LAST PLACE

            # Getting all player names again
            known_players = []
            leader_names = []
            for y in year_player_list:
                for p in y['players']:
                    for players in total_player_list:
                        try:
                            if p['player'] not in known_players:
                                if players[p['player']][0] >= leaderboard_entrypoint:
                                    # Append name > total > wins > losses
                                    leader_names.append((p['player'].capitalize(), players[p['player']][0], players[p['player']][1], players[p['player']][2],
                                                         round(((players[p['player']][1] - players[p['player']][2]) / players[p['player']][0] + 1), 2)))
                                # Put player in a list so we can check if we already iterated over this player.
                                known_players.append(p['player'])
                        except KeyError:
                            pass

            leader_sum = lambda playerw: (playerw[2] - playerw[3]) / playerw[1]
            leader_names_sorted = sorted(leader_names, key=leader_sum, reverse=True)
            leader_msg_final.append("\n***UNO WINS***\n")
            leader_count = len(leader_names_sorted)

            for l in range(leader_count):
                if name == leader_names_sorted[l][0].lower():
                    leader_msg_final.append("Rank **{}**:medal:\n".format(l + 1))
                    leader_msg_final.append("```css\n")
                    leader_msg_final.append(
                        "#{} has a ratio of [{}]\nWon: {}/{} Lost: {}/{}\n\n".format(leader_names_sorted[l][0], leader_names_sorted[l][4], leader_names_sorted[l][2],
                                                                                         leader_names_sorted[l][1], leader_names_sorted[l][3], leader_names_sorted[l][1]))
                    break

            if len(str(leader_msg_final)) >= 2000:
                await message.channel.send("There's more than 2000 characters in my message, try to reduce the amount of players.")
                return
            leader_msg_final.append("\n```")
            leader_msg = "".join(map(str, leader_msg_final))

            await message.channel.send("{}".format(leader_msg))
            return

        elif 'elo' in '{}'.format(message.content.lower()):
            year_player_list = []
            for i in uno_file['games']:
                # Don't count the first value because it's null
                if i is not uno_file['games'][0]:
                    year_player_list.append(i)

            total_player_list = []
            player_checklist = []
            for y in year_player_list:
                win_names = []
                for p in y['players']:
                    # If player not found, add to total_player_list for storing game info and checklist for checking
                    if p['player'] not in player_checklist:
                        # Append unknown players into list
                        total_player_list.append({
                            '{}'.format(p['player']): [],
                        })
                        player_checklist.append(p['player'])

                    for idx, s in enumerate(p['score']):
                        if idx == len(p['score']) - 1:
                            for pkey in total_player_list:
                                if p['player'] in pkey:
                                    # If name is found in array of players, and it's the first game,
                                    # make first key 1 > first game
                                    if total_player_list[total_player_list.index(pkey)][p['player']] == []:
                                        # Add to player the following keys:
                                        # 0: games,
                                        # 1: wins,
                                        # 2: losses,
                                        # 3: last score,
                                        # 4: second place,
                                        # 5: third place,
                                        # 6: between third - last,
                                        # 7: ELO (starts with 1000)
                                        total_player_list[total_player_list.index(pkey)][p['player']] = [1, 0, 0, 0, 0,
                                                                                                         0, 0, 1000]

                                        total_player_list[total_player_list.index(pkey)][p['player']][3] = int(s)

                                    # If first game key exists, add 1 per played game to get total played games
                                    else:
                                        total_player_list[total_player_list.index(pkey)][p['player']][0] = \
                                            total_player_list[total_player_list.index(pkey)][p['player']][0] + 1

                                        total_player_list[total_player_list.index(pkey)][p['player']][3] = int(s)
                                    win_names.append(total_player_list[total_player_list.index(pkey)])

                # Making new list per game to sort
                one_game = []
                for p in y['players']:
                    for w in win_names:
                        if p['player'] in w:
                            one_game.append((
                                '{}'.format(p['player']),
                                w[p['player']][3],
                            ))
                sorted_game = sorted(one_game, key=operator.itemgetter(1))

                # Making new list to check if player key matches ranking position.
                for p in y['players']:
                    # If this player key is in first place
                    if p['player'] == sorted_game[0][0]:
                        for pp in total_player_list:
                            if p['player'] in pp:
                                # Add 1 won game to player
                                total_player_list[total_player_list.index(pp)][p['player']][1] = \
                                    total_player_list[total_player_list.index(pp)][p['player']][1] + 1
                                # todo changing ELO (starting value = 1000)
                                # todo ELO + (1 * Place Multiplier) – (Wins * 0.1) – (2nds * 0.05) + (losses*0.15)
                                total_player_list[total_player_list.index(pp)][p['player']][7] = \
                                    total_player_list[total_player_list.index(pp)][p['player']][7] \
                                    + (1 * rank_multiplier['1st']) - \
                                    (total_player_list[total_player_list.index(pp)][p['player']][1] * 0.01) - \
                                    (total_player_list[total_player_list.index(pp)][p['player']][4] * 0.005) + \
                                    (total_player_list[total_player_list.index(pp)][p['player']][2] * 0.015)

                    if p['player'] == sorted_game[1][0]:
                        for pp in total_player_list:
                            if p['player'] in pp:
                                total_player_list[total_player_list.index(pp)][p['player']][4] = \
                                    total_player_list[total_player_list.index(pp)][p['player']][4] + 1
                        # SECOND PLACE

                    # If third place is not last place
                    if p['player'] == sorted_game[2][0]:
                        if p['player'] is not sorted_game[len(sorted_game) - 1][0]:
                            for pp in total_player_list:
                                if p['player'] in pp:
                                    total_player_list[total_player_list.index(pp)][p['player']][5] = \
                                        total_player_list[total_player_list.index(pp)][p['player']][5] + 1
                            # THIRD PLACE

                    if p['player'] == sorted_game[len(sorted_game) - 1][0]:
                        for pp in total_player_list:
                            if p['player'] in pp:
                                # Add 1 lost game to player
                                total_player_list[total_player_list.index(pp)][p['player']][2] = \
                                    total_player_list[total_player_list.index(pp)][p['player']][2] + 1
                        # LAST PLACE

                    # If there is a place between third and last
                    try:
                        # amount of players between fourth and last place (fourth-last = folast)
                        folast_int = (len(sorted_game) - 1) - 3
                        for folast_player in range(folast_int):
                            # for every player between 4th and last place
                            # sorted_game[3 + folast_player][0] because folast_player can be 0
                            if p['player'] == sorted_game[3 + folast_player][0]:
                                if sorted_game[2 + folast_player][0] is not sorted_game[len(sorted_game) - 1][0]:
                                    # print('{} was the {} player in: {}'.format(p['player'], 4 + folast_player,sorted_game))
                                    for pp in total_player_list:
                                        if p['player'] in pp:
                                            total_player_list[total_player_list.index(pp)][p['player']][6] = \
                                                total_player_list[total_player_list.index(pp)][p['player']][6] + 1
                        # FOURTH UNTIL LAST PLACE
                    except IndexError:
                        pass

            #    Getting keys!! Because player displays {'name': [total,wins,loss etc.]}
            #    key is that object's key. AKA the player name!
            # for player in total_player_list:
            #    for key in player.keys():
            #        player[key][0] is the total games played for that player

            leader_elo = []
            for player in total_player_list:
                for key in player.keys():
                    leader_elo.append((
                        key.capitalize(),
                        round(player[key][7])
                    ))

            leader_elo_sorted = sorted(leader_elo, key=operator.itemgetter(1), reverse=True)

            # Generating leaderboard MSG
            leader_msg_final = ["***UNO ELO***\n```css\n"]
            leader_count = len(leader_elo_sorted)
            for l in range(leader_count):
                if l < leaderboard_limit:
                    leader_msg_final.append("{}. [{}] ELO: #{}\n\n".format(l+1,leader_elo_sorted[l][1],leader_elo_sorted[l][0]))
            if len(str(leader_msg_final)) >= 2000:
                await message.channel.send("There's more than 2000 characters in my message, try to reduce the amount of players.")
                return
            leader_msg_final.append("\n```")
            leader_msg = "".join(map(str, leader_msg_final))

            for player in total_player_list:
                for key in player.keys():
                    try:
                        if key == message.content.split()[2].lower():
                            leader_msg = leader_msg + "{} is rank: {}\n".format(key.capitalize(), round(player[key][7]))

                            rank_icon = rank_icons['1copper'][0]
                            # E.g. if between rank 970-980, floor to 980 and match rank icon
                            elo_floored = round(player[key][7]) / 10
                            elo_floored = math.floor(elo_floored) * 10
                            for icons in rank_icons:
                                if elo_floored == rank_icons[icons][1]:
                                    rank_icon = rank_icons[icons][0]
                                # len(rank_icons) for exceeding
                                # measure if rank is lower than first key
                                if elo_floored <= rank_icons[list(rank_icons.keys())[0]][1]:
                                    rank_icon = rank_icons[list(rank_icons.keys())[0]][0]
                                # measure if rank is higher than last key
                                if elo_floored >= rank_icons[list(rank_icons.keys())[len(rank_icons) - 1]][1]:
                                    rank_icon = rank_icons[list(rank_icons.keys())[len(rank_icons) - 1]][0]

                            await message.channel.send("{}".format(leader_msg), file=rank_icon)
                            return
                    except IndexError:
                        await message.channel.send("{}".format(leader_msg))
                        return


        elif 'dl' in '{}'.format(message.content.lower()):
            if ('Administrator' in str(message.author.roles)) or ('Moderator' in str(message.author.roles)):
                await message.channel.send(file=discord.File('resources/battle/uno.json'))
            else:
                response = "Only Admins and Mods are able to use this command!"
                await message.channel.send(response)

        elif 'delete' in '{}'.format(message.content.lower()):
            if ('Administrator' in str(message.author.roles)):
                await message.channel.send("Which game do you want do delete? Give me the ID digits.")

                def check(msg):
                    return msg.author == message.author

                try:
                    msg = await client.wait_for('message', check=check, timeout=timeout_time)
                except asyncio.TimeoutError:
                    await message.channel.send(
                        "{} didn't respond in time! The game hasn't been added:zzz:".format(
                            message.author.mention))
                    return
                else:
                    if msg.content.isdigit():
                        for g in uno_file['games']:
                            # Don't count the first value because it's null
                            if g is not uno_file['games'][0]:
                                if int(msg.content) > len(uno_file['games']):
                                    await message.channel.send("Couldn't find that ID!")
                                    return
                                elif g['game_id'] == msg.content:
                                    # Making player_array look neat in a string
                                    player_array_msg = g['players']
                                    final_msg = ''
                                    for pl in player_array_msg:
                                        str_scores = str(pl['score'])
                                        str_scores = str_scores.replace("'", "")
                                        str_scores = str_scores.replace("[", "")
                                        str_scores = str_scores.replace("]", "")
                                        final_msg = final_msg + '**{}**: *{}*\n'.format(
                                            pl['player'].capitalize(),
                                            str_scores)
                                    await message.channel.send(
                                        "*Game ID* : **{}**\n"
                                        "*Submitted By* : {}\n"
                                        "*Submission Date* : {}\n"
                                        "*Total Players* : **{}**\n"
                                        "*Total Rounds* : **{}**\n"
                                        "*Game Date* : {}\n\n"
                                        "*Players* : \n{}"
                                        "\n\n**Are you sure you want to delete this game?** ***Y/N***".format(
                                            g['game_id'],
                                            g['submitted_by'],
                                            g['submission_date_UTC'],
                                            g['player_total'],
                                            g['rounds'],
                                            g['date'],
                                            final_msg))

                                    def check(msg):
                                        return msg.author == message.author

                                    try:
                                        msg = await client.wait_for('message', check=check, timeout=timeout_time)
                                    except asyncio.TimeoutError:
                                        await message.channel.send(
                                            "{} didn't respond in time! The game hasn't been added:zzz:".format(
                                                message.author.mention))
                                        return
                                    else:
                                        if 'yes' in msg.content.lower() or 'ye' in msg.content.lower() or 'y' in msg.content.lower():
                                            for d in uno_file['games']:
                                                # Don't count the first value because it's null
                                                if d is not uno_file['games'][0]:
                                                    if g['game_id'] == d['game_id']:
                                                        await message.channel.send(
                                                            'Game has been deleted!\n\n{}'.format(d))
                                                        uno_file['games'].remove(d)

                                            with open('./resources/battle/uno.json', 'w') as f:
                                                json.dump(uno_file, f, indent=4)

                                            return
                                        elif 'no' in msg.content.lower() or 'n' in msg.content.lower():
                                            await message.channel.send('Alrighty then!')
                                            return
                                        else:
                                            await message.channel.send(
                                                "I can only understand **yes**, **ye**, **y**, **n** and **no**")
                                            return

                    else:
                        await message.channel.send("That ID doesn't exist!")
                        return

            else:
                response = "Only Admins and Mods are able to use this command!"
                await message.channel.send(response)

        elif 'edit' in '{}'.format(message.content.lower()):
            if 'Administrator' in str(message.author.roles):
                await message.channel.send("Which game do you want to edit? Give me the ID digits.")

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
                        game_count = 0
                        for g in uno_file['games']:
                            # Don't count the first value because it's null
                            if g is not uno_file['games'][0]:
                                game_count = game_count + 1
                                if int(msg.content) > len(uno_file['games']):
                                    await message.channel.send("Couldn't find that ID!")
                                    return
                                elif g['game_id'] == msg.content:
                                    # Making player_array look neat in a string
                                    player_array_msg = g['players']
                                    final_msg = ''
                                    for pl in player_array_msg:
                                        str_scores = str(pl['score'])
                                        str_scores = str_scores.replace("'", "")
                                        str_scores = str_scores.replace("[", "")
                                        str_scores = str_scores.replace("]", "")
                                        final_msg = final_msg + '**{}**: *{}*\n'.format(
                                            pl['player'].capitalize(),
                                            str_scores)
                                    await message.channel.send(
                                        "*Game ID* : **{}**\n"
                                        "*Submitted By* : {}\n"
                                        "*Submission Date* : {}\n"
                                        "*Total Players* : **{}**\n"
                                        "*Total Rounds* : **{}**\n"
                                        "*Game Date* : {}\n\n"
                                        "*Players* : \n{}"
                                        "\n\n**What date? Ex: 2020-6-12**".format(
                                            g['game_id'],
                                            g['submitted_by'],
                                            g['submission_date_UTC'],
                                            g['player_total'],
                                            g['rounds'],
                                            g['date'],
                                            final_msg))

                                    def check(msg):
                                        return msg.author == message.author

                                    try:
                                        msg = await client.wait_for('message', check=check, timeout=timeout_time)
                                    except asyncio.TimeoutError:
                                        await message.channel.send(
                                            "{} didn't respond in time! The game hasn't been edited:zzz:".format(
                                                message.author.mention))
                                        return
                                    else:
                                        if msg.content.lower() == 'n/a' or msg.content.lower() == 'na':
                                            msg_date = 'N/A'
                                        else:
                                            temp = str(msg.content)
                                            temp = temp.strip('[]')
                                            temp = temp.strip("'")

                                            msg_date = ''
                                            r = re.compile('\d{4}-\d{1,2}-\d{1,2}')  # date format
                                            if r.match(temp) is not None:
                                                msg_date = temp
                                            else:
                                                await message.channel.send(
                                                    "Please try again!\nSubmit a date as N/A or in this format: 2020-6-26")
                                                return

                                            year_of_post = str(message.created_at)
                                            year_of_post = year_of_post.split()[0]
                                            year_post, month_post, day_post = year_of_post.split('-')

                                            try:
                                                year, month, day = temp.split('-')
                                            except ValueError:
                                                await message.channel.send(
                                                    "Please try again!\nSubmit a date as N/A or in this format: 2020-6-26")
                                                return

                                            # Checking if the date is possible
                                            if int(year) < 2017:
                                                await message.channel.send("We didn't start playing Uno until 2017!")
                                                return
                                            if int(month) > 12:
                                                await message.channel.send("There's only 12 months in a year!")
                                                return
                                            if int(day) > 31:
                                                await message.channel.send(
                                                    "There can only be a maximum of 31 days in a year!")
                                                return
                                            # Checking if the date input exceeds the date of submission, preventing false game reports
                                            if int(year) > int(year_post) or (
                                                    int(month) > int(month_post) and int(year) == int(year_post)) or (
                                                    int(month) == int(month_post) and int(year) == int(
                                                year_post) and int(day) > int(
                                                day_post)):
                                                await message.channel.send(
                                                    "You can't submit games that haven't been played yet!")
                                                return

                                        for d in uno_file['games']:
                                            # Don't count the first value because it's null
                                            if d is not uno_file['games'][0]:
                                                if g['game_id'] == d['game_id']:
                                                    await message.channel.send(
                                                        'Game has been edited!')
                                                    g['date'] = msg_date

                                        with open('./resources/battle/uno.json', 'w') as f:
                                            json.dump(uno_file, f, indent=4)

                                        return

                    else:
                        await message.channel.send("That ID doesn't exist!")
                        return
            else:
                await message.channel.send("You're not an Admin!")
                return

        elif 'test' in '{}'.format(message.content.lower()):
            print(int(uno_file['games'][len(uno_file['games']) - 1]['game_id']) + 1)
            pass


        # todo Uno-player role: They can add a game in real-time, adds this game to a queue which has to be confirmed by a uno-datist!

        # todo biggest hit leaderboard. Look at score value difference!!


        # todo clean sweep victories, final score = 0
        # todo games won at 69,

        else:
            await message.channel.send(help_msg())
            return

# Notions in players[player]

# BORDA
#         aantal x 1e plek =    43 x [aantal players per gewonnen gameronde]
#         aantal x  2e plek =   32 x [aantal players per 2e plek gameronde - 1]
#         aantal x  3e plek =   16 x [aantal players per 3e plek gameronde - 2]
#                               ETC. ETC. ETC. ETC. ETC. ETC. ETC. ETC. ETC. ETC.
#                               ______________________________________________
#                               aantal gespeelde games
#                               = gemiddelde lb borda score
