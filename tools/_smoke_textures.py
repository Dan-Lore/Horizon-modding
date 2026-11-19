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
print("screen", st.get("screen"))
if st.get("screen") == "title" or not st.get("player"):
    print("open", cmd("open gtceu-parity-smoke"))
    for i in range(60):
        time.sleep(0.5)
        st = cmd("status")
        if st.get("player") and st.get("pending_chunks", 1) == 0:
            print("ready", i)
            break

for it in [
    "gtceu:lv_macerator",
    "gtceu:silver_cable_4x",
    "gtceu:bronze_plate",
    "gtceu:tin_dust",
]:
    print("give", it, cmd(f"give {it} 1"))

# right-click cable in air shouldn't matter; setblock then interact via command if available
# try opening inventory — JEI should add UI widgets
print("key e?", cmd("key e"))
time.sleep(0.5)
scr = cmd("screen")
print("screen id", scr.get("screen") if isinstance(scr, dict) else scr)
if isinstance(scr, dict):
    buttons = scr.get("buttons") or []
    print("buttons", len(buttons), [b.get("label") for b in buttons[:12]])
    # some JEI UIs show as extra widgets
    for k in ("widgets", "labels", "slots", "menu"):
        if k in scr:
            v = scr[k]
            print(k, type(v).__name__, (len(v) if hasattr(v, "__len__") else v))

msg = cmd("messages")
print("actionbar", msg.get("actionbar"))
print("chat head", (msg.get("chat") or [None])[:3])
