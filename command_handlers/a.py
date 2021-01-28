import random
import asyncio

prefix = '!'

wait_time = 0.5
timeout_time = 20
min_seed = 0
max_seed = 1000

# One room has shop or boss

# Click to reveal! ||**good item**|| ||normal|| ||*bad*||

# Room data
class room:
    def __init__(self, name, odds):
        self.name = name
        self.odds = odds


room_list = dict(
    goblin=room("Room 1", .5),
    rare=room("Room 2", .2)
)
rooms = []
rooms_weight = []
for k in room_list:
    rooms.append(room_list[k])
    rooms_weight.append(room_list[k].odds)


def gen_lvl(width, height, max_rooms, seed):
    random.seed(seed)

    map = []
    room_count = 0
    for y in range(height):
        new_row = []
        for x in range(width):
            new_row.append(0)
        map.append(new_row)

    for y in range(height):
        for x in range(width):
            r_int = random.randint(0, 1)
            if r_int == 1:
                room_count = room_count + 1
            map[y][x] = r_int

        '''
        # Add extra rooms when there's two empty ones next to each other
        # ? For each room in existence
        for index, r in enumerate(map[y]):
            if map[y] is not 0 and map[y] is not len(map[y]):
                if r == 0 and map[y][index - 1] == 0:
                    # print('two empty rooms at map[y]: {}'.format(map[y]))
                    map[y][x] = 1
                    '''

    return [map, seed]


#  gen_lvl into discord format
def gen_map_msg(width, length, lvl):
    # lvl[0] = ALL ROOMS - lvl[0][0] = FIRST ROW - lvl[1] = ROOM SEED

    # Code block start
    width_symbol = ''
    for i in range(width):
        width_symbol = width_symbol + '-'
    length_symbol = ''
    for o in range(width):
        length_symbol = length_symbol + ' '
    string = "```\n"

    # Converting room rows to string
    # ? For every row in generated level
    for lvl_row in lvl[0]:

        # Formulate TOP of the room
        # ? For every room in every level row
        for lvl_room in lvl_row:
            if lvl_room == 1:
                string = string + "+" + width_symbol + "+"
            else:
                string = string + " " + (" " * len(width_symbol)) + " "
        string = string + '\n'

        # Formulate SPACE in the room
        for lvl_length in range(length):
            for lvl_room in lvl_row:

                # Random room code per room in level row
                with open('./resources/misc/fiveletterwords.txt', 'r', encoding='utf-8') as words:
                    room_code = str(random.choice(list(words)).rstrip()).capitalize() + " room"
                # room_code = "Room " + str((random.randrange(1, 10000)))

                if lvl_room == 1:
                    if lvl_length == 0:
                        spaces = width
                        for chars in room_code:
                            spaces = spaces - 1
                        string = string + "|" + room_code + (' ' * spaces) + "|"
                    else:
                        string = string + "|" + length_symbol + "|"
                else:
                    string = string + " " + (" " * len(width_symbol)) + " "
            string = string + '\n'

        # Formulate BOTTOM of the room
        for lvl_room in lvl_row:
            if lvl_room == 1:
                string = string + "+" + width_symbol + "+"
            else:
                string = string + " " + (" " * len(width_symbol)) + " "
        string = string + '\n'

    string = string + "\n"

    string = string + "\nLevel seed: {}".format(lvl[1])

    # Code block end
    string = string + "\n```"

    return string


# If '||' in string. 1/5 chance for a door?

# Rogue like
async def run(client, message):
    if len(message.content.split()) < 2:
        print('help msg')

    elif len(message.content.split()) >= 2:

        if message.content.split()[1] == 'play' or message.content.split()[1] == 'seed':
            # Generate seed based on message.
            if message.content.split()[1] == 'play':
                r_seed = random.randrange(min_seed, max_seed)
            elif message.content.split()[1] == 'seed':
                try:
                    r_seed = int(message.content.split()[2])
                except Exception:
                    await message.channel.send("{} seed wasn't entered, or not as an integer!".format(message.author.mention))
                    return
            else:
                r_seed = 0

            lvl = gen_lvl(3, 3, 5, r_seed)
            await message.channel.send(gen_map_msg(10, 3, lvl))

            def check(msg):
                return msg.author == message.author
            try:
                msg = await client.wait_for('message', check=check, timeout=timeout_time)
            except asyncio.TimeoutError:
                await message.channel.send("{} waited too long!".format(message.author.mention))
                return
            else:
                if msg.content.lower() == 'enter':
                    print('enter')

        else:
            print('help msg')

    else:
        print('help msg')