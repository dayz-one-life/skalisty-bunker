import os
import shutil
import json
import xml.etree.ElementTree as ET
import sys

# --- Configuration ---
CUSTOM_SUBDIR = "custom"

def find_mission_data_folder():
    """
    Scans the current directory for a folder that looks like a DayZ mission folder
    (e.g., starts with 'dayzOffline'). Returns the name of the folder.
    """
    # Exclude standard script/git folders
    exclusions = {".git", ".github", "__pycache__", ".idea", ".vscode"}

    candidates = []
    for item in os.listdir("."):
        if os.path.isdir(item) and item not in exclusions:
            # We assume the main data folder is the one containing the custom content
            if os.path.exists(os.path.join(item, CUSTOM_SUBDIR)) or item.startswith("dayzOffline"):
                candidates.append(item)

    if not candidates:
        print("Error: Could not find a mission data folder in this repository.")
        print("Make sure you have a folder named 'dayzOffline.chernarusplus' (or similar) containing your files.")
        sys.exit(1)

    # Return the first valid candidate found
    return candidates[0]

def get_mission_path(mission_name):
    print("\n--- Mission Selection ---")
    print(f"Detected repository data for map: {mission_name}")
    print("Please enter the full path to your server's mission directory.")
    print("Typical examples based on this map:")
    print(f"  - Windows: C:\\DayZServer\\mpmissions\\{mission_name}")
    print(f"  - Linux:   /home/dayz/server/mpmissions/{mission_name}")

    path = input("\nPath: ").strip()

    # Clean up quotes
    if path.startswith('"') and path.endswith('"'):
        path = path[1:-1]

    if not os.path.isdir(path):
        print(f"Error: The directory '{path}' does not exist.")
        sys.exit(1)

    return path

def install_custom_files(mission_path, data_dir):
    print("\n--- Step 1: Installing Custom Files ---")

    src_custom = os.path.join(data_dir, CUSTOM_SUBDIR)
    dst_custom = os.path.join(mission_path, "custom")

    if not os.path.exists(src_custom):
        print(f"No custom files found in {src_custom}. Skipping.")
        return []

    if not os.path.exists(dst_custom):
        os.makedirs(dst_custom)
        print(f"Created directory: {dst_custom}")

    installed_files = []

    for filename in os.listdir(src_custom):
        if filename.endswith(".json"):
            src_file = os.path.join(src_custom, filename)
            dst_file = os.path.join(dst_custom, filename)
            shutil.copy(src_file, dst_file)
            print(f"Copied {filename}")
            installed_files.append(filename)

    return installed_files

def update_cfggameplay(mission_path, installed_files):
    print("\n--- Step 2: Updating cfggameplay.json ---")
    cfg_path = os.path.join(mission_path, "cfggameplay.json")

    if not os.path.exists(cfg_path):
        print("Error: cfggameplay.json not found.")
        return

    try:
        with open(cfg_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if "WorldsData" not in data:
            print("Error: 'WorldsData' missing in config.")
            return

        changed = False

        if "objectSpawnersArr" not in data["WorldsData"]: data["WorldsData"]["objectSpawnersArr"] = []
        if "playerRestrictedAreaFiles" not in data["WorldsData"]: data["WorldsData"]["playerRestrictedAreaFiles"] = []

        for filename in installed_files:
            rel_path = f"./custom/{filename}"

            if filename.lower().endswith("-pra.json"):
                target_list = data["WorldsData"]["playerRestrictedAreaFiles"]
                list_name = "playerRestrictedAreaFiles"
            else:
                target_list = data["WorldsData"]["objectSpawnersArr"]
                list_name = "objectSpawnersArr"

            if rel_path not in target_list:
                target_list.append(rel_path)
                print(f"Added {rel_path} to {list_name}")
                changed = True
            else:
                print(f"Skipping {rel_path} (already exists)")

        if changed:
            with open(cfg_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            print("Saved cfggameplay.json")

    except Exception as e:
        print(f"Error updating gameplay config: {e}")

def merge_json_triggers(mission_path, data_dir):
    print("\n--- Step 3: Updating Triggers ---")
    src_file = os.path.join(data_dir, "cfgundergroundtriggers.json")
    dst_file = os.path.join(mission_path, "cfgundergroundtriggers.json")

    if not os.path.exists(src_file):
        print("No triggers file in data folder. Skipping.")
        return

    if not os.path.exists(dst_file):
        print("Target cfgundergroundtriggers.json not found. Skipping.")
        return

    try:
        with open(src_file, 'r', encoding='utf-8') as f: src_data = json.load(f)
        with open(dst_file, 'r', encoding='utf-8') as f: dst_data = json.load(f)

        if "Triggers" not in dst_data: dst_data["Triggers"] = []

        count = 0
        for trigger in src_data.get("Triggers", []):
            if trigger not in dst_data["Triggers"]:
                dst_data["Triggers"].append(trigger)
                count += 1

        if count > 0:
            with open(dst_file, 'w', encoding='utf-8') as f: json.dump(dst_data, f, indent=4)
            print(f"Added {count} triggers.")
        else:
            print("No new triggers needed.")

    except Exception as e:
        print(f"Error merging triggers: {e}")

def merge_xml_content(mission_path, data_dir, filename, root_tag, id_attr):
    print(f"\n--- Processing {filename} ---")
    src_file = os.path.join(data_dir, filename)
    dst_file = os.path.join(mission_path, filename)

    if not os.path.exists(src_file):
        print(f"No {filename} in data folder. Skipping.")
        return

    if not os.path.exists(dst_file):
        print(f"Target {filename} not found. Skipping.")
        return

    try:
        ET.register_namespace('', "")
        target_tree = ET.parse(dst_file)
        target_root = target_tree.getroot()
        source_tree = ET.parse(src_file)

        existing = set()
        for child in target_root:
            val = child.get(id_attr)
            if filename == "mapgrouppos.xml":
                pos = child.get("pos")
                if val and pos: existing.add(f"{val}|{pos}")
            elif val:
                existing.add(val)

        count = 0
        for child in source_tree.getroot():
            val = child.get(id_attr)
            unique_key = val
            if filename == "mapgrouppos.xml":
                pos = child.get("pos")
                unique_key = f"{val}|{pos}"

            if unique_key and unique_key not in existing:
                target_root.append(child)
                existing.add(unique_key)
                count += 1
            elif filename == "cfgspawnabletypes.xml" and val in existing:
                for existing_node in target_root.findall(f".//*[@{id_attr}='{val}']"):
                    target_root.remove(existing_node)
                target_root.append(child)
                count += 1
                print(f"Updated type: {val}")

        if count > 0:
            indent(target_root)
            target_tree.write(dst_file, encoding="UTF-8", xml_declaration=True)
            print(f"Added/Updated {count} entries.")
        else:
            print("No changes required.")

    except Exception as e:
        print(f"Error processing XML: {e}")

def indent(elem, level=0):
    i = "\n" + level * "    "
    if len(elem):
        if not elem.text or not elem.text.strip(): elem.text = i + "    "
        if not elem.tail or not elem.tail.strip(): elem.tail = i
        for elem in elem: indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip(): elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()): elem.tail = i

def main():
    print("=== Generic DayZ Mod Installer ===")

    # 1. Find Data Folder
    data_dir = find_mission_data_folder()

    # 2. Get User Mission Path (using hints from data_dir)
    mission_path = get_mission_path(data_dir)

    # 3. Install
    files = install_custom_files(mission_path, data_dir)
    if files:
        update_cfggameplay(mission_path, files)

    merge_json_triggers(mission_path, data_dir)
    merge_xml_content(mission_path, data_dir, "mapgrouppos.xml", "map", "name")
    merge_xml_content(mission_path, data_dir, "mapgroupproto.xml", "prototype", "name")
    merge_xml_content(mission_path, data_dir, "cfgspawnabletypes.xml", "spawnabletypes", "name")

    print("\n=== Installation Complete ===")

if __name__ == "__main__":
    main()