def handle_data(self, data):
    if data:
        self.dev_panel.log_message("We have grabbed data.")
        self.dev_panel.set_player_name(data.get("PlayerName", ""))
        self.dev_panel.set_player_level(str(data.get("PlayerLevelProgress", "")))
        
        new_progress = data.get("PlayerLevelProgress", None)
        last_adv = data.get("LastAdventure", {})
        gold_coins = None
        for item in last_adv.get("Items", []):
            if item.get("Name", "").strip() == "Gold Coins":
                gold_coins = item.get("Amount", None)
                break

        if new_progress is not None:
            if self.last_progress is None:
                # First fetch: initialize without incrementing run count.
                self.last_progress = new_progress
                self.last_gold_coins = gold_coins
            elif new_progress != self.last_progress and (gold_coins is None or gold_coins != self.last_gold_coins):
                # A new run is confirmed; increment run count.
                self.run_count += 1
                self.last_progress = new_progress
                self.last_gold_coins = gold_coins
                
                # Accumulate run time.
                time_taken = data.get("TimeTaken", 0)
                try:
                    time_taken = float(time_taken)
                except Exception:
                    time_taken = 0
                self.run_time_total += time_taken

                # Update map counts using LastAdventure>AdventureName.
                adventure_name = last_adv.get("AdventureName", None)
                if adventure_name:
                    if adventure_name in self.map_counts:
                        self.map_counts[adventure_name] += 1
                    else:
                        self.map_counts[adventure_name] = 1

                    # Determine the favorite map (most played).
                    favorite_map = max(self.map_counts, key=self.map_counts.get)
                    self.dev_panel.set_fav_map(favorite_map)

                # For each selected icon, check if its file name matches any item in LastAdventure>Items.
                import os
                index = -1
                for icon in self.item_selector_panel.selected_items:
                    index += 1
                    base_name = os.path.splitext(os.path.basename(icon.file_path))[0].strip()
                    self.dev_panel.log_message("Checking icon: " + base_name)
                    # Find the first matching item from LastAdventure>Items.
                    matching_item = next((item for item in last_adv.get("Items", []) if base_name in item.get("Name", "")), None)
                    if matching_item:
                        try:
                            if base_name == "Enjin Gem" or base_name == "Flame Crystal":
                                count = matching_item.get("Amount", 1)
                                self.items_display.item_counts[index] += count
                            else:
                                self.items_display.item_counts[index] += 1
                        except Exception as e:
                            self.dev_panel.log_message("Error updating count for " + base_name + ": " + str(e))

        self.dev_panel.set_run_count(self.run_count)
        self.dev_panel.set_run_time(self.run_time_total)
        json_text = json.dumps(data, indent=2)
        self.json_panel.set_json_text(json_text)
        self.dev_panel.json_button.setEnabled(True)
    else:
        self.dev_panel.log_message("Failed to load data: Empty response.")
