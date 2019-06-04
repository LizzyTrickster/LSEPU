#!/usr/bin/env python
# Copyright

import os
import requests
import PySimpleGUI as sg

# need to work out if we're running in multimc or standalone
IsMMC = False
for envvar in ["INST_NAME", "INST_ID", "INST_DIR", "INST_MC_DIR", "INST_JAVA", "INST_JAVA_ARGS"]:
    if envvar in os.environ:
        IsMMC = True
        break

print(f"Running in MultiMC? {IsMMC}")

WindowLayout = [
    [sg.Text("Lizzy's updater", key='test')],
    [sg.Text("Getting pack metadata:"), sg.ProgressBar(1, key="pb-mod-index")],
    [sg.Text("Downloading: "), sg.ProgressBar(1, key="pb-mod-download")],
    [sg.Output(size=(100, 4))]
]

mainWindow = sg.Window("Lizzy's Solder-Enabled Pack Updater", WindowLayout).Finalize()

index_bar, mod_bar = mainWindow.Element("pb-mod-index"), mainWindow.Element("pb-mod-download")

solderInstance = "https://solder.theender.net/"
solderPackName = "techycraft-30"

modpack_meta = dict()

# Look up pack details
with requests.get(f"{solderInstance}/api/modpack/{solderPackName}") as resp:
    try:
        modpack_meta['recommended'] = resp.json()["recommended"]
    except Exception:
        pass

print(f"Recommended pack version: {modpack_meta['recommended']}")
event, value = mainWindow.Read()
with requests.get(f"{solderInstance}/api/modpack/{solderPackName}/{modpack_meta['recommended']}") as resp:
    try:
        data = resp.json()
    except:
        pass
    else:
        modpack_meta["mods"] = data["mods"]
print("Processing modlist....")
index_bar.UpdateBar(0, max=len(modpack_meta["mods"]))
event, value = mainWindow.Read()

# Process mod metadata
for mod in modpack_meta["mods"]:


# with requests.get(f"{solderInstance}/api/mod/")

# Download the mods

# Extract zips
