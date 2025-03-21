# Scripts/DataFetcher.py
# Created by PlanetSurgery

import os, json, requests, re

from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap

class DataFetcherThread(QThread):
    data_fetched = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def run(self):
        try:
            response = requests.get("http://localhost:11990/Player")
            response.raise_for_status()
            data = response.json()
            self.data_fetched.emit(data)
        except Exception as e:
            self.error.emit(str(e))
            
def load_all_icons(main_window):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icons_folder = os.path.join(base_dir, "..", "Icons")
    all_items = []
    for root, dirs, files in os.walk(icons_folder):
        for file in files:
            if file.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
                path = os.path.join(root, file)
                pix = QPixmap(path)
                if pix.isNull():
                    print(f"Failed to load icon: {path}")
                    pix = QPixmap(64, 64)
                    pix.fill(Qt.gray)
                all_items.append((pix, path))
    return all_items

def check_github_update(main_window):
    url = "https://raw.githubusercontent.com/PlanetSurgery/FoundRelics/refs/heads/main/README.md"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            readme_text = response.text
            version_match = re.search(r'App Version:\s*([^\s]+)', readme_text)
            if version_match:
                version = version_match.group(1).strip()
                if version != "0.01_05":
                    message = "30 Minute Log:: Project has been updated to version " + version + ". Update for latest changes!"
                    main_window.dev_panel.log_message(message)
                    print(message)
                else:
                    print("30 Minute Log:: Your version is up to date.")
            else:
                message = "No Version Found"
                main_window.dev_panel.log_message(message)
                print(message)
            
            notice_match = re.search(r'Notice:\s*(.*)', readme_text)
            if notice_match:
                notice_text = notice_match.group(1).strip()
                if notice_text:
                    notice_message = "30 Minute Log:: Notice: " + notice_text
                    main_window.dev_panel.log_message(notice_message)
                    #print(notice_message)
        else:
            message = "Failed to fetch GitHub README. HTTP status code: " + str(response.status_code)
            main_window.dev_panel.log_message(message)
            print(message)
    except Exception as e:
        message = "Error fetching GitHub README: " + str(e)
        main_window.dev_panel.log_message(message)
        print(message)

def update_player_data(main_window):
    main_window.dev_panel.log_message("Fetching data in background...")
    thread = DataFetcherThread()
    main_window.current_data_thread = thread
    thread.data_fetched.connect(lambda data: handle_data(main_window, data))
    thread.error.connect(lambda error_msg: handle_error(main_window, error_msg))
    thread.finished.connect(lambda: setattr(main_window, 'current_data_thread', None))
    thread.start()

def handle_data(main_window, data):
    try:
        if data:
            main_window.dev_panel.log_message("We have grabbed data.")
            echelon = data.get("PlayerLevel")
            player_name = data.get("PlayerName", "")
            main_window.dev_panel.set_player_name(f"{player_name} || Echelon {echelon}")
                            
            try:
                current_xp = int(data.get("PlayerLevelProgress", 0))
            except (ValueError, TypeError):
                current_xp = 0

            try:
                max_xp = int(data.get("PlayerLevelMax", 0))
            except (ValueError, TypeError):
                max_xp = 0

            formatted_current = "{:,}".format(current_xp)
            formatted_max = "{:,}".format(max_xp)
            percentage = (current_xp / max_xp) * 100 if max_xp != 0 else 0
            final_string = f"{formatted_current} XP / {formatted_max} XP || {percentage:.0f}%"
            main_window.dev_panel.set_player_level(final_string)

            new_progress = data.get("PlayerLevelProgress", None)
            last_adv = data.get("LastAdventure", {})
            gold_coins = None
            for item in last_adv.get("Items", []):
                if item.get("Name", "").strip() == "Gold Coins":
                    gold_coins = item.get("Amount", None)
                    break
            if main_window.last_progress is None:
                main_window.last_progress = new_progress
                main_window.last_gold_coins = gold_coins
            elif new_progress is not None and new_progress != main_window.last_progress and (gold_coins is None or gold_coins != main_window.last_gold_coins):
                main_window.last_progress = new_progress
                main_window.last_gold_coins = gold_coins

                if main_window.skip:
                    main_window.skip = False
                    return
                        
                if gold_coins is not None:
                    main_window.run_count += 1
                    
                time_taken = data.get("TimeTaken", 0)
                try:
                    time_taken = float(time_taken)
                except Exception:
                    time_taken = 0
                main_window.run_time_total += time_taken

                adventure_name = last_adv.get("AdventureName", None)
                if adventure_name:
                    if adventure_name in main_window.map_counts:
                        main_window.map_counts[adventure_name] += 1
                    else:
                        main_window.map_counts[adventure_name] = 1

                    favorite_map = max(main_window.map_counts, key=main_window.map_counts.get)
                    main_window.dev_panel.set_fav_map(favorite_map)
                        
                market_gold_total = 0
                market_enj_total = 0
                for item in last_adv.get("Items", []):
                    try:
                        market_value = float(item.get("MarketValue", 0))
                    except (ValueError, TypeError):
                        market_value = 0
                    if item.get("Name", None) not in ["Enjin Gem", "Waygate Orb", "Gold Coins"]:
                        amount = item.get("Amount", 1)
                        if item.get("IsBlockchain", False):
                            market_enj_total += round((market_value * amount) / 100, 2)
                        else:
                            market_gold_total += market_value * amount

                main_window.market_gold += market_gold_total
                main_window.market_enj += market_enj_total
                main_window.dev_panel.set_market_gold("{:,}".format(main_window.market_gold))
                main_window.dev_panel.set_market_enj("{:,}".format(main_window.market_enj))

                index = -1
                for icon in main_window.item_selector_panel.selected_items:
                    index += 1
                    base_name = os.path.splitext(os.path.basename(icon.file_path))[0].strip()
                    main_window.dev_panel.log_message("Checking icon: " + base_name)
                    matching_item = next((item for item in last_adv.get("Items", []) if base_name in item.get("Name", "")), None)
                    if matching_item:
                        try:
                            count = matching_item.get("Amount", 1)
                            main_window.run_count += 1
                            if base_name in ["Enjin Gem"]:
                                count = round(matching_item.get("Amount", 1) / 100, 2)
                                main_window.items_display.item_counts[index] += round(count, 2)
                            else:
                                main_window.items_display.item_counts[index] += (count)
                        except Exception as e:
                            main_window.dev_panel.log_message("Error updating count for " + base_name + ": " + str(e))

            main_window.dev_panel.set_run_count(main_window.run_count)
            main_window.dev_panel.set_run_time(main_window.run_time_total)
            json_text = json.dumps(data, indent=2)
            main_window.json_panel.set_json_text(json_text)
            main_window.dev_panel.json_button.setEnabled(True)
        else:
            main_window.dev_panel.log_message("Failed to load data: Empty response.")
    except Exception as e:
        main_window.dev_panel.log_message("Exception in handle_data: " + str(e))

def handle_error(main_window, error_msg):
    main_window.dev_panel.log_message("Failed to load data: " + error_msg)