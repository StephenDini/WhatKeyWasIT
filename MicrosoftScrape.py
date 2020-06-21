# Custom Bindings are located in"
# %APPDATALOCAL%/Microsoft/PowerToys/Keyboard Manager/default.json

# Microsoft only shows what is remapped to what.
# These are using VirtualKeys
import csv, json
from os import path

def devirtualize(vitualkey):
    """ Take the Vitural Keys number value and returns the key """
    key_map = dict()

    with open('VirtualKeys.csv',mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            key_map.update({row['VK']: row['KEY']})

    return key_map[vitualkey]


def getListofChanges():
    """ Gathers the keybindings into a list """
    with open(path.expandvars(r'%LOCALAPPDATA%\Microsoft\PowerToys\Keyboard Manager\default.json')) as f:
        microsoft_keybind_file = json.load(f)

    with open(path.expandvars(r'%LOCALAPPDATA%\Microsoft\PowerToys\settings.json')) as f:
        m_enabled_check = json.load(f)

    remapKeys = microsoft_keybind_file["remapKeys"]
    inProcess = remapKeys["inProcess"]
    enable_check = m_enabled_check["enabled"]
    key_manager = enable_check["Keyboard Manager"]
    # print(key_manager)

    gathered_binds = [(str(devirtualize(container['originalKeys'])),  str(devirtualize(container['newRemapKeys']))) for container in inProcess]
    gathered_binds.append(key_manager)
    return gathered_binds
