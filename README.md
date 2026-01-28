# Skalisty Bunker - DayZ Custom Map Addition (Chernarus)

This repository contains files to add the custom "Skalisty Bunker" to your DayZ Chernarus mission. You can install this modification automatically using the provided Python script or manually.

## Prerequisites

* A DayZ Server with a Chernarus mission folder (e.g., `dayzOffline.chernarusplus`).
* **For Automatic Install:** Python 3.x installed on your system.

---

## Method 1: Automatic Installation (Recommended)

This method uses a Python script to automatically copy files and inject the necessary code into your mission configuration files.

### Steps

1.  **Download Files:** Ensure all files from this repository (including `install_skalisty_bunker.py`) are in the same folder.
2.  **Run Script:** Open your terminal or command prompt in that folder and run:
    ```bash
    python install_skalisty_bunker.py
    ```
3.  **Provide Mission Path:** When prompted, paste the full path to your server's mission directory (e.g., `C:\DayZServer\mpmissions\dayzOffline.chernarusplus`).

The script will automatically:
* Create a `custom` folder in your mission directory if it doesn't exist.
* Copy `skalisty-bunker.json` and `skalisty-bunker-pra.json` to that folder.
* Update `cfggameplay.json` to spawn the bunker objects and restrict the area.
* Add the necessary underground triggers to `cfgundergroundtriggers.json`.
* Add the required loot and map groups to `mapgrouppos.xml` and `mapgroupproto.xml`.

---

## Method 2: Manual Installation

If you prefer to install manually, follow these steps strictly.

### 1. Copy Custom Files
1.  Navigate to your mission folder (e.g., `dayzOffline.chernarusplus`).
2.  Create a folder named `custom` if it does not already exist.
3.  Copy the following files from this repository into `dayzOffline.chernarusplus/custom/`:
    * `skalisty-bunker.json`
    * `skalisty-bunker-pra.json`

### 2. Update `cfggameplay.json`
Open `cfggameplay.json` in your mission folder and make the following changes:

* **Object Spawners:** Locate the `"objectSpawnersArr"` array inside `"WorldsData"`. Add:
    ```json
    "objectSpawnersArr": [
        "./custom/skalisty-bunker.json"
    ],
    ```
* **Restricted Areas:** Locate the `"playerRestrictedAreaFiles"` array inside `"WorldsData"`. Add:
    ```json
    "playerRestrictedAreaFiles": [
        "./custom/skalisty-bunker-pra.json"
    ],
    ```

### 3. Update `cfgundergroundtriggers.json`
1.  Open `undergroundtrigger-entries.json` from this repository.
2.  Open `cfgundergroundtriggers.json` in your mission folder.
3.  Copy all trigger objects (the code between `{` and `}`) from the source file and paste them into the `"Triggers": [ ... ]` array in your mission file.

### 4. Update `mapgrouppos.xml`
1.  Open `mapgrouppos-entries.xml` from this repository.
2.  Open `mapgrouppos.xml` in your mission folder.
3.  Copy all `<group ... />` lines from the source file and paste them inside the `<map>` tag of your mission file.

### 5. Update `mapgroupproto.xml`
1.  Open `mapgroupproto-entries.xml` from this repository.
2.  Open `mapgroupproto.xml` in your mission folder.
3.  Copy the entire group definitions (e.g., `<group name="..."> ... </group>`) from the source file.
4.  Paste them inside the `<prototype>` tag of your mission file.

---
**Installation Complete!** Restart your server to see the changes.