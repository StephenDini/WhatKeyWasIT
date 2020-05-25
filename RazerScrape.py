import os, re
from os import path


# Root location to look for. RAZER CENTRAL ONLY
# C:\ProgramData\Razer\Razer Central\Accounts\RZR_0070242a49548f0ad2244e5d505b\Emily3\Devices
def profiles_found():
    razer_profiles = list()

    if(str(path.exists("C:\ProgramData\Razer\Razer Central\Accounts")) == 'True' ):
        for root, dirs, files in os.walk("C:\ProgramData\Razer\Razer Central\Accounts"):
            for name in dirs:
                if name[:3] == "RZR":
                    user_folder = root + '\\' + name
                    print(user_folder)

        for root, dirs, files in os.walk(user_folder):
            for name in dirs:
                if bool(re.match('^\d+(\d{1,3})?$', name)):  # Razer Tartarus Pro
                    device_folder = root + '\\' + name
                    root_profile_folder = device_folder + "\\Features"
                    print(root_profile_folder)
                    device_name = "Razer Tartarus Pro"


        # return 'test'

# Device info location
# You might be able to ignore 770 folder. This seems to be the chroma connect device.
# /XXX/DeviceInfo.xml > under <Name> DEVICENAME </Name>

# Profiles for the Device location
# /XXX/Features/XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX

# Profiles will be the largest file

# XML tree for profile name
# Keymappings/KeymapList/Keymapping/Name

# TODO: Verify this

# Keyboard, Mouse, Jotstick, etc..
# ./Mapping/MappingGroup

# Location of the Bound Key Function. If this is missing there is no custom key set.
# ./KeyGroup/KeyAssignment/VirtualKey

# Unsure what ./KeyGroup/KeyAssignment/Scancode is

# I think this location is the order of the keys, I only use the razer Tartus, this could be very different on a normal
# keyboard.
# ./KeyGroup/KeyAssignment/AnalogInput

# TODO: Find the rest starting at Mapping/Joystick
print(profiles_found())

