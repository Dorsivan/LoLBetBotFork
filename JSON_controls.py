import json
import random


# writes to file
async def write_to_file(file, val):
    loadedFile = await load_file(file)
    loadedFile.append(val)
    with open(file, "w") as f:
        json.dump(loadedFile, f)
    return True


# loads file
async def load_file(file):
    file = json.load(open(file))
    return file


# return values in file
async def look_for_value_in_file(file, valuefield, valuetocompare):
    loadedFile = await load_file(file)
    result = list(filter(lambda x: x[valuefield] == valuetocompare, loadedFile))
    if not result:
        return False
    else:
        return result


async def get_3_choices():
    loadedFile = await load_file("Bets.json")
    return random.sample(loadedFile, 3)


async def pop_dict_in_list(file, dictrem):
    try:
        loadedFile = await load_file(file)
        loadedFile.remove(dictrem)
    except:
        raise ValueError("File or value doesnt exist!")
    with open(file, "w") as f:
        json.dump(loadedFile, f)
    return True
