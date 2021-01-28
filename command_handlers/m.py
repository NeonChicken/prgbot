import random
import discord
import asyncio
from PIL import Image, ImageFont, ImageDraw, ImageOps
import json
import os
import io
import datetime

# MINE SIM

prefix = '!'

wait_time = 0.5
timeout_time = 20

# items per backpack tier
bp_tier_0 = 10
bp_tier_1 = 50
bp_tier_2 = 100
bp_tier_3 = 225

# Player data
data = {}
data['players'] = []

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
font = ImageFont.truetype("courbd.ttf", 12)
shadow_font = ImageFont.truetype("courbd.ttf", 12)
# amount of pixels to offset shadow in text
shadow_offset = 2

# Mine data
# 0=ID,  1=Name, 2=Description, 3=min_amount, 4=max_amount, 5=image
resources = [
    [0, "dirt", "It's dirty.", 2, 7, "resources/items/miner/dirt.png"],
    [1, "compressed dirt", "Tightly packed dirt", 0, 0, "resources/items/miner/dirt_comp.png"],
    [2, "stone", "Some very dull looking stone...", 1, 5, "resources/items/miner/stone.png"],
    [3, "compressed stone", "Tightly packed stone", 0, 0, "resources/items/miner/stone_comp.png"],
    [4, "iron", "*Very* useful!", 1, 2, "resources/items/miner/iron.png"],
    [5, "compressed iron", "Very heavy.", 0, 0, "resources/items/miner/iron_comp.png"],
    [6, "gold", "*Shiny!*", 1, 1, "resources/items/miner/gold.png"]
]

# Sprite data
# 0=ID, 1=Name, 2=image
sprites = [
    [0, "lock", "resources/items/miner/lock64.png"]
]

# Crafting data
# 0=ID, 1=Name, 2=image, 3=unlocked, 4=recipe[[resource id, amount], [resource id, amount]], 5=resource ID, 6=research_requirement[[resource id, amount]]
crafting = [
    [0, "compressed dirt", "resources/items/miner/dirt_comp.png", False, [[0, 5]], 1, [[0, 7]]],
    [1, "compressed stone", "resources/items/miner/stone_comp.png", False, [[2, 5], [0, 1]], 3, [[1, 3], [2, 3]]],
    [2, "compressed iron", "resources/items/miner/iron_comp.png", False, [[4, 5]], 5, [[3, 3], [4, 3]]]
]

# First pool with selected items from resources * rarity/10000
pool_0 = [
    [resources[0]] * 5000 +
    [resources[2]] * 3500 +
    [resources[4]] * 1499 +
    [resources[6]] * 1
]

# Mining Simulator
async def run(client, message):
    # help message
    def help_msg():
        filename = str(os.path.basename(__file__))
        commandname = filename.replace('.py', '')
        response = "{}, welcome to **".format(message.author.mention) + prefix +\
                   "{}** ".format(commandname) + "miner!\n\nAfter **" + prefix + "{}** ".format(commandname) + "you can use:" \
                                                                                                                "\n**mine** - Mine something" \
                                                                                                                "\n**inv** - See inventory" \
                                                                                                                "\n**craft** - Craft something"
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
                        do_not_create_save = 1
                        # print("Found {}".format(message.author) + " in players!")
                        # Found message.author in player file!
                    elif str(message.author.id) is not str(p['name']) and do_not_create_save is not 1:
                        if count is int(len(contents['players'])):
                            contents['players'].append({'name': '{}'.format(message.author.id),
                                                        'name_at_save': '{}'.format(message.author.name),
                                                        'total_times_mined': 0,
                                                        'inventory_tier': 0,
                                                        'pick_tier': 0,
                                                        'inventory': [],
                                                        'crafting': crafting,
                                                        'research': []
                                                        })
                            with open('./resources/battle/miner.json', 'w') as f:
                                json.dump(contents, f, indent=4)
                            await message.channel.send('*Created a save file for {}.*'.format(message.author))
                    count = count + 1

                # Help msg and testing space
                if len(message.content.split()) < 2:
                    await message.channel.send(help_msg())

                # Game logic
                elif len(message.content.split()) >= 2:
                    if message.content.split()[1] == 'inv':
                        for p in contents['players']:
                            if str(message.author.id) == str(p['name']):
                                # Sort inventory
                                p["inventory"] = sorted(p["inventory"])
                                # Write to player file
                                with open('./resources/battle/miner.json', 'w') as f:
                                    json.dump(contents, f, indent=4)
                                await message.channel.send("{}'s inventory contains:{}".format(message.author.mention, getInv(p)[0]), file=getInv(p)[1])
                                return

                    if message.content.split()[1] == 'mine':
                        for p in contents['players']:
                            if str(message.author.id) == str(p['name']):
                                # Check if inventory is full first
                                if len(p["inventory"]) >= getBackpackTier(p):
                                    await message.channel.send("{}, your inventory is full! *({}/{} items)*\nConsider **upgrading your backpack**.".format(message.author.mention, len(p["inventory"]), getBackpackTier(p)))
                                    return
                                else:
                                    # Generate random item from pool 0
                                    r_pool_0 = random.choice(pool_0[0])
                                    print(r_pool_0)
                                    # Generate random amount of that item in the min-max range
                                    r_pool_0_int = random.randrange(r_pool_0[3], r_pool_0[4])
                                    # If generated amount will overencumber player, retract amount
                                    if (r_pool_0_int + len(p["inventory"])) >= getBackpackTier(p):
                                        r_pool_0_int = getBackpackTier(p) - len(p["inventory"])
                                    # Add to total of times mined
                                    p["total_times_mined"] = p["total_times_mined"] + 1
                                    # Append generated item to inventory * random int min>max from item
                                    for unused in range(r_pool_0_int):
                                        p["inventory"].append(r_pool_0)
                                    # Write to player file
                                    with open('./resources/battle/miner.json', 'w') as f:
                                        json.dump(contents, f, indent=4)

                                    await message.channel.send("{} found {} {}.\n{}".format(message.author.mention, r_pool_0_int, r_pool_0[1], r_pool_0[2]))
                                    return

                    if message.content.split()[1] == 'craft':
                        for p in contents['players']:
                            if str(message.author.id) == str(p['name']):
                                total = 0
                                unlocked = 0
                                for crafts in p["crafting"]:
                                    if crafts[3] == False:
                                        total = total + 1
                                    elif crafts[3] == True:
                                        unlocked = unlocked + 1
                                        total = total + 1
                                temp_msg = "{}, enter the **recipe's number** you'd like to inspect (*craft/unlock*).```css\nRecipes unlocked: {}/{}```".format(message.author.mention, unlocked, total)
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
                                            await message.channel.send('{}, please try again **without** the prefix: **{}**\n*(And please do not try running multiple commands at once...)*'.format(message.author.mention, prefix))
                                            return
                                        if int(msg.content):
                                            first_check = False

                                            craft_idx = int(msg.content) - 1

                                            # Check if this number is in the ID's
                                            id_list = []
                                            for ids in crafting:
                                                if ids[0] not in id_list:
                                                    id_list.append(ids[0])
                                            if craft_idx not in id_list:
                                                await message.channel.send("{}, that number is not on the list! Try again...".format(message.author.mention))
                                                return

                                            # Checking if player has NOT unlocked this recipe
                                            if p["crafting"][craft_idx][3] == False:
                                                
                                                # todo Would you like to research this recipe?
                                                pass
                                            else:
                                                # Crafting recipe cost message
                                                cost_msg = '{}, for **{}** you have:\n```css\n'.format(message.author.mention, crafting[craft_idx][1].capitalize())

                                                # Check if player can craft this recipe
                                                can_craft = True
                                                owned_comps = []
                                                owned_amounts = []
                                                for idx, component in enumerate(crafting[craft_idx][4]):
                                                    owned_amount = 0
                                                    for items in p["inventory"]:
                                                        # If ID matches crafting ID, add to owned components (owned_comps)
                                                        if items[0] == component[0]:
                                                            if items not in owned_comps:
                                                                owned_comps.append(items)
                                                                owned_amount = owned_amount + 1
                                                                owned_amounts.append(owned_amount)
                                                            elif items in owned_comps:
                                                                owned_amount = owned_amount + 1
                                                                owned_amounts[idx] = owned_amount

                                                # Checking player resources
                                                for idx, component in enumerate(crafting[craft_idx][4]):
                                                    # add to msg the amount of resource (component[1]) & the resource name from the componnent ID (component[0])
                                                    cost_msg = cost_msg + str(owned_amounts[idx]) + '/' + str(component[1]) + ' ' + resources[component[0]][1].capitalize() + '\n'
                                                    if owned_amounts[idx] < component[1]:
                                                        can_craft = False
                                                cost_msg = cost_msg + '```\n'
                                                if can_craft == False:
                                                    cost_msg = cost_msg + 'You do not have enough resources to craft **{}**.'.format(crafting[craft_idx][1].capitalize())
                                                    await message.channel.send(cost_msg)
                                                    return
                                                else:
                                                    cost_msg = cost_msg + 'Would you like to craft **{}**? (Y/N)'.format(crafting[craft_idx][1].capitalize())
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

                                                            # Removing elements from a list whilst iterating over them calls for a while loop
                                                            dupe_inv = p["inventory"]
                                                            # Remove items from inv
                                                            for component in crafting[craft_idx][4]:
                                                                deleted = 0
                                                                while deleted < component[1]:
                                                                    for items in dupe_inv:
                                                                        if items[0] == component[0]:
                                                                            if deleted < component[1]:
                                                                                p["inventory"].remove(items)
                                                                                deleted = deleted + 1
                                                                            else:
                                                                                break
                                                            # Check crafted item's resource id from crafting library
                                                            p["inventory"].append(resources[crafting[craft_idx][5]])
                                                            # Sort inv
                                                            p["inventory"] = sorted(p["inventory"])
                                                            with open('./resources/battle/miner.json', 'w') as f:
                                                               json.dump(contents, f, indent=4)
                                                            await message.channel.send("{} crafted **{}**.\nInventory now contains:{}".format(message.author.mention, crafting[craft_idx][1].capitalize(), getInv(p)[0]), file=getInv(p)[1])
                                                            return
                                                        elif msg.content.lower() in no_list:
                                                            await message.channel.send("{} decided *not* to craft {} for now...".format(message.author.mention, crafting[craft_idx][1].capitalize()))
                                                            return
                                                        else:
                                                            await message.channel.send("{} I can only accept 'yes' or 'no' answers (**Y**/**N**)\nResetting...".format(message.author.mention, crafting[craft_idx][1].capitalize()))
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

def getCrafting(player):
    # amount of pixels per item in image
    px_per_item = 64
    px_per_craftable = 32

    px_times_width = 15
    px_times_height = 15

    img_bg = Image.open('resources/misc/empty320x320.png')

    iterated = 0
    img_temp = None

    # Loop through all empty spaces in table
    for x in range(px_times_height):
        for y in range(px_times_width):
            for idx, crafts in enumerate(player["crafting"]):
                if idx == iterated:
                    locked = ''
                    if crafts[3] == False:
                        img_temp = Image.open(sprites[0][2])
                        locked = ' (LOCKED)'
                    elif crafts[3] == True:
                        img_temp = Image.open(crafts[2])
                        locked = ''
                        # Nearest Neighbor for crisp pixel-art
                        img_temp = img_temp.resize((64,64), Image.NEAREST)
                    img_bg.paste(img_temp, (x * px_per_item, y * px_per_item), img_temp)
                    # Numbering
                    str_iter = str(iterated + 1) + ' '
                    posX = x * px_per_item
                    posX_s = x * px_per_item + shadow_offset
                    posY = y * px_per_item
                    posY_s = y * px_per_item + shadow_offset
                    ImageDraw.Draw(img_bg).text((posX_s, posY_s), str_iter, (0, 0, 0), font=shadow_font)
                    ImageDraw.Draw(img_bg).text((posX, posY), str_iter, (255, 255, 255), font=font)
                    # Name drawing
                    str_name = ' ' + crafts[1].capitalize() + locked
                    ImageDraw.Draw(img_bg).text((posX_s + px_per_item, posY_s + (px_per_item/2)), str_name, (0, 0, 0), font=shadow_font, anchor="lm")
                    ImageDraw.Draw(img_bg).text((posX + px_per_item, posY + (px_per_item/2)), str_name, (255, 255, 255), font=font, anchor="lm")

                    iterated = iterated + 1

                    break

    img_bg.save("resources/misc/temp2.png")

    return discord.File("resources/misc/temp2.png")

# Function for getting player inventory
# player = p from a loop: for p in contents['players']
# returns array[]
# 0=discord.file(image), 1=dirt, 2=stone, 3=iron, 4=gold
def getInv(player):
    # amount of pixels per item in image
    px_per_item = 32

    if player["inventory_tier"] == 0:
        # px_per_item multiplier > width of img_bg
        px_times_width = 10
        # px_per_item multiplier > height of img_bg
        px_times_height = 1
        # Empty png image
        img_bg = Image.open('resources/misc/empty320x32.png')
    elif player["inventory_tier"] == 1:
        px_times_width = 15
        px_times_height = 15
        img_bg = Image.open('resources/misc/empty320x160.png')
    elif player["inventory_tier"] == 2:
        px_times_width = 15
        px_times_height = 15
        img_bg = Image.open('resources/misc/empty320x320.png')
    elif player["inventory_tier"] == 3:
        px_times_width = 15
        px_times_height = 15
        img_bg = Image.open('resources/misc/empty480x480.png')
    else:
        px_times_width = 15
        px_times_height = 15
        img_bg = Image.open('resources/misc/empty480x480.png')

    # end message
    msg = ""

    iterated = 0

    p_dirt = 0
    p_stone = 0
    p_iron = 0
    p_gold = 0

    # Counting items
    for items in player["inventory"]:
        if items[1] == "dirt":
            p_dirt = p_dirt + 1
        if items[1] == "stone":
            p_stone = p_stone + 1
        if items[1] == "iron":
            p_iron = p_iron + 1
        if items[1] == "gold":
            p_gold = p_gold + 1

    msg = "\n```css\n.Backpack {}/{}\n\nDirt: {}\nStone: {}\nIron: {}\nGold: {}```".format(len(player["inventory"]), getBackpackTier(player), p_dirt, p_stone, p_iron, p_gold)

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

    img_bg.save("resources/misc/temp2.png")

    return [msg, discord.File("resources/misc/temp2.png")]