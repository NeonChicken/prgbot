import random
import asyncio
import os

timeout_time = 30.0  # message.author response time in seconds

width_gp = 6  # minimum of 3 recommended
length_gp = 3  # minimum of 3 recommended
max_money_per_room = 5  # has to be less than (width*length) - (player + monsters + max_items_per_room)
max_items_per_room = 1  # see above
char_player = 'O'  # character to identify player character
char_item = 'I'  # character to identify items
char_money = '.'  # character to identify money
char_monster = 'x'  # character to identify monster
movement_msg = "{}, move **left**/**right**/**up**/**down** or **W**/**A**/**S**/**D**, **refresh** or **stop**"

# todo delete previous message and send new so screen always stays @ bottom

# Flip a coin and send the result.
async def run(client, message):
    filename = str(os.path.basename(__file__))
    commandname = filename.replace('.py', '')

    if len(message.content.split()) < 2:

        # generate the grid
        # GAME OBJECTS > IDENTIFY IN GRID: 1 = player, 2 = item, 3 = money, 4 = monster
        grid = []
        for y in range(length_gp):
            new_row = []
            for x in range(width_gp):
                new_row.append(0)
            grid.append(new_row)
        grid[0][0] = 1  # player start in upper left corner.
        # generate the item
        gen_monster = False
        r_money_generated = 0
        r_item_generated = 0
        while not gen_monster:
            for y in range(length_gp):
                for x in range(width_gp):
                    r_int = random.randrange(0, 100)  # max range must be more than its game object value
                    r_money = random.randrange(0, 50)
                    r_item = random.randrange(0, 150)

                    # grid[y][x] == 0, only generate in empty spaces
                    if r_money == 3 and grid[y][x] == 0 and r_money_generated < max_money_per_room:
                        grid[y][x] = 3
                        r_money_generated = r_money_generated + 1
                    if r_item == 2 and grid[y][x] == 0 and r_item_generated < max_items_per_room:
                        grid[y][x] = 2
                        r_item_generated = r_item_generated + 1
                    if r_int == 4 and grid[y][x] == 0:
                        grid[y][x] = 4
                        gen_monster = True
                        break
                else:
                    continue
                break

        # generate discord message string
        def gen_string(grid_input):

            string = '```\n'
            # TOP
            string = string + "+" + ('-' * width_gp) + "+\n"

            # MIDDLE
            lines_generated = 0
            for y in range(length_gp):
                if lines_generated < length_gp:
                    row_str = ''
                    for i in grid_input[y]:
                        if i == 1:
                            row_str = row_str + char_player
                        elif i == 2:
                            row_str = row_str + char_item
                        elif i == 3:
                            row_str = row_str + char_money
                        elif i == 4:
                            row_str = row_str + char_monster
                        else:
                            row_str = row_str + ' '
                    string = string + "|" + row_str + "|\n"
                    lines_generated = lines_generated + 1

            # BOTTOM
            string = string + "+" + ('-' * width_gp) + "+\n"
            string = string + "```"

            print(grid)
            return string

        map_msg = await message.channel.send((gen_string(grid) + movement_msg))

        # When player has collided with a value in the grid, check some values. Otherwise return the current grid
        # This function gets executed !in! the await msg.edit statement, whenever the player moves
        def edit_msg_on_collision(value):
            if value == 2:
                return gen_string(grid) + "{} found an item!".format(message.author.mention)
            elif value == 3:
                return gen_string(grid) + "{} picked up some money!".format(message.author.mention)
            elif value == 4:
                return gen_string(grid) + "{} encountered a monster!".format(message.author.mention)
            else:
                return gen_string(grid)

        # Checks if the adjacent values on the grid are items, monsters etc and returns their respective values.
        def check_pickup(direction):
            for y in range(length_gp):
                for x in range(width_gp):
                    if grid[y][x] == 1:
                        def adjacent_value_checker(game_object):
                            if grid[y][0] != 1 and grid[y][x - 1] == game_object and direction == 'left':
                                print("Player picked up {}".format(game_object))
                                return game_object
                            elif grid[0][x] != 1 and grid[y - 1][x] == game_object and direction == 'up':
                                print("Player picked up {}".format(game_object))
                                return game_object
                            try:
                                if grid[y][x + 1] == game_object and direction == 'right':
                                    print("Player picked up {}".format(game_object))
                                    return game_object
                                elif grid[y + 1][x] == game_object and direction == 'down':
                                    print("Player picked up {}".format(game_object))
                                    return game_object
                            except Exception:
                                pass

                        # Return for every existent game object
                        if adjacent_value_checker(2) == 2:
                            return 2
                        if adjacent_value_checker(3) == 3:
                            return 3
                        if adjacent_value_checker(4) == 4:
                            return 4

        stop = 0
        while stop is not 1:
            def check(msg):
                return msg.author == message.author

            try:
                msg = await client.wait_for('message', check=check, timeout=timeout_time)
            except asyncio.TimeoutError:
                await map_msg.edit(content=gen_string(grid) + "{} waited too long!".format(message.author.mention))
                stop = 1
                return
            else:
                if msg.content.lower() == 'refresh':
                    map_msg = await message.channel.send((gen_string(grid)))
                elif msg.content.lower() == 'quit' or msg.content.lower() == 'stop':
                    await map_msg.edit(content=gen_string(grid) + "{} quit the game!".format(message.author.mention))
                    stop = 1
                    return
                elif msg.content.lower() == 'right' or msg.content.lower() == 'd':
                    for y in range(length_gp):
                        for x in range(width_gp):
                            if grid[y][x] == 1:
                                check_pickup_value = check_pickup('right')
                                grid[y][x] = 0
                                try:
                                    grid[y][x + 1] = 1
                                    await map_msg.edit(content=edit_msg_on_collision(check_pickup_value))
                                except Exception:
                                    grid[y][x] = 1
                                    await map_msg.edit(content=gen_string(grid) + "{} can't move any further!".format(
                                        message.author.mention))
                                break
                elif msg.content.lower() == 'left' or msg.content.lower() == 'a':
                    for y in range(length_gp):
                        for x in range(width_gp):
                            if grid[y][x] == 1:
                                if grid[y][0] == 1:
                                    grid[y][x] = 1
                                    await map_msg.edit(content=gen_string(grid) + "{} can't move any further!".format(
                                        message.author.mention))
                                else:
                                    check_pickup_value = check_pickup('left')
                                    grid[y][x] = 0
                                    grid[y][x - 1] = 1
                                    await map_msg.edit(content=edit_msg_on_collision(check_pickup_value))
                                break
                elif msg.content.lower() == 'down' or msg.content.lower() == 's':
                    # Boolean for when player has moved to prevent looping
                    moved = False
                    for y in range(length_gp):
                        for x in range(width_gp):
                            if grid[y][x] == 1 and moved == False:
                                try:
                                    # if player is not at bottom wall
                                    if grid[length_gp - 1][x] != 1:
                                        check_pickup_value = check_pickup('down')
                                        grid[y][x] = 0
                                        grid[y + 1][x] = 1
                                        moved = True
                                        await map_msg.edit(content=edit_msg_on_collision(check_pickup_value))
                                    else:
                                        grid[y][x] = 1
                                        await map_msg.edit(
                                            content=gen_string(grid) + "{} can't move any further!".format(
                                                message.author.mention))
                                except Exception:
                                    grid[y][x] = 1
                                    await map_msg.edit(content=gen_string(grid) + "{} can't move any further!".format(
                                        message.author.mention))
                                break
                elif msg.content.lower() == 'up' or msg.content.lower() == 'w':
                    moved = False
                    for y in range(length_gp):
                        for x in range(width_gp):
                            if grid[y][x] == 1 and moved == False:
                                if grid[0][x] == 1:
                                    grid[y][x] = 1
                                    await map_msg.edit(content=gen_string(grid) + "{} can't move any further!".format(
                                        message.author.mention))
                                else:
                                    check_pickup_value = check_pickup('up')
                                    grid[y][x] = 0
                                    grid[y - 1][x] = 1
                                    moved = True
                                    await map_msg.edit(content=edit_msg_on_collision(check_pickup_value))
                                break
                elif commandname in msg.content.lower():
                    await map_msg.edit(content=gen_string(grid) + "{} quit!".format(message.author.mention))
                    stop = 1
                    return
                else:
                    await map_msg.edit(
                        content=gen_string(grid) + movement_msg + "\n"
                                                                  "{} must have misspelled something!".format(
                            message.author.mention))


'''
money_loc_str
Old # MIDDLE from message.
            for y in range(length_gp):
                for x in range(width_gp):
                    if 1 in grid_input[y] and 2 not in grid_input[y]:
                        if grid_input[y][x] == 1:
                            for i in grid_input[y]:
                                if i == 1:
                                    pl_loc_str = pl_loc_str + char_player
                                else:
                                    pl_loc_str = pl_loc_str + ' '
                            string = string + "|" + pl_loc_str + "|\n"
                            lines_generated = lines_generated + 1
                            break
                    # if item in grid without anything else
                    elif 2 in grid_input[y] and 1 not in grid_input[y]:
                        if grid_input[y][x] == 2:
                            for i in grid_input[y]:
                                if i == 2:
                                    item_loc_str = item_loc_str + char_item
                                else:
                                    item_loc_str = item_loc_str + ' '
                            string = string + "|" + item_loc_str + "|\n"
                            lines_generated = lines_generated + 1
                            break
                    # If item on the same grid as player
                    elif 1 in grid_input[y] and 2 in grid_input[y]:
                        if grid_input[y][x] == 1:
                            for i in grid_input[y]:
                                if i == 1:
                                    pl_loc_str = pl_loc_str + char_player
                                elif i == 2:
                                    pl_loc_str = pl_loc_str + char_item
                                else:
                                    pl_loc_str = pl_loc_str + ' '
                            string = string + "|" + pl_loc_str + "|\n"
                            lines_generated = lines_generated + 1
                            break
                    else:
                        if lines_generated < length_gp:
                            string = string + "|" + (' ' * width_gp) + "|\n"
                            lines_generated = lines_generated + 1
                            break

# bottom'''
