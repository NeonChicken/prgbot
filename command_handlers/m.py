import random
import discord
import asyncio
from PIL import Image, ImageFont, ImageDraw, ImageOps
import json
import os
import io
import math
import datetime

# MINE SIM

prefix = '!'

wait_time = 0.5
timeout_time = 20

# items per backpack tier
bp_tier_0 = 20
bp_tier_1 = 50
bp_tier_2 = 100
bp_tier_3 = 225

# Player data
data = {}
data['players'] = []

# todo check if multiple save files are necessary with users using at the same time

# todo logging which upgrades where bought, time from start, time from finish in days, hours and minutes

# todo print multiple unlocks in one big picture

# todo upgrade description in picture

# Create json file
def create_json_player():
    with io.open(os.path.join('./resources/battle', 'miner.json'), 'w') as file:
        json.dump(data, file, indent=4)
    with open('./resources/battle/miner.json') as log:
        first_log = json.load(log)
        first_log['players'].append({'name': 'null'})
        with open('./resources/battle/miner.json', 'w') as f:
            json.dump(first_log, f, indent=4)

# courier new is monospace (even spaced characters)
font = ImageFont.truetype("./resources/misc/fonts/courbd.ttf", 12)
shadow_font = ImageFont.truetype("./resources/misc/fonts/courbd.ttf", 12)
font_big = ImageFont.truetype("./resources/misc/fonts/courbd.ttf", 18)
shadow_font_big = ImageFont.truetype("./resources/misc/fonts/courbd.ttf", 18)
# amount of pixels to offset shadow in text
shadow_offset = 2

# Mine data
#    0=ID,  1=Name,                 2=Description,                                  3=min_amount,  4=max_amount,   5=image
resources = [
    [0,     "dirt",                 "*Tiny grains of rock and organic matter.*",    1,             3,              "resources/items/miner/dirt.png"],
    [1,     "compressed dirt",      "*Tightly packed dirt.*",                       0,             0,              "resources/items/miner/dirt_comp.png"],
    [2,     "stone",                "*A mass of hard, compacted mineral.*",         1,             5,              "resources/items/miner/stone.png"],
    [3,     "compressed stone",     "*Tightly packed stone.*",                      0,             0,              "resources/items/miner/stone_comp.png"],
    [4,     "iron",                 "*A malleable, silver-gray metal.*",            1,             4,              "resources/items/miner/iron.png"],
    [5,     "compressed iron",      "*Very heavy.*",                                0,             0,              "resources/items/miner/iron_comp.png"],
    [6,     "gold",                 "*What a surprise!*",                           1,             2,              "resources/items/miner/gold.png"],
    [7,     "backpack 1",           "Spacious!",                                    0,             0,              "resources/items/miner/bp1.png"],
    [8,     "backpack 2",           "Spacious!",                                    0,             0,              "resources/items/miner/bp2.png"],
    [9,     "backpack 3",           "Spacious!",                                    0,             0,              "resources/items/miner/bp3.png"],
    [10,     "auto miner",          "Very useful!\nMines until your inventory is filled.", 0,      0,              "resources/items/miner/pick2.png"],
    [11,     "lucky upgrade",       "Big money!\nGet more rare items.",             0,             0,              "resources/items/miner/lucky.png"],
    [12,     "haul upgrade",        "More stuff!\nMine larger veins.",              0,             0,              "resources/items/miner/pick.png"],
    [13,     "fast crafter",        "Faster crafting!\nUpon crafting, compresses every material of that kind from your inventory", 0, 0, "resources/items/miner/crafter.png"],
    [14,     "auto compressor",     "Automatic compression upon mining!",           0,             0,              "resources/items/miner/crafter2.png"],
    [15,     "midas crown",         "Everything is gold!",                          0,             0,              "resources/items/miner/crown.png"]
    ]

# Sprite data
# 0=ID, 1=Name, 2=image
sprites = [[0, "lock", "resources/items/miner/lock64.png"]]

# Crafting data
#    0=ID  1=Name           2=image                                 3=unlocked 4=recipe[[resource id, amount], [resource id, amount]]   5=ID    6=research_requirement[[resource id, amount]]
crafting = [
    # Compressed dirt RECIPE                                                   (ID:0 x5)                                                ID      (ID:0 x5)
    [0, "compressed dirt",  "resources/items/miner/dirt_comp.png",  False,     [[0, 5]],                                                1,      [[0, 1]]],
    # Compressed stone RECIPE                                                  (ID:1 x2, ID:2 x3)                                       ID      (ID:1 x1, ID:2 x1)
    [1, "compressed stone", "resources/items/miner/stone_comp.png", False,     [[1, 2], [2, 3]],                                        3,      [[1, 1], [2, 1]]],
    # Compressed iron RECIPE                                                   (ID:3 x3, ID:4 x3)                                       ID      (ID:3 x3, ID:4 x3)
    [2, "compressed iron",  "resources/items/miner/iron_comp.png",  False,     [[3, 2], [4, 3]],                                        5,      [[3, 1], [4, 1]]],
    # Name                                                                     Recipe (ID, AMT)                                         ID      Req (ID, AMT)
    [3, "inventory upgrade 1",  "resources/items/miner/bp1.png",    False,     [[5, 1]],                                                7,      [[5, 1]]],
    # Name                                                                     Recipe (ID, AMT)                                         ID      Req (ID, AMT)
    [4, "inventory upgrade 2",    "resources/items/miner/bp2.png",  False,     [[5, 4]],                                                8,      [[5, 4]]],
    # Name                                                                     Recipe (ID, AMT)                                         ID      Req (ID, AMT)
    [5, "inventory upgrade 3", "resources/items/miner/bp3.png",     False,     [[5, 10], [6, 5]],                                       9,      [[5, 10], [6, 5]]],
    [6, "fast crafter",        "resources/items/miner/crafter.png", False,     [[5, 3]],                                                13,     [[5, 1]]],
    [7, "auto miner",        "resources/items/miner/pick2.png",     False,     [[5, 2]],                                                10,     [[5, 1]]],
    [8, "lucky upgrade",       "resources/items/miner/lucky.png",   False,     [[1, 10], [3, 5], [5, 3]],                               11,     [[5, 1]]],
    [9, "haul upgrade",        "resources/items/miner/pick.png",    False,     [[5, 5], [6, 2]],                                        12,     [[5, 1], [6, 1]]],
    [10, "auto compressor",     "resources/items/miner/crafter2.png", False,   [[5, 10], [6, 15]],                                      14,     [[5, 1], [6, 1]]],
    [11, "midas crown",        "resources/items/miner/crown.png",   False,     [[5, 100], [6, 80]],                                     15,     [[5, 100], [6, 80]]]
]

# First pool with selected items from resources * rarity/10000
pool_0 = [[resources[0]] * 200 + [resources[2]] * 90 + [resources[4]] * 40 + [resources[6]] * 1]
pool_1 = [[resources[0]] * 600 + [resources[2]] * 150 + [resources[4]] * 30 + [resources[6]] * 1]
pool_2 = [[resources[0]] * 300 + [resources[2]] * 75 + [resources[4]] * 50 + [resources[6]] * 10]
pool_3 = [[resources[6]] * 25]

# Mining Simulator
async def run(client, message):
    # help message
    def help_msg():
        filename = str(os.path.basename(__file__))
        commandname = filename.replace('.py', '')
        response =  "{}, welcome to **".format(message.author.mention) + prefix + "{}** ".format(commandname) + \
                    "miner!\n\nAfter **" + prefix + "{}** ".format(commandname) + "you can use:" \
                    "\n**mine** - Mine materials" \
                    "\n**fill** - Mine until your inventory is full" \
                    "\n**inv** - See inventory" \
                    "\n**craft** - Craft materials" \
                    "\n**dump** - Dump materials" \
                    "\n\n**restart** - Start over *(deletes your save file)*"

        return response

    # loading save files
    if not os.path.isfile('./resources/battle/miner.json'):
        # if file not found, make rogue.json with create_json_player function
        create_json_player()
        await message.channel.send('Miner data has been created. Please try again.')
        return
    else:
        with open('./resources/battle/miner.json') as log:
            contents = json.load(log)
            if str(contents) == '' or str(contents) == '[]' or str(contents) == '{}':
                create_json_player()
                await message.channel.send('Miner data did not exist. Please try again.')
                return
            else:
                count = 1
                do_not_create_save = 0
                for p in contents['players']:
                    if str(message.author.id) == str(p['name']):
                        do_not_create_save = 1  # print("Found {}".format(message.author) + " in players!")  # Found message.author in player file!
                    elif str(message.author.id) is not str(p['name']) and do_not_create_save is not 1:
                        if count is int(len(contents['players'])):
                            contents['players'].append(
                                {
                                    'name': '{}'.format(message.author.id),
                                    'name_at_save': '{}'.format(message.author.name),
                                    'total_times_mined': 0,
                                    'inventory_tier': 0,
                                    'lucky': False,
                                    'haul': False,
                                    'fast': False,
                                    'miner': False,
                                    'auto': False,
                                    'midas': False,
                                    'pick_tier': 0,
                                    'inventory': [],
                                    'crafting': crafting,
                                    'research': []})
                            with open('./resources/battle/miner.json', 'w') as f:
                                json.dump(contents, f, indent=4)
                            await message.channel.send('*Created a save file for {}.*'.format(message.author))
                    count = count + 1

                # Help msg and testing space
                if len(message.content.split()) < 2:
                    await message.channel.send(help_msg())

                # Game logic
                elif len(message.content.split()) >= 2:
                    if message.content.split()[1] != 'restart':
                        for p in contents['players']:
                            if str(message.author.id) == str(p['name']):
                                # Check if player has won first
                                if won(p):
                                    filename = str(os.path.basename(__file__))
                                    commandname = filename.replace('.py', '')
                                    msg = "{}'s inventory contains:{}".format(message.author.mention, getInv(p, True)[0])
                                    await message.channel.send(msg, file=getInv(p, True)[1])
                                    msg = "{}, you have completed **".format(message.author.mention) + prefix + "{}** miner!".format(commandname) + " :trophy: :trophy: :trophy:"
                                    msg += "\nYou can start over by typing **" + prefix + "{} restart**".format(commandname)
                                    await message.channel.send(msg)
                                    return

                    if message.content.split()[1] == 'inv':
                        for p in contents['players']:
                            if str(message.author.id) == str(p['name']):
                                # Sort inventory
                                p["inventory"] = sorted(p["inventory"])
                                # Write to player file
                                with open('./resources/battle/miner.json', 'w') as f:
                                    json.dump(contents, f, indent=4)
                                msg = "{}'s inventory contains:{}".format(message.author.mention, getInv(p, True)[0])
                                await message.channel.send(msg, file=getInv(p, True)[1])
                                return

                    if message.content.split()[1] == 'restart':
                        for idx, p in enumerate(contents['players']):
                            if str(message.author.id) == str(p['name']):
                                await message.channel.send("{}, are you sure you want to restart? (Y/N)".format(message.author.mention))

                                def check(msg):
                                    return msg.author == message.author

                                try:
                                    msg = await client.wait_for('message', check=check, timeout=timeout_time)
                                except asyncio.TimeoutError:
                                    await message.channel.send("{}, you've waited too long!".format(message.author.mention))
                                    return
                                else:
                                    yes_list = ['y', 'yes', 'yea', 'yeah', 'ya']
                                    no_list = ['n', 'no', 'nah', 'na']

                                    if msg.content.lower() in yes_list:
                                        await message.channel.send("{}, **your save file will be reset**.\nAre you **really** sure you want to restart? (Y/N)".format(message.author.mention))

                                        def check(msg):
                                            return msg.author == message.author

                                        try:
                                            msg = await client.wait_for('message', check=check, timeout=timeout_time)
                                        except asyncio.TimeoutError:
                                            await message.channel.send("{}, you've waited too long!".format(message.author.mention))
                                            return
                                        else:
                                            if msg.content.lower() in yes_list:
                                                contents['players'].pop(idx)
                                                with open('./resources/battle/miner.json', 'w') as f:
                                                    json.dump(contents, f, indent=4)

                                                await message.channel.send("{}, **your save file has been deleted!**".format(message.author.mention))
                                                return
                                            elif msg.content.lower() in no_list:
                                                await message.channel.send("{}, reset has been cancelled.".format(message.author.mention))
                                                return
                                            else:
                                                await message.channel.send("{}, your message input wasn't recognized.\n*Reset has been cancelled.*".format(message.author.mention))
                                                return
                                    elif msg.content.lower() in no_list:
                                        await message.channel.send("{}, reset has been cancelled.".format(message.author.mention))
                                        return
                                    else:
                                        await message.channel.send("{}, your message input wasn't recognized.\n*Reset has been cancelled.*".format(message.author.mention))
                                        return

                    if message.content.split()[1] == 'mine' or message.content.split()[1] == 'fill':
                        for p in contents['players']:
                            if str(message.author.id) == str(p['name']):

                                # Check if inventory is full first
                                if len(p["inventory"]) >= getBackpackTier(p):
                                    p["inventory"] = sorted(p["inventory"])
                                    filename = str(os.path.basename(__file__))
                                    commandname = filename.replace('.py', '')

                                    await message.channel.send(
                                        "{}, **your inventory is full!** *({}/{} items)*\nConsider **upgrading** your backpack, or using the commands:\n".format(
                                            message.author.mention, len(p["inventory"]), getBackpackTier(p)) + prefix + "{} craft\n".format(commandname) + prefix + "{} dump".format(commandname)
                                        + getInv(p, True)[0], file=getInv(p, True)[1])
                                    return
                                else:
                                    if message.content.split()[1] == 'fill' and not p["miner"]:
                                        await message.channel.send("{}, you can't use the **fill** command yet.\n*You have to unlock and craft the* ***autominer*** *first!*".format(message.author.mention))
                                        return

                                    while len(p["inventory"]) < getBackpackTier(p):
                                        # Generate random item from pool 0, or pool 1 if player has lucky upgrade
                                        if p["midas"]:
                                            r_pool_0 = random.choice(pool_3[0])
                                        elif p["lucky"]:
                                            r_pool_0 = random.choice(pool_2[0])
                                        elif p["inventory_tier"] >= 1:
                                            r_pool_0 = random.choice(pool_1[0])
                                        else:
                                            r_pool_0 = random.choice(pool_0[0])
                                        # Generate random amount of that item in the min-max range
                                        r_pool_0_int = random.randrange(r_pool_0[3], r_pool_0[4] + 1)
                                        if p["midas"]:
                                            r_pool_0_int = random.randrange(1, 21)
                                        # Increase haul, only half for dirt & stone, thrice for gold and iron
                                        if p["haul"]:
                                            if r_pool_0[0] is not 0 and r_pool_0[0] is not 2:
                                                r_pool_0_int *= random.randrange(2, 4)
                                            else:
                                                r_pool_0_int *= 1.5
                                                r_pool_0_int = math.floor(r_pool_0_int)
                                        # If generated amount will overencumber player, retract amount
                                        if (r_pool_0_int + len(p["inventory"])) >= getBackpackTier(p):
                                            r_pool_0_int = getBackpackTier(p) - len(p["inventory"])
                                        # Add to total of times mined
                                        p["total_times_mined"] = p["total_times_mined"] + 1
                                        # Append generated item to inventory * random int min>max from item
                                        for unused in range(r_pool_0_int):
                                            p["inventory"].append(r_pool_0)

                                        if p["auto"]:
                                            autoCraft(p)

                                        p["inventory"] = sorted(p["inventory"])

                                        if not message.content.split()[1] == 'fill':
                                            # Write to player file
                                            with open('./resources/battle/miner.json', 'w') as f:
                                                json.dump(contents, f, indent=4)

                                            await message.channel.send("{} found {} {}.\n{}".format(message.author.mention, r_pool_0_int, r_pool_0[1], r_pool_0[2]))

                                            unlock_mash = checkUnlock(p)
                                            if unlock_mash != 'resources/misc/empty320x320.png':
                                                await message.channel.send("{}".format(message.author.mention), file=discord.File(unlock_mash))
                                                with open('./resources/battle/miner.json', 'w') as f:
                                                    json.dump(contents, f, indent=4)

                                            # Check if player has won first
                                            if won(p):
                                                filename = str(os.path.basename(__file__))
                                                commandname = filename.replace('.py', '')
                                                msg = "{}'s inventory contains:{}".format(message.author.mention, getInv(p, True)[0])
                                                await message.channel.send(msg, file=getInv(p, True)[1])
                                                msg = "{}, you have completed **".format(message.author.mention) + prefix + "{}** miner!".format(commandname) + " :trophy: :trophy: :trophy:"
                                                msg += "\nYou can start over by typing **" + prefix + "{} restart**".format(commandname)
                                                await message.channel.send(msg)
                                                return
                                            return
                                    if message.content.split()[1] == 'fill':
                                        # Write to player file
                                        with open('./resources/battle/miner.json', 'w') as f:
                                            json.dump(contents, f, indent=4)

                                        await message.channel.send("{}, inventory has been filled.\n".format(message.author.mention) + getInv(p, True)[0], file=getInv(p, True)[1])

                                        unlock_mash = checkUnlock(p)
                                        if unlock_mash != 'resources/misc/empty320x320.png':
                                            await message.channel.send("{}".format(message.author.mention), file=discord.File(unlock_mash))
                                            with open('./resources/battle/miner.json', 'w') as f:
                                                json.dump(contents, f, indent=4)

                                        # Check if player has won first
                                        if won(p):
                                            filename = str(os.path.basename(__file__))
                                            commandname = filename.replace('.py', '')
                                            msg = "{}, you have completed **".format(message.author.mention) + prefix + "{}** miner!".format(commandname) + " :trophy: :trophy: :trophy:"
                                            msg += "\nYou can start over by typing **" + prefix + "{} restart**".format(commandname)
                                            await message.channel.send(msg)
                                            return
                                        return

                    if message.content.split()[1] == 'dump':
                        for p in contents['players']:
                            if str(message.author.id) == str(p['name']):
                                # Sort inventory
                                p["inventory"] = sorted(p["inventory"])
                                # Write to player file
                                with open('./resources/battle/miner.json', 'w') as f:
                                    json.dump(contents, f, indent=4)

                                # Start message, add getInv backpack information and inventory image
                                msg = "{}\n\nWhich items do you want to dump? *(Example: 1 3 5-10 12)*\nSay 'exit' if you want to cancel.\n\n".format(message.author.mention)
                                await message.channel.send(msg + getInv(p, True)[0], file=getInv(p, True)[1])

                                def check(msg):
                                    return msg.author == message.author
                                try:
                                    msg = await client.wait_for('message', check=check, timeout=timeout_time)
                                except asyncio.TimeoutError:
                                    await message.channel.send("{}, you've waited too long!".format(message.author.mention))
                                    return
                                else:
                                    if msg.content == 'exit':
                                        await message.channel.send("{}, you've cancelled an item dump".format(message.author.mention))
                                        return
                                    else:
                                        try:
                                            # Strip message in case someone used commas
                                            msg.content.strip(",")
                                            # Split msg into a list
                                            split = msg.content.split()
                                            # Make a list with items we can delete
                                            list_to_delete = []
                                            for to_delete in split:
                                                # If there's a dash in the received msg, read it as an integer range
                                                if '-' in to_delete:
                                                    # Split range (e.g. 5-10) into individual different characters
                                                    def split(word):
                                                        return [char for char in word]
                                                    ints = split(to_delete)
                                                    # Locate dash (51-109 and 1-8 have different dash locations)
                                                    dash_location = 0
                                                    for idx, dash in enumerate(ints):
                                                        if dash == '-':
                                                            dash_location = idx
                                                    # Concatenate string before and after the dash, and turn string into integers
                                                    def get_int(str):
                                                        string = ''
                                                        for inte in str:
                                                            string += inte
                                                        return int(string)
                                                    before_dash = ints[0:dash_location]
                                                    before_dash_int = get_int(before_dash)
                                                    after_dash = ints[dash_location+1:]
                                                    after_dash_int = get_int(after_dash)
                                                    # Put these integers into a range
                                                    # After_dash_int + 1 because range loops UNTIL final integer (NOT up to and including)
                                                    dash_range = range(before_dash_int, after_dash_int + 1)
                                                    # Append everything in between this range to the list_to_delete
                                                    # -1 so the input msg will correspond with the coded inventory locations (1-5 becomes 0-4)
                                                    for int_in_range in dash_range:
                                                        list_to_delete.append(int_in_range - 1)
                                                else:
                                                    # If there is no dash in this loop (to_delete), turn string into integer, -1 for correct inventory location, and append to list_to_delete
                                                    list_to_delete.append(int(to_delete) - 1)
                                            # Reverse list_to_delete order; so we can POP without reordering index in list
                                            list_to_delete.sort(reverse=True)
                                            # Storing the players inventory temporarily for safe deletion
                                            store_temp_inv = []
                                            for temp_item in p["inventory"]:
                                                store_temp_inv.append(temp_item)
                                            # Deleting everything in the temporary list
                                            for delete in list_to_delete:
                                                store_temp_inv.pop(delete)
                                                # If an integer has been entered that exceeds the players inventory limit
                                                if delete > getBackpackTier(p):
                                                    await message.channel.send("{}, numbers do not match with what is available in your inventory!\n"
                                                                               "You can't delete items that are not in your backpack.".format(message.author.mention))
                                                    return
                                            # Overwriting the players inventory with the temporary list and saving
                                            p["inventory"] = store_temp_inv
                                            with open('./resources/battle/miner.json', 'w') as f:
                                                json.dump(contents, f, indent=4)
                                            await message.channel.send("{}, **dump succesful!**\nYour new inventory:".format(message.author.mention) + getInv(p, True)[0], file=getInv(p, True)[1])
                                            return
                                        except ValueError:
                                            await message.channel.send("{}, something went wrong! I encountered a Value Error!\nEnter numbers like: *1 3 5-10 12*".format(message.author.mention))
                                            return
                                        except IndexError:
                                            await message.channel.send("{}, something went wrong! I encountered an Index Error!\nEnter numbers like: *1 3 5-10 12*".format(message.author.mention))
                                            return

                    if message.content.split()[1] == 'craft':
                        for p in contents['players']:
                            if str(message.author.id) == str(p['name']):
                                if p["midas"]:
                                    await message.channel.send("{}, **there's nothing left for you to craft!**\n\n*You would turn it into gold anyways...*".format(message.author.mention))
                                    return

                                unlock_mash = checkUnlock(p)
                                if unlock_mash != 'resources/misc/empty320x320.png':
                                    await message.channel.send("{}".format(message.author.mention), file=discord.File(unlock_mash))
                                    with open('./resources/battle/miner.json', 'w') as f:
                                        json.dump(contents, f, indent=4)

                                total = 0
                                unlocked = 0
                                for crafts in p["crafting"]:
                                    if crafts[3] == False:
                                        total = total + 1
                                    elif crafts[3] == True:
                                        unlocked = unlocked + 1
                                        total = total + 1
                                temp_msg = "{}, enter the **recipe's number** you'd like to craft/inspect.```css\nRecipes unlocked: {}/{}```".format(message.author.mention, unlocked, total)
                                await message.channel.send(temp_msg, file=getCrafting(p))

                                # Bool for checking value/index errors in the first response
                                first_check = True

                                def check(msg):
                                    return msg.author == message.author

                                try:
                                    msg = await client.wait_for('message', check=check, timeout=timeout_time)
                                except asyncio.TimeoutError:
                                    await message.channel.send("{}, you've waited too long!".format(message.author.mention))
                                    return
                                else:
                                    try:
                                        # Preventing from opening multiple times!
                                        if prefix in msg.content:
                                            await message.channel.send(
                                                '{}, cancelled previous action...'.format(message.author.mention, prefix))
                                            return
                                        if int(msg.content):
                                            first_check = False

                                            craft_idx = int(msg.content) - 1

                                            # Check if this number is in the ID's
                                            id_list = []
                                            for ids in p["crafting"]:
                                                if ids[0] not in id_list:
                                                    id_list.append(ids[0])
                                            if craft_idx not in id_list:
                                                await message.channel.send("{}, that number is not on the list! Try again...".format(message.author.mention))
                                                return

                                            # Checking if player has NOT unlocked this recipe
                                            if p["crafting"][craft_idx][3] == False:
                                                temp_msg = "{}, you haven't unlocked **{}** yet.\n\nTo **unlock** it, your backpack must contain:\n".format(message.author.mention, p["crafting"][craft_idx][1].capitalize())
                                                # All crafting components
                                                recipe_txt = []
                                                for components in p["crafting"][craft_idx][6]:
                                                    # Getting component name by ID
                                                    name = ''
                                                    ID = ''
                                                    for rsc in resources:
                                                        if components[0] is rsc[0]:
                                                            name = rsc[1]
                                                            ID = rsc[0]
                                                    recipe_txt.append([components[1], [ID, name]])
                                                await message.channel.send(temp_msg, file=getRecipe(p, recipe_txt))
                                                return
                                            else:
                                                # Crafting recipe cost message
                                                cost_msg = '{}, to craft **{}** you need:\n```css\n'.format(message.author.mention, p["crafting"][craft_idx][1].capitalize())

                                                # Check if player can craft this recipe
                                                can_craft = True
                                                owned_comps = []
                                                requirements = p["crafting"][craft_idx][4]

                                                for idx, req_mat in enumerate(requirements):
                                                    # Appending required material ID to owned components
                                                    owned_amount = 0
                                                    # Searching for this material ID in players inventory
                                                    for items in p["inventory"]:
                                                        # If ID matches the component ID in owned_comps, add to owned components (owned_comps)
                                                        if items[0] == req_mat[0]:
                                                            owned_amount += 1
                                                    owned_comps.append([req_mat[0], owned_amount])
                                                # owned_comps outputs [ID, Player Inventory Amount]

                                                # Checking player resources
                                                for idx, req_mat in enumerate(requirements):
                                                    # add to msg the amount of resources (component[1]) & the resource name based on the component ID (component[0])
                                                    cost_msg = cost_msg + str(owned_comps[idx][1]) + '/' + str(req_mat[1]) + ' ' + resources[req_mat[0]][1].capitalize() + '\n'
                                                    if owned_comps[idx][1] < req_mat[1]:
                                                        can_craft = False
                                                cost_msg = cost_msg + '```\n'

                                                if can_craft == False:
                                                    cost_msg = cost_msg + 'You do not have enough resources to craft **{}**.'.format(p["crafting"][craft_idx][1].capitalize())
                                                    await message.channel.send(cost_msg)
                                                    return
                                                else:
                                                    if p["fast"] and 'compressed' in p["crafting"][craft_idx][1]:
                                                        # Creating a list to match requirements
                                                        req_match_list = []
                                                        for req_mat in requirements:
                                                            for items in owned_comps:
                                                                if req_mat[0] == items[0]:
                                                                    req_match_list.append(math.floor(items[1] / req_mat[1]))
                                                        # Lowest owned required amount will be how many the player can craft
                                                        req_match_list.sort()
                                                        craft_amt = req_match_list[0]
                                                        cost_msg += 'You have a **fast crafter**.\n'
                                                        cost_msg += 'Would you like to craft ***{}*** **{}**? (Y/N)'.format(craft_amt, p["crafting"][craft_idx][1].capitalize())

                                                    else:
                                                        cost_msg = cost_msg + 'Would you like to craft **{}**? (Y/N)'.format(p["crafting"][craft_idx][1].capitalize())

                                                    await message.channel.send(cost_msg)

                                                    def check(msg):
                                                        return msg.author == message.author

                                                    try:
                                                        msg = await client.wait_for('message', check=check, timeout=timeout_time)
                                                    except asyncio.TimeoutError:
                                                        await message.channel.send("{}, you've waited too long!".format(message.author.mention))
                                                        return
                                                    else:
                                                        yes_list = ['y', 'yes', 'yea', 'yeah', 'ya']
                                                        no_list = ['n', 'no', 'nah', 'na']

                                                        if msg.content.lower() in yes_list:

                                                            if p["fast"] and 'compressed' in p["crafting"][craft_idx][1]:
                                                                # Removing elements from a list whilst iterating over them > while loop
                                                                dupe_inv = p["inventory"]
                                                                # Remove items from inv
                                                                for fast_craft in range(craft_amt):
                                                                    for req_mat in requirements:
                                                                        deleted = 0
                                                                        while deleted < req_mat[1]:
                                                                            for items in dupe_inv:
                                                                                if items[0] == req_mat[0]:
                                                                                    if deleted < req_mat[1]:
                                                                                        p["inventory"].remove(items)
                                                                                        deleted = deleted + 1
                                                                                    else:
                                                                                        break
                                                            else:
                                                                # Removing elements from a list whilst iterating over them > while loop
                                                                dupe_inv = p["inventory"]
                                                                # Remove items from inv
                                                                for req_mat in requirements:
                                                                    deleted = 0
                                                                    while deleted < req_mat[1]:
                                                                        for items in dupe_inv:
                                                                            if items[0] == req_mat[0]:
                                                                                if deleted < req_mat[1]:
                                                                                    p["inventory"].remove(items)
                                                                                    deleted = deleted + 1
                                                                                else:
                                                                                    break

                                                            craft_result = p["crafting"][craft_idx][1].capitalize()

                                                            def bool_pop_reorder(upgrade):
                                                                p[upgrade] = True
                                                                # Pop recipe
                                                                for idx, crafts in enumerate(p["crafting"]):
                                                                    if crafts[5] == p["crafting"][craft_idx][5]:
                                                                        p["crafting"].pop(idx)
                                                                # Reorder ID's
                                                                for idx, crafts in enumerate(p["crafting"]):
                                                                    crafts[0] = idx

                                                            # Check if player crafted an upgrade
                                                            if 'inventory' in p["crafting"][craft_idx][1]:
                                                                p['inventory_tier'] += 1
                                                                for idx, crafts in enumerate(p["crafting"]):
                                                                    if crafts[5] == p["crafting"][craft_idx][5]:
                                                                        p["crafting"].pop(idx)
                                                                # Reorder ID's
                                                                for idx, crafts in enumerate(p["crafting"]):
                                                                    crafts[0] = idx
                                                            elif 'fast' in p["crafting"][craft_idx][1]:
                                                                bool_pop_reorder('fast')
                                                            elif 'compressor' in p["crafting"][craft_idx][1]:
                                                                bool_pop_reorder('auto')
                                                                autoCraft(p)
                                                                p["inventory"] = sorted(p["inventory"])
                                                            elif 'lucky' in p["crafting"][craft_idx][1]:
                                                                bool_pop_reorder('lucky')
                                                            elif 'haul' in p["crafting"][craft_idx][1]:
                                                                bool_pop_reorder('haul')
                                                            elif 'miner' in p["crafting"][craft_idx][1]:
                                                                bool_pop_reorder('miner')
                                                            elif 'crown' in p["crafting"][craft_idx][1]:
                                                                p['midas'] = True
                                                                execute_midas(p)
                                                            else:
                                                                # Add crafted item to players inventory
                                                                # Check crafted item's resource id from crafting library
                                                                if p["fast"] and 'compressed' in p["crafting"][craft_idx][1]:
                                                                    for fast_craft in range(craft_amt):
                                                                        p["inventory"].append(resources[p["crafting"][craft_idx][5]])
                                                                else:
                                                                    p["inventory"].append(resources[p["crafting"][craft_idx][5]])

                                                            # Sort inv
                                                            p["inventory"] = sorted(p["inventory"])

                                                            # Save
                                                            with open('./resources/battle/miner.json', 'w') as f:
                                                                json.dump(contents, f, indent=4)

                                                            if p['midas']:
                                                                await message.channel.send(
                                                                    "{} crafted the **Midas Crown**! :trophy: :trophy: :trophy:\n*Everything has turned to gold*\n\n"
                                                                    "Inventory now contains:{}".format(message.author.mention, getInv(p, True)[0]), file=getInv(p, True)[1])
                                                            else:
                                                                await message.channel.send(
                                                                    "{} crafted **{}**.\nInventory now contains:{}".format(message.author.mention, craft_result, getInv(p, True)[0]),
                                                                    file=getInv(p, True)[1])

                                                                unlock_mash = checkUnlock(p)
                                                                if unlock_mash != 'resources/misc/empty320x320.png':
                                                                    await message.channel.send("{}".format(message.author.mention), file=discord.File(unlock_mash))
                                                                    with open('./resources/battle/miner.json', 'w') as f:
                                                                        json.dump(contents, f, indent=4)
                                                                return

                                                        elif msg.content.lower() in no_list:
                                                            await message.channel.send("{} decided *not* to craft {} for now...".format(message.author.mention,
                                                                                                                                        p["crafting"][craft_idx][1].capitalize()))
                                                            return
                                                        else:
                                                            await message.channel.send("{} I can only accept 'yes' or 'no' answers (**Y**/**N**)\nResetting...".format(message.author.mention,
                                                                                                                                                                       p["crafting"][craft_idx][
                                                                                                                                                                           1].capitalize()))
                                                            return

                                        else:
                                            await message.channel.send("{}, that number is not on the list! Try again...".format(message.author.mention))
                                            return
                                    except ValueError and first_check:
                                        await message.channel.send("{}, I need a single integer! Try again...".format(message.author.mention))
                                        return
                                    except IndexError and first_check:
                                        await message.channel.send("{}, that number is not on the list! Try again...".format(message.author.mention))
                                        return

                    else:
                        await message.channel.send(help_msg())
                        return


# Function for getting player backpack tier
# player = p from a loop: for p in contents['players']
# returns max inventory regarding tier
def getBackpackTier(player):
    if player["inventory_tier"] == 0:
        return bp_tier_0
    if player["inventory_tier"] == 1:
        return bp_tier_1
    if player["inventory_tier"] == 2:
        return bp_tier_2
    if player["inventory_tier"] == 3:
        return bp_tier_3

def autoCraft(player):
    IDs_to_craft = [0, 1, 2]  # AUTOCRAFT DIRT, STONE & IRON

    for ID_to_craft in IDs_to_craft:
        owned_comps = []
        requirements = crafting[ID_to_craft][4]
        craft_amt = 0

        for idx, req_mat in enumerate(requirements):
            # Appending required material ID to owned components
            owned_amount = 0
            # Searching for this material ID in players inventory
            for items in player["inventory"]:
                # If ID matches the component ID in owned_comps, add to owned components (owned_comps)
                if items[0] == req_mat[0]:
                    owned_amount += 1
            owned_comps.append([req_mat[0], owned_amount])
        # owned_comps outputs [ID, Player Inventory Amount]

        for req_mats in requirements:
            # Creating a list to match requirements
            req_match_list = []
            for req_mat in requirements:
                for items in owned_comps:
                    if req_mat[0] == items[0]:
                        req_match_list.append(math.floor(items[1] / req_mat[1]))
            # Lowest owned required amount will be how many the player can craft
            req_match_list.sort()
            craft_amt = req_match_list[0]

        # Removing elements from a list whilst iterating over them > while loop
        dupe_inv = player["inventory"]
        # Remove items from inv
        for auto_craft in range(craft_amt):
            for req_mat in requirements:
                deleted = 0
                while deleted < req_mat[1]:
                    for items in dupe_inv:
                        if items[0] == req_mat[0]:
                            if deleted < req_mat[1]:
                                player["inventory"].remove(items)
                                deleted = deleted + 1
                            else:
                                break

        for auto_craft in range(craft_amt):
            player["inventory"].append(resources[crafting[ID_to_craft][5]])

    return



# Returns unlocked recipes

# So that the unlock will be written on the save file, use as follows:
# for unlock in checkUnlock(p):
#   await message.channel.send("{}".format(message.author.mention), file=discord.File("resources/misc/unlockID{}.png".format(unlock[0])))
#   with open('./resources/battle/miner.json', 'w') as f:
#       json.dump(contents, f, indent=4)
def checkUnlock(player):
    p_inv = player["inventory"]
    p_craft = player["crafting"]
    unlocked_something = False
    things_unlocked = []

    for idx, craft in enumerate(p_craft):
        # boolean > player unlocked recipe
        got_recipe = craft[3]
        # recipe requirements
        recipe_rqds = craft[6]

        if not got_recipe:
            # list with material ID's in this recipe + booleans to check in player's inventory
            id_bool_list = []
            for mat_and_amt in recipe_rqds:
                for amount in range(mat_and_amt[1]):
                    id_bool_list.append([mat_and_amt[0], False])

            # for every material in the players inventory
            # check if a material matches ID with the id_bool_list
            # If this material is False in the id_bool_list, set it to True
            for p_mat in p_inv:
                for mat_and_amt in id_bool_list:
                    # got_material = mat_and_amt[1]
                    if not mat_and_amt[1]:
                        mat_ID = mat_and_amt[0]
                        if mat_ID is p_mat[0]:
                            mat_and_amt[1] = True
                            break

            # amount of materials matching in the players inventory
            mats_got = 0
            for req in id_bool_list:
                if req[1]:
                    mats_got += 1
                if mats_got >= len(id_bool_list):
                    things_unlocked.append(craft)
                    craft[3] = True
                    unlocked_something = True

    print(things_unlocked)

    if unlocked_something:
        for unlock in things_unlocked:
            img_bg = Image.open('resources/misc/320x320unlock.png')

            img_temp = Image.open(unlock[2])
            # Nearest Neighbor for crisp pixel-art
            img_temp = img_temp.resize((64, 64), Image.NEAREST)
            img_bg.paste(img_temp, (128, 128), img_temp)
            # Name drawing
            str_name = ' ' + unlock[1].capitalize()
            ImageDraw.Draw(img_bg).text((161, 251), str_name, (0, 0, 0), font=shadow_font_big, anchor="mm")
            ImageDraw.Draw(img_bg).text((160, 250), str_name, (255, 255, 255), font=font_big, anchor="mm")

            img_bg.save("resources/misc/unlockID{}.png".format(unlock[0]))

        if len(things_unlocked) == 1:
            for unlock in things_unlocked:
                img_bg = Image.open("resources/misc/unlockID{}.png".format(unlock[0]))
                return "resources/misc/unlockID{}.png".format(unlock[0])
        elif len(things_unlocked) == 2:
            img_bg = Image.open('resources/misc/empty640x320.png')
            unlock_img_square_size = 320
            for idx, unlock in enumerate(things_unlocked):
                size = unlock_img_square_size
                img_temp = Image.open("resources/misc/unlockID{}.png".format(unlock[0]))
                img_bg.paste(img_temp, (size * idx, 0), img_temp)
            img_bg.save("resources/misc/temp/m_temp_mashup_2_{}.png".format(player['name_at_save']))
            return "resources/misc/temp/m_temp_mashup_2_{}.png".format(player['name_at_save'])
        elif len(things_unlocked) == 3 or len(things_unlocked) == 4:
            img_bg = Image.open('resources/misc/empty640x640.png')
            unlock_img_square_size = 320
            for idx, unlock in enumerate(things_unlocked):
                size = unlock_img_square_size
                img_temp = Image.open("resources/misc/unlockID{}.png".format(unlock[0]))
                if idx == 0 or idx == 1:
                    img_bg.paste(img_temp, (size * idx, 0), img_temp)
                elif idx == 2:
                    img_bg.paste(img_temp, (0, 320), img_temp)
                elif idx == 3:
                    img_bg.paste(img_temp, (320, 320), img_temp)
            img_bg.save("resources/misc/temp/m_temp_mashup_4_{}.png".format(player['name_at_save']))
            return "resources/misc/temp/m_temp_mashup_4_{}.png".format(player['name_at_save'])
        elif len(things_unlocked) == 5 or len(things_unlocked) == 6:
            img_bg = Image.open('resources/misc/empty640x960.png')
            unlock_img_square_size = 320
            for idx, unlock in enumerate(things_unlocked):
                size = unlock_img_square_size
                img_temp = Image.open("resources/misc/unlockID{}.png".format(unlock[0]))
                if idx == 0 or idx == 1:
                    img_bg.paste(img_temp, (size * idx, 0), img_temp)
                elif idx == 2:
                    img_bg.paste(img_temp, (0, size), img_temp)
                elif idx == 3:
                    img_bg.paste(img_temp, (size, size), img_temp)
                elif idx == 4:
                    img_bg.paste(img_temp, (0, size * 2), img_temp)
                elif idx == 5:
                    img_bg.paste(img_temp, (size, size * 2), img_temp)
                else:
                    img_bg.paste(img_temp, (0, size * 3), img_temp)
            img_bg.save("resources/misc/temp/m_temp_mashup_5_{}.png".format(player['name_at_save']))
            return "resources/misc/temp/m_temp_mashup_5_{}.png".format(player['name_at_save'])
        elif len(things_unlocked) >= 7:
            img_bg = Image.open('resources/misc/empty960x960.png')
            unlock_img_square_size = 320
            for idx, unlock in enumerate(things_unlocked):
                size = unlock_img_square_size
                img_temp = Image.open("resources/misc/unlockID{}.png".format(unlock[0]))
                if idx == 0 or idx == 1 or idx == 2:
                    img_bg.paste(img_temp, (size * idx, 0), img_temp)
                elif idx == 3:
                    img_bg.paste(img_temp, (0, size), img_temp)
                elif idx == 4:
                    img_bg.paste(img_temp, (size, size), img_temp)
                elif idx == 5:
                    img_bg.paste(img_temp, (size * 2, size), img_temp)
                elif idx == 6:
                    img_bg.paste(img_temp, (0, size * 2), img_temp)
                elif idx == 7:
                    img_bg.paste(img_temp, (size, size * 2), img_temp)
                elif idx == 8:
                    img_bg.paste(img_temp, (size * 2, size * 2), img_temp)
                else:
                    img_bg.paste(img_temp, (size * 3, size * 3), img_temp)
            img_bg.save("resources/misc/temp/m_temp_mashup_5_{}.png".format(player['name_at_save']))
            return "resources/misc/temp/m_temp_mashup_5_{}.png".format(player['name_at_save'])

    else:
        return 'resources/misc/empty320x320.png'

def won(player):
    if len(player["inventory"]) >= bp_tier_3 and player["midas"]:
        return True
    else:
        return False

def execute_midas(player):
    for idx, item in enumerate(player["inventory"]):
        # Turns everything into gold
        player["inventory"][idx] = resources[6]

def getCrafting(player):
    # amount of pixels per item in image
    px_per_item = 64
    px_per_craftable = 32

    px_times_width = 15
    px_times_height = 15

    img_bg = Image.open('resources/misc/empty384x640.png')
    divided_space = len(crafting) / 2
    add_width = 0
    add = 1
    other_side = False

    iterated = 0
    img_temp = None

    # Loop through all empty spaces in table
    for x in range(px_times_height):
        for y in range(px_times_width):
            for idx, crafts in enumerate(player["crafting"]):
                if idx == iterated:
                    if other_side:
                        y -= idx - add
                        add += 1
                    if idx >= divided_space and add_width == 0:
                        add_width += 320
                        y = 0
                        other_side = True
                    locked = ''
                    if crafts[3] == False:
                        img_temp = Image.open(sprites[0][2])
                        locked = ' (LOCKED)'
                    elif crafts[3] == True:
                        img_temp = Image.open(crafts[2])
                        locked = ''
                        # Nearest Neighbor for crisp pixel-art
                        img_temp = img_temp.resize((64, 64), Image.NEAREST)
                    img_bg.paste(img_temp, (x * px_per_item + add_width, y * px_per_item), img_temp)
                    # Numbering
                    str_iter = str(iterated + 1) + ' '
                    posX = x * px_per_item + add_width
                    posX_s = x * px_per_item + shadow_offset + add_width
                    posY = y * px_per_item
                    posY_s = y * px_per_item + shadow_offset
                    ImageDraw.Draw(img_bg).text((posX_s, posY_s), str_iter, (0, 0, 0), font=shadow_font)
                    ImageDraw.Draw(img_bg).text((posX, posY), str_iter, (255, 255, 255), font=font)
                    # Name drawing
                    str_name = ' ' + crafts[1].capitalize() + locked
                    ImageDraw.Draw(img_bg).text((posX_s + px_per_item, posY_s + (px_per_item / 2)), str_name, (0, 0, 0), font=shadow_font, anchor="lm")
                    ImageDraw.Draw(img_bg).text((posX + px_per_item, posY + (px_per_item / 2)), str_name, (255, 255, 255), font=font, anchor="lm")

                    iterated = iterated + 1

                    break

    img_bg.save("resources/misc/temp/m_temp_{}.png".format(player["name_at_save"]))

    return discord.File("resources/misc/temp/m_temp_{}.png".format(player["name_at_save"]))

# player = p
# recipe_txt =      [how many of the following material required for crafting, [ID, name]]
# recipe_txt can be multiple: [[2, [1, 'compressed dirt']], [3, [2, 'stone']]]
def getRecipe(player, recipe_txt):
    # amount of pixels per item in image
    px_per_item = 64
    px_per_craftable = 32

    px_times_width = 15
    px_times_height = 15

    img_bg = Image.open('resources/misc/empty320x320.png')

    iterated = 0
    img_temp = None

    # Materials required for crafting final IMG list
    # Has material: AMT, NAME, IMAGE
    final_list = []
    for recipe in recipe_txt:
        AMT = recipe[0]
        ID = recipe[1][0]
        NAME = recipe[1][1]
        for rsc in resources:
            if ID is rsc[0]:
                final_list.append([AMT, NAME, rsc[5]])

    # Loop through all empty spaces in table
    for x in range(px_times_height):
        for y in range(px_times_width):
            for idx, amt_name_img in enumerate(final_list):
                if idx == iterated:
                    img_temp = Image.open(amt_name_img[2])
                    # Nearest Neighbor for crisp pixel-art
                    img_temp = img_temp.resize((64, 64), Image.NEAREST)
                    img_bg.paste(img_temp, (x * px_per_item, y * px_per_item), img_temp)
                    # Amount of materials required
                    str_iter = str(amt_name_img[0]) + 'x '
                    posX = x * px_per_item
                    posX_s = x * px_per_item + shadow_offset
                    posY = y * px_per_item
                    posY_s = y * px_per_item + shadow_offset
                    # Name drawing
                    str_name = ' ' + amt_name_img[1].capitalize()
                    ImageDraw.Draw(img_bg).text((posX_s + px_per_item + 5, posY_s + (px_per_item / 2)), str_iter + str_name, (0, 0, 0), font=shadow_font_big, anchor="lm")
                    ImageDraw.Draw(img_bg).text((posX + px_per_item + 5, posY + (px_per_item / 2)), str_iter + str_name, (255, 255, 255), font=font_big, anchor="lm")

                    iterated = iterated + 1

                    break

    img_bg.save("resources/misc/temp/m_temp_{}.png".format(player["name_at_save"]))

    return discord.File("resources/misc/temp/m_temp_{}.png".format(player["name_at_save"]))

# Function for getting player inventory
# player = p from a loop: for p in contents['players']
# allow_msg = True for backpack message and picture, False for data requests
# returns array[]
# 0=discord.file(image), 1=dirt, 2=stone, 3=iron, 4=gold
def getInv(player, allow_msg):
    # amount of pixels per item in image
    px_per_item = 32

    if player["inventory_tier"] == 0:
        # Empty png image
        img_bg = Image.open('resources/misc/empty320x64.png')
        # px_per_item multiplier > width of img_bg
        px_times_width = 10
        # px_per_item multiplier > height of img_bg
        px_times_height = 2
    elif player["inventory_tier"] == 1:
        img_bg = Image.open('resources/misc/empty320x160.png')
        px_times_width = 10
        px_times_height = 5
    elif player["inventory_tier"] == 2:
        img_bg = Image.open('resources/misc/empty320x320.png')
        px_times_width = 10
        px_times_height = 10
    elif player["inventory_tier"] == 3:
        img_bg = Image.open('resources/misc/empty480x480.png')
        px_times_width = 15
        px_times_height = 15
    else:
        img_bg = Image.open('resources/misc/empty480x480.png')
        px_times_width = 15
        px_times_height = 15

    # end message
    msg = ""

    iterated = 0

    # !IMPORTANT: This function executes twice.
    # Once for the information, twice for the IMG request;
    # Img request still executes the same code, but returns the IMG generating side of this function.

    # calculate how many items of each materials player has
    items_in_inv_count_list = []
    first_item = True

    for items in player["inventory"]:
        if first_item:
            # Adding the first item to the list, so we can loop over the list
            items_in_inv_count_list.append([items, 1])
            first_item = False
        else:
            for idx, item_count in enumerate(items_in_inv_count_list):
                # if item ID does not match
                if items[0] is not item_count[0][0]:
                    if idx >= len(items_in_inv_count_list) - 1:
                        items_in_inv_count_list.append([items, 1])
                        # Idx has exceeded the items_in_inv_count_list, so the item is added (it wasn't found)
                        # There is now 1 of this item in the players inventory [item data, item count]
                        break
                elif items[0] is item_count[0][0]:
                    # If string name is the same, add one to the item count
                    if item_count[0][1] == items[1]:
                        item_count[1] += 1
                        break

    msg = "\n```css\n.Backpack {}/{}\n\n".format(len(player["inventory"]), getBackpackTier(player))

    # Counting items
    for rsc in resources:
        for item in items_in_inv_count_list:
            # If resource ID matches items_in_inv_count_list item ID
            if rsc[0] is item[0][0]:
                # Appending material name and material count to the message. Example Dirt: 3\n
                msg += "{}: {}\n".format(rsc[1].capitalize(), item[1])
                # Can grab either rsc[?] or item[0][?] data. rsc[] is from this script, item[] is from save file.

    # Loop through all empty spaces in table
    for y in range(px_times_height):
        for x in range(px_times_width):
            for idx in range(len(player['inventory'])):
                if iterated == idx:
                    img_temp = Image.open(player['inventory'][idx][5])
                    img_temp = img_temp.resize((px_per_item, px_per_item))

                    img_bg.paste(img_temp, (x * px_per_item, y * px_per_item), img_temp)

                    str_iter = str(iterated + 1) + ' '

                    # number all iterations in pic
                    ImageDraw.Draw(img_bg).text((x * px_per_item + shadow_offset, y * px_per_item + shadow_offset), str_iter, (0, 0, 0), font=shadow_font)
                    ImageDraw.Draw(img_bg).text((x * px_per_item, y * px_per_item), str_iter, (255, 255, 255), font=font)

                    iterated = iterated + 1
                    break

    msg += "```"

    img_bg.save("resources/misc/temp/m_temp_{}.png".format(player["name_at_save"]))

    if allow_msg:
        return [msg, discord.File("resources/misc/temp/m_temp_{}.png".format(player["name_at_save"]))]
    else:
        return items_in_inv_count_list

