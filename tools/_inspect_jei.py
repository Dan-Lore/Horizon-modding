import zipfile
from pathlib import Path

z = zipfile.ZipFile(
    Path.home()
    / "AppData/Roaming/horizon/instances/create-nightly-test/horizon-native-mods/jei.hnmod"
)
print("==== screen_post ====")
print(z.read("mixins/jei/screen_post.rs").decode()[:3500])
print("==== list head ====")
print(z.read("mixins/jei/list.rs").decode()[:2500])

root = Path.home() / "AppData/Roaming/horizon"
for p in root.rglob("*"):
    if not p.is_file():
        continue
    name = p.name.lower()
    if "jei" in name and p.stat().st_size < 50000:
        print("cfg", p, p.stat().st_size)
