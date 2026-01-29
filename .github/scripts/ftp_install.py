import os
import json
import ftplib
import xml.etree.ElementTree as ET
import sys
import io

# --- Configuration ---
CUSTOM_SUBDIR = "custom"

# --- Helper Functions (In-Memory Processing) ---
def find_mission_data_folder():
    """Scans repository for the mission data folder"""
    exclusions = {".git", ".github", "__pycache__", ".idea", ".vscode"}
    candidates = []
    # Scan root directory
    for item in os.listdir("."):
        if os.path.isdir(item) and item not in exclusions:
            if os.path.exists(os.path.join(item, CUSTOM_SUBDIR)) or item.startswith("dayzOffline"):
                candidates.append(item)

    if not candidates: return None
    return candidates[0]

def process_json_gameplay(file_content, installed_files):
    try:
        data = json.loads(file_content.decode('utf-8'))
        if "WorldsData" not in data: return None

        changed = False
        if "objectSpawnersArr" not in data["WorldsData"]: data["WorldsData"]["objectSpawnersArr"] = []
        if "playerRestrictedAreaFiles" not in data["WorldsData"]: data["WorldsData"]["playerRestrictedAreaFiles"] = []

        for filename in installed_files:
            rel_path = f"./custom/{filename}"
            if filename.lower().endswith("-pra.json"):
                target = data["WorldsData"]["playerRestrictedAreaFiles"]
            else:
                target = data["WorldsData"]["objectSpawnersArr"]

            if rel_path not in target:
                target.append(rel_path)
                changed = True

        return json.dumps(data, indent=4).encode('utf-8') if changed else None
    except: return None

def process_json_triggers(target_content, source_path):
    try:
        target_data = json.loads(target_content.decode('utf-8'))
        with open(source_path, 'r', encoding='utf-8') as f: source_data = json.load(f)

        if "Triggers" not in target_data: target_data["Triggers"] = []

        count = 0
        for trig in source_data.get("Triggers", []):
            if trig not in target_data["Triggers"]:
                target_data["Triggers"].append(trig)
                count += 1

        return json.dumps(target_data, indent=4).encode('utf-8') if count > 0 else None
    except: return None

def process_xml(target_content, source_path, filename):
    try:
        ET.register_namespace('', "")
        target_tree = ET.ElementTree(ET.fromstring(target_content.decode('utf-8')))
        target_root = target_tree.getroot()
        source_tree = ET.parse(source_path)

        existing = set()
        id_attr = "name"

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

        if count > 0:
            out = io.BytesIO()
            target_tree.write(out, encoding="UTF-8", xml_declaration=True)
            return out.getvalue()
        return None
    except: return None

# --- FTP Logic ---
def run_ftp_install():
    # 1. Setup Data Directory
    data_dir = find_mission_data_folder()
    if not data_dir:
        print("Error: Could not find a mission data folder in the repository.")
        sys.exit(1)

    print(f"Using source data from: {data_dir}")

    # 2. Get Inputs
    HOST = os.environ.get("FTP_HOST")
    USER = os.environ.get("FTP_USER")
    PASS = os.environ.get("FTP_PASSWORD")
    PORT = int(os.environ.get("FTP_PORT", 21))
    PATH = os.environ.get("MISSION_PATH", "").strip()

    if not HOST or not USER or not PASS:
        print("Error: Missing FTP credentials.")
        sys.exit(1)

    if not PATH:
        print("Error: Mission Path is required.")
        print(f"HINT: Based on this repo, your path should likely end in: .../{data_dir}")
        print("Common examples:")
        print(f" - Xbox:  /dayzxb_missions/{data_dir}")
        print(f" - PS:    /dayzps_missions/{data_dir}")
        print(f" - PC:    /mpmissions/{data_dir}")
        sys.exit(1)

    print(f"Connecting to {HOST}:{PORT}...")

    try:
        ftp = ftplib.FTP()
        ftp.connect(HOST, PORT)
        ftp.login(USER, PASS)
        print("Connected.")

        try:
            ftp.cwd(PATH)
            print(f"Working directory: {PATH}")
        except:
            print(f"Error: Could not navigate to '{PATH}'. Check path and permissions.")
            sys.exit(1)

        # 3. Install Custom Files
        print("Syncing custom files...")
        if "custom" not in ftp.nlst(): ftp.mkd("custom")

        local_custom = os.path.join(data_dir, CUSTOM_SUBDIR)
        installed_files = []
        if os.path.exists(local_custom):
            for fname in os.listdir(local_custom):
                if fname.endswith(".json"):
                    with open(os.path.join(local_custom, fname), "rb") as f:
                        ftp.storbinary(f"STOR custom/{fname}", f)
                    print(f"Uploaded custom/{fname}")
                    installed_files.append(fname)

        # 4. Update Configs
        configs = [
            ("cfggameplay.json", "json_gameplay"),
            ("cfgundergroundtriggers.json", "json_trigger"),
            ("mapgrouppos.xml", "xml"),
            ("mapgroupproto.xml", "xml"),
            ("cfgspawnabletypes.xml", "xml")
        ]

        remote_files = ftp.nlst()

        for fname, type_ in configs:
            local_src = os.path.join(data_dir, fname)

            if type_ != "json_gameplay" and not os.path.exists(local_src):
                continue

            if fname in remote_files:
                print(f"Processing {fname}...")

                # A. Download
                r = io.BytesIO()
                ftp.retrbinary(f"RETR {fname}", r.write)
                content = r.getvalue()

                # B. Modify
                new_content = None
                if type_ == "json_gameplay":
                    new_content = process_json_gameplay(content, installed_files)
                elif type_ == "json_trigger":
                    new_content = process_json_triggers(content, local_src)
                elif type_ == "xml":
                    new_content = process_xml(content, local_src, fname)

                # C. Backup & Upload
                if new_content:
                    backup_name = f"{fname}.bak"
                    try:
                        if backup_name in ftp.nlst(): ftp.delete(backup_name)
                        ftp.rename(fname, backup_name)
                        print(f"  -> Created backup: {backup_name}")
                    except:
                        print(f"  -> Warning: Failed to backup {fname}")

                    ftp.storbinary(f"STOR {fname}", io.BytesIO(new_content))
                    print(f"  -> Updated {fname}")
                else:
                    print(f"  -> No changes needed for {fname}")
            else:
                print(f"Warning: Remote file {fname} not found. Skipping.")

        ftp.quit()
        print("\n=== Success ===")

    except Exception as e:
        print(f"FTP Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_ftp_install()