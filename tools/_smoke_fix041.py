import json
import socket
import time
from pathlib import Path

info = json.loads(
    Path(r"C:/Users/smoln/AppData/Roaming/horizon-launcher/game-control.json").read_text(
        encoding="utf-8"
    )
)
s = socket.create_connection(("127.0.0.1", info["port"]), timeout=15)
f = s.makefile("rwb", buffering=0)


def cmd(line: str):
    f.write((line + "\n").encode())
    f.flush()
    return json.loads(f.readline().decode())


print("auth", cmd("auth " + info["token"]))
st = cmd("status")
if st.get("screen") == "title" or not st.get("player"):
    print("open", cmd("open greglite-parity-smoke"))
    for _ in range(40):
        time.sleep(0.5)
        st = cmd("status")
        if st.get("player") and st.get("pending_chunks", 1) == 0:
            print("ready")
            break

cmd("options-set guiScale 2")
cmd("command gamemode creative")
for it in [
    "greglite:lv_macerator",
    "greglite:tin_cable_1x",
    "greglite:silver_cable_4x",
    "greglite:tin_ingot",
    "greglite:lv_steam_turbine",
    "greglite:steam_solid_boiler_lp",
    "minecraft:coal",
]:
    print("give", it, cmd(f"give {it} 1"))

# place macerator in front
st = cmd("status")
x, y, z = [int(v) for v in st["player"]["position"]]
print("setblock mac", cmd(f"setblock {x} {y} {z + 2} greglite:lv_macerator"))
print("setblock cable", cmd(f"setblock {x} {y} {z + 1} greglite:tin_cable_1x"))
print("look", cmd("look 0 20"))
time.sleep(0.3)
# interact to open GUI
print("select", cmd("select 1"))
print("interact", cmd("interact"))
time.sleep(0.5)
ui = cmd("ui")
print("screen", ui.get("screen"), "widgets", len(ui.get("widgets") or []))
print(cmd("screenshot C:/Dev/Horizon-modding/tools/_fix_gui.png"))
cmd("close")
time.sleep(0.2)
print(cmd("screenshot C:/Dev/Horizon-modding/tools/_fix_hotbar.png"))

# JEI survival
cmd("command gamemode survival")
time.sleep(0.2)
cmd("open-inventory")
time.sleep(1.5)
print(cmd("screenshot C:/Dev/Horizon-modding/tools/_fix_jei.png"))
cmd("close")
cmd("command gamemode creative")
print("done")
