#!/usr/bin/env python
# Copyright
import hashlib
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
session = requests.Session()

WindowLayout = [
    [sg.Text("Lizzy's updater", key='test')],
    [sg.Text("Getting pack metadata:"), sg.ProgressBar(1, key="pb-mod-index")],
    [sg.Text("Downloading: "), sg.ProgressBar(1, key="pb-mod-download")],
    [sg.Output(size=(100, 6))]
]

mainWindow = sg.Window("Lizzy's Solder-Enabled Pack Updater", WindowLayout).Finalize()

index_bar, mod_bar = mainWindow.Element("pb-mod-index"), mainWindow.Element("pb-mod-download")

solderInstance = "https://solder.theender.net/"
solderPackName = "techycraft-30"

modpack_meta = dict()
moddata = dict()

# Look up pack details
with session.get(f"{solderInstance}/api/modpack/{solderPackName}") as resp:
    try:
        modpack_meta['recommended'] = resp.json()["recommended"]
    except Exception:
        raise

print(f"Recommended pack version: {modpack_meta['recommended']}")
event, value = mainWindow.Read(timeout=0)
with session.get(f"{solderInstance}/api/modpack/{solderPackName}/{modpack_meta['recommended']}") as resp:
    try:
        data = resp.json()
    except:
        raise
    else:
        modpack_meta["mods"] = data["mods"]
print("Processing modlist....")
index_bar.UpdateBar(0, max=len(modpack_meta["mods"]))
event, value = mainWindow.Read(timeout=0)

# Process mod metadata
for mod in modpack_meta["mods"]:
    with session.get(f"{solderInstance}/api/mod/{mod['name']}") as resp:
        data = resp.json()
    #if data["description"] is not None and "#clientonly" in data['description']:
    #    client_only = True
    moddata[mod['name']] = dict(version=mod['version'], md5=mod['md5'], url=mod['url'])
    index_bar.UpdateBar(modpack_meta['mods'].index(mod))
    print(f"Processing {mod['name']}")
    event, value = mainWindow.Read(timeout=0)

CACHE_DIR = "X:\\L-SEPU\\crap"

# Download the mods
ii = 1
for mod in moddata:
    m = hashlib.md5()
    print(f"Downloading mod: {mod}")
    with session.get(f"{moddata[mod]['url']}", stream=True) as resp:
        try:
            with open(os.path.join(CACHE_DIR, f"{mod}-{moddata[mod]['version']}.zip"), "wb") as f:
                for chunk in resp.iter_content(chunk_size=1024):
                    # Chunked download so that the window can be "refreshed" when downloading large files
                    if chunk:
                        f.write(chunk)
                        m.update(chunk)
                    event, value = mainWindow.Read(timeout=0)
        except:
            raise
    print(f"Do the MD5 Hashes match? {m.hexdigest() == moddata[mod]['md5']}")
    mod_bar.UpdateBar(ii, max=len(moddata))
    ii = ii + 1

# Extract zips
