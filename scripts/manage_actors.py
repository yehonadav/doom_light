# list all actor files
# get all ids + actor names
# TODO: change actor names + ids if duplicates
# save all actor names + ids in a DB
import os

actor_dir = os.path.dirname(__file__).replace('scripts', 'things_to_import')
line_pattern = b'ACTOR '
pattern_length = len(line_pattern)
id_range = (0, 50000)
no_id_counter = {'counter': 0}

database = 'actors.db'


def get_db():
    data = {}
    if not os.path.exists(database):
        open(database, 'w').close()

    with open(database) as f:
        lines = f.readlines()

    assert len(lines) < id_range[1]

    for line in lines:
        name, id = line.split(' ')
        data[name] = id
    return data


def name_in_db(data: dict, name):
    if name in data:
        return True


def id_in_db(data: dict, id):
    if id in data.values():
        return True


def update_db(data: dict):
    data = '\n'.join([f'{name} {id}' for name, id in data.items()])

    with open(database, 'w') as f:
        f.write(data)


def is_id(id):
    try:
        int(id)
        return True
    except:
        return False


def assign_name(db, name):
    name_dup = 0
    while name_in_db(db, name):
        name = f'{name}{name_dup}'
        name_dup += 1
    return name


def assign_id(db, name):
    id = None
    ids = db.values()
    for a in range(id_range[1]):
        if str(a) not in ids:
            id = str(a)
            break
    if id:
        db[name] = id

    elif no_id_counter['counter'] == 0:
        no_id_counter['counter'] += 1
        print('no more available ids =(')


def normalize(element):
    element = str(element)[2:-1]
    return element[:-2] if element.endswith('\\r') else element

filechanges = {
#     file_path: [lines...]
}


def update_line(index, name, id, elements, file_path, is_id):
    lines = filechanges[file_path]
    line: bin = lines[index]
    line0, line2 = line.split(elements[1], 1)

    line1 = bytes(name, 'UTF-8')
    if elements[1].endswith("\\r"):
        line1 += b'\\r'

    if is_id:
        line2, line3 = line2.split(elements[2], 1)
    else:
        line3 = line2

    line2 = bytes(id, 'UTF-8')
    if elements[2].endswith("\\r"):
        line2 += b'\\r'

    line_items = (line0, line1, line2, line3)

    for i in range(len(line_items)):
        while line_items[i].startswith(b' '):
            line_items[i] = line_items[i][1:]
        while line_items[i].endswith(b' '):
            line_items[i] = line_items[i][:-1]

    line_items = [elements[0]] + line_items

    if len(elements) > 3:
        line_items.extend(elements)

    lines[index] = b' '.join(line_items)


def update_file(file_path):
    pass
    # lines = filechanges[file_path]
    # with open(file_path, 'wb') as file:
    #     file.writelines(lines)


def handle_file(path, db):
    with open(path, 'rb') as actor_file:
        data = actor_file.read()
        lines = data.split(b'\n')
        filechanges[path] = lines

        for index, line in enumerate(lines):
            if len(line) > pattern_length:
                start_line = line[:pattern_length].upper()
                if start_line == line_pattern:
                    elements = line.split(b' ')

                    # no name
                    if len(elements) == 1:
                        pass

                    # only name
                    elif len(elements) == 2:
                        name = normalize(elements[1])

                        # validate actor has name and not id
                        if is_id(name):
                            continue

                        name = assign_name(db, name)
                        assign_id(db, name)

                        file_has_changes = True
                        update_line(
                            index,
                            name,
                            id=db[name],
                            elements=elements,
                            file_path=path,
                            is_id=False
                        )

                    # name and id are present
                    else:
                        name = normalize(elements[1])
                        id = normalize(elements[2])

                        if is_id(name):
                            continue

                        if not is_id(id):
                            continue

                        # check for name and id in database
                        if name_in_db(db, name):
                            if id != db[name]:
                                original_name = name
                                name = assign_name(db, name)

                                if original_name != name:
                                    file_has_changes = True

                                if id in db.values():
                                    original_id = db[name]
                                    assign_id(db, name)

                                    if original_id != db[name]:
                                        file_has_changes = True
                                else:
                                    db[name] = id
                            update_line(
                                index,
                                name,
                                id=db[name],
                                elements=elements,
                                file_path=path,
                                is_id=True
                            )


def main():
    db = get_db()
    for dirpath, dirnames, filenames in os.walk(actor_dir):
        for file_name in filenames:
            if file_name.endswith(".wad"):
                path = dirpath + os.sep + file_name

                file_has_changes = False
                handle_file(path, db)
                if file_has_changes:
                    update_file(path)
                del filechanges[path]
    update_db(db)


if __name__ == "__main__":
    main()
