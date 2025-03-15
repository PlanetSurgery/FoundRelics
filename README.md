# 💻 FoundRelics  
_A Simple Query API Fetcher Tool_

> **Notes:** Must have activated an orb to use; please purchase one to continue. Also note, panels is draggable -- Item display will be movable as well in a future update.

---

![alt text](https://i.ibb.co/C5ZpZLVC/Lost-Relics-3-8-2025-10-17-56-AM-removebg-preview-1.png)

### Features
  1. Loot Tracker
  2. Player Info
  3. Run Count
  4. Earned Market Gold & ENJ Per Run
  5. Favorite Map
  6. JSON Data
  7. Toggle In-Game UI

### Setup Instructions
   *Tip: This currently uses Python310. Edit setup and run batch files to change (I'll add a version check later.)
    Panels are draggable by clicking & holding panel title bar.
    This tool is still a WIP, so you may run into issues during use.
    This is not fully tested. Some items do not work. 
    Playing TD, DN, or Siege after fighting boss will bug out item & run counts at this moment; please play an adventure map in between.
    Run Time and the "Earned" labels are being worked on.
    This app runs on two threads.
    Untradable items currently add to market values -- communicating with dev to change.*

1. **Install Python:**  
   Ensure you have Python v3.10 installed on your machine. If not, download it [here](https://www.python.org/downloads/release/python-3100/). If you are using a different version, you will need to edit the Setup & Run script. This will be auto in the future.

2. **Initial Setup:**  
   Run the `Setup.bat` file to install any required modules.

3. **Settings:**  
   Make sure you have the "Settings>Options>Query API" turned on in game settings.

4. **Adding New Items:**  
   When providing new items, ensure that the file name exactly matches its name in the JSON data.

   ============

### Tested Items (In Communication w/ Dev Team to Fix)

| Item                     | Status | 
|--------------------------|--------|
| Arcane Fragments         | ❌     |
| Armor Gems               | ❌     |
| Enjin Gems               | ✅     |
| Flame Crystal            | ✅     |
| Golden Grind Chest       | ✅     |
| Guardian's Chest         | ✅     |
| Luminal Extract          | ✅     |
| Mysterious Nest          | ✅     |
| Sunken Treasure Trove    | ✅     |
| Void Satchel             | ✅     |

---

# 🎥 Watch the Video (Outdated): FoundRelics - Loot Tracker Tool
[![FoundRelics - Loot Tracker Tool](https://img.youtube.com/vi/7pXumxXoP04/maxresdefault.jpg)](https://www.youtube.com/watch?v=7pXumxXoP04)

App Version: 0.01_05
---
Notice: Please do not move panels behind item display; it will be unusable afterwards. Also note, this will bug out from extra modes most of the time as there is no proper run counter yet. One final thing, some items currently do not work due to having similar names. 

Game Servers Are Currently Down
