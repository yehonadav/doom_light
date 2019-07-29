# list all actor files
# get all ids + actor names
# change actor names + ids if duplicates
# save all actor names + ids in a DB
import os

actor_dir = os.path.dirname(__file__).replace('scripts', 'monsters')
line_pattern = b'ACTOR '
pattern_length = len(line_pattern)
id_range = (0, 50000)

database = 'actors.db'
if not os.path.exists(database):
    open(database, 'w').close()


def get_db():
    data = {}
    with open(database) as f:
        lines = f.readlines()

    for line in lines:
        name, id = line.split(' ')
        data[name] = id
    return data


def update_db(data):
    data = ''.join([f'{name} {id}' for name, id in data.items()])

    with open(database, 'w') as f:
        f.write(data)


def is_id(id):
    try:
        int(id)
        return True
    except:
        return False


for dirpath, dirnames, filenames in os.walk(actor_dir):
    for file_name in filenames:
        if file_name.endswith(".wad"):
            path = dirpath + os.sep + file_name
            with open(path, 'rb') as actor_file:
                data = actor_file.read()
                lines = data.split(b'\n')
                for line in lines:
                    if len(line) > pattern_length:
                        start_line = line[:pattern_length].upper()
                        if start_line == line_pattern:
                            elements = line.split(b' ')

                            # no name
                            if len(elements) == 1:
                                pass

                            # only name
                            elif len(elements) == 2:
                                # validate actor has name and not id
                                if is_id(elements[1]):
                                    continue

                                # assign a new id
                                pass

                            # name and id are present
                            else:
                                name = elements[1]
                                id = elements[2]

                                if is_id(name):
                                    continue

                                if not is_id(id):
                                    continue

                                # check for name and id in database
