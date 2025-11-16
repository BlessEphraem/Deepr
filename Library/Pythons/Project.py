import os
import sys
import json
import shutil
import subprocess
import configparser
import platform
import tempfile
import time
from datetime import datetime
sys.dont_write_bytecode = True

# Conditional import of GoogleCalendar for the API
try:
    import GoogleCalendar
except ImportError:
    GoogleCalendar = None

# --- TUI ENGINE (Colors & Keyboard Management) ---

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    INVERT = "\033[7m"      
    BLUE_BG = "\033[44m"
    RED_BG = "\033[41m"
    WHITE_TXT = "\033[97m"
    HEADER = "\033[95m"     
    GREEN = "\033[92m"      
    GREY = "\033[90m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    
    @staticmethod
    def hex_to_ansi(hex_color):
        """Converts HEX (#RRGGBB) to ANSI foreground code"""
        if not hex_color or not hex_color.startswith('#'): return Colors.WHITE_TXT
        hex_color = hex_color.lstrip('#')
        try:
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            return f"\033[38;2;{r};{g};{b}m"
        except: return Colors.WHITE_TXT

class _Getch:
    """Cross-platform non-blocking keyboard input manager"""
    def __init__(self):
        try: self.impl = _GetchWindows()
        except ImportError: self.impl = _GetchUnix()
    def __call__(self): return self.impl()

class _GetchUnix:
    def __init__(self): import tty, termios
    def __call__(self):
        import tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                seq = sys.stdin.read(2)
                if seq == '[A': return 'UP'
                if seq == '[B': return 'DOWN'
            return ch
        finally: termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

class _GetchWindows:
    def __init__(self): import msvcrt
    def __call__(self):
        import msvcrt
        ch = msvcrt.getch()
        if ch == b'\xe0':
            ch = msvcrt.getch()
            if ch == b'H': return 'UP'
            if ch == b'P': return 'DOWN'
        try: return ch.decode('utf-8')
        except: return ch

getch = _Getch()

def input_text_tui(prompt, default_val=""):
    """Clean text input"""
    # Print prompt
    p_str = f"{Colors.CYAN}{prompt}{Colors.RESET} "
    if default_val:
        p_str += f"[{default_val}] "
        
    sys.stdout.write(f"\r{p_str}")
    sys.stdout.flush()
    try:
        if os.name != 'nt':
            import tty, termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            termios.tcsetattr(fd, termios.TCSADRAIN, termios.tcgetattr(sys.stdout))
        
        user_input = input()
        
        if os.name != 'nt': termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        
        result = user_input.strip()
        if not result and default_val: return default_val
        return result
    except: return default_val

# --- CONFIGURATION & PATHS ---

def get_app_data_dir() -> str:
    APP_NAME = "ProjectsManager" 
    try:
        user_home = os.path.expanduser('~')
        config_dir = os.path.join(user_home, '.config', APP_NAME)
        os.makedirs(config_dir, exist_ok=True)
        return config_dir
    except: return os.getcwd()

APP_DIR = get_app_data_dir()
SETTINGS_FILE = os.path.join(APP_DIR, "settings.json")
PROJECTS_DB = os.path.join(APP_DIR, "projects.ini")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_MAKER_SCRIPT = os.path.join(SCRIPT_DIR, "Template.py")

# --- BUSINESS LOGIC (Settings & DB) ---

def save_settings_file(data):
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving settings: {e}")

def load_settings() -> dict:
    if not os.path.exists(SETTINGS_FILE): return init_settings()
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if "Projects_Directory" not in data: return init_settings()
            
            current_root = data.get("Projects_Directory", "")
            if not os.path.exists(current_root):
                return fix_broken_root_path(data)
            
            if "Customer_Colors" not in data:
                data["Customer_Colors"] = {}
                save_settings_file(data)

            return data
    except: return init_settings()

def fix_broken_root_path(settings: dict) -> dict:
    bad_path = settings.get("Projects_Directory", "Unknown")
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Colors.RED_BG}{Colors.WHITE_TXT} CRITICAL CONFIG ERROR {Colors.RESET}")
    print(f"\nMissing Path: {Colors.RED}{bad_path}{Colors.RESET}")
    while True:
        new_path = input(f"{Colors.YELLOW}New Directory Path: {Colors.RESET}").strip()
        if new_path.startswith('"') and new_path.endswith('"'): new_path = new_path[1:-1]
        
        if not os.path.exists(new_path):
            print(f"{Colors.RED}Directory does not exist.{Colors.RESET}")
            print("Create it? (y/n)")
            if input().lower() == 'y':
                try: os.makedirs(new_path)
                except Exception as e: print(f"Failed: {e}"); continue
            else: continue

        if os.path.exists(new_path) and os.path.isdir(new_path):
            settings["Projects_Directory"] = new_path
            save_settings_file(settings)
            return settings

def init_settings() -> dict:
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Colors.HEADER}--- INITIAL CONFIGURATION ---{Colors.RESET}")
    proj_dir = ""
    while True:
        proj_dir = input("Production Directory (Full path): ").strip()
        if proj_dir.startswith('"') and proj_dir.endswith('"'): proj_dir = proj_dir[1:-1]
        
        if not os.path.exists(proj_dir):
            print("Directory does not exist. Create it? (y/n)")
            if input().lower() == 'y':
                try: os.makedirs(proj_dir)
                except: print("Failed."); continue
            else: continue

        if os.path.exists(proj_dir) and os.path.isdir(proj_dir): break
    
    steps = []
    print(f"\n{Colors.YELLOW}Adding Steps (Optional){Colors.RESET}")
    while True:
        s = input("Step Name (e.g., Review) (Enter to finish): ").strip()
        if not s: break
        steps.append(s)
        
    use_google = input("\nUse Google Calendar? (y/n): ").lower() == 'y'
    add_cust_title = input("Add customer name to project folder? (y/n): ").lower() == 'y'
    
    settings = {
        "Projects_Directory": proj_dir,
        "Title_AddCustomer": add_cust_title,
        "GoogleAPI": use_google,
        "User_Wants_Google": use_google,
        "Customers": [], 
        "Customer_Colors": {}, 
        "Steps": steps
    }
    save_settings_file(settings)
    settings = sync_customers(settings)
    # Initial Project Sync
    sync_projects_db(settings)
    return settings

def sync_customers(settings: dict) -> dict:
    """Sync filesystem folders with settings."""
    root = settings.get("Projects_Directory")
    if not root or not os.path.exists(root): return settings

    valid_fs_customers = set()
    try:
        for entry in os.scandir(root):
            if entry.is_dir() and not entry.name.startswith(('.', '_', '-')):
                valid_fs_customers.add(entry.name)
    except: return settings

    current_json_customers = set(settings.get("Customers", []))
    has_changes = False

    removed = current_json_customers - valid_fs_customers
    if removed:
        settings["Customers"] = [c for c in settings["Customers"] if c not in removed]
        has_changes = True

    new_cust = valid_fs_customers - current_json_customers
    if new_cust:
        # Silent add during startup to avoid blocking, or simple prompt if empty
        # For this version, we AUTO ADD to ensure synchronization without hassle
        for nc in new_cust:
             settings["Customers"].append(nc)
             if "Customer_Colors" not in settings: settings["Customer_Colors"] = {}
             settings["Customer_Colors"][nc] = "#FFFFFF"
             has_changes = True

    if has_changes:
        settings["Customers"].sort()
        save_settings_file(settings)
    return settings

def sync_projects_db(settings: dict) -> int:
    """
    SMART SYNC:
    1. Scan FS for existing projects.
    2. Add missing projects to DB.
    3. Remove deleted projects from DB.
    4. Keep deadlines for existing ones.
    """
    root = settings.get("Projects_Directory")
    if not root or not os.path.exists(root): return 0
    
    db = load_projects_db()
    
    # 1. Map Filesystem Projects
    fs_projects = set()
    project_to_customer_map = {}
    
    customers = settings.get("Customers", [])
    
    for cust in customers:
        c_path = os.path.join(root, cust)
        if os.path.exists(c_path):
            try:
                for entry in os.scandir(c_path):
                    # It's a project if it's a folder and not hidden
                    if entry.is_dir() and not entry.name.startswith(('.', '_')):
                        proj_name = entry.name
                        fs_projects.add(proj_name)
                        project_to_customer_map[proj_name] = cust
            except: pass
            
    # 2. Identify changes
    db_projects = set(db.sections())
    
    # Remove Zombies (In DB but not in FS)
    to_remove = db_projects - fs_projects
    for p in to_remove:
        db.remove_section(p)
        
    # Add Ghosts (In FS but not in DB)
    to_add = fs_projects - db_projects
    for p in to_add:
        db.add_section(p)
        db.set(p, "Customer", project_to_customer_map[p])
        db.set(p, "Deadline", "--")
    
    if to_remove or to_add:
        save_projects_db(db)
        
    return len(fs_projects)

def load_projects_db() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    if not os.path.exists(PROJECTS_DB):
        with open(PROJECTS_DB, 'w', encoding='utf-8') as f: f.write("") 
    config.read(PROJECTS_DB, encoding='utf-8')
    return config

def save_projects_db(config):
    with open(PROJECTS_DB, 'w', encoding='utf-8') as f: config.write(f)

def open_file_explorer(path: str):
    if not os.path.isdir(path): return
    real_path = os.path.realpath(path)
    try:
        if sys.platform == "win32": os.startfile(real_path)
        elif sys.platform == "darwin": subprocess.run(["open", real_path])
        else: subprocess.run(["xdg-open", real_path])
    except: pass

# --- SETTINGS MENU ---

def command_settings_menu():
    while True:
        settings = load_settings()
        current_dir = settings.get("Projects_Directory", "Not Set")
        
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Colors.BLUE_BG}{Colors.WHITE_TXT}  SETTINGS  {Colors.RESET}")
        print("─" * 60)
        print(f"Production Directory:")
        print(f"{Colors.BOLD}{current_dir}{Colors.RESET}")
        print("─" * 60)
        print(f"{Colors.YELLOW}[E]{Colors.RESET}dit Path  {Colors.GREY}[ESC]{Colors.RESET} Back")
        
        k = getch()
        
        if k == '\x1b': return
        
        elif k.lower() == 'e':
            new_path = input_text_tui("New Path >", default_val=current_dir)
            if new_path == current_dir: continue

            if new_path.startswith('"') and new_path.endswith('"'): 
                new_path = new_path[1:-1]

            if not os.path.exists(new_path):
                print(f"\n{Colors.RED}Directory not found!{Colors.RESET}")
                print("Create it? (y/n)")
                if getch().lower() == 'y':
                    try: os.makedirs(new_path)
                    except Exception as e: print(f"Error: {e}"); time.sleep(1); continue
                else: continue
            
            if os.path.isdir(new_path):
                settings["Projects_Directory"] = new_path
                
                # Clean slate for Customers but let Sync rebuild them
                settings["Customers"] = [] 
                save_settings_file(settings)
                
                # Wipe DB completely on directory change (Start fresh)
                with open(PROJECTS_DB, 'w', encoding='utf-8') as f: f.write("")
                
                print(f"\n{Colors.YELLOW}Scanning new directory structure...{Colors.RESET}")
                
                # 1. Sync Customers
                settings = sync_customers(settings)
                
                # 2. Sync Projects (This populates the list!)
                proj_count = sync_projects_db(settings)
                
                print(f"{Colors.GREEN}Updated! Found {len(settings['Customers'])} clients and {proj_count} projects.{Colors.RESET}")
                time.sleep(2.5)

# --- CUSTOMER MENU & ACTIONS ---

def get_customer_stats(settings):
    """Returns list of dicts: {name, count, color}"""
    root = settings.get("Projects_Directory")
    customers = settings.get("Customers", [])
    colors = settings.get("Customer_Colors", {})
    
    stats = []
    for c in customers:
        c_path = os.path.join(root, c)
        count = 0
        if os.path.exists(c_path):
            try:
                count = len([name for name in os.listdir(c_path) if os.path.isdir(os.path.join(c_path, name)) and not name.startswith(('.', '_'))])
            except: pass
        
        hex_col = colors.get(c, "#FFFFFF")
        stats.append({"name": c, "count": count, "color": hex_col})
    return stats

def draw_customers_dashboard(stats, selected_idx):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Colors.BLUE_BG}{Colors.WHITE_TXT}  CUSTOMERS MANAGEMENT  {Colors.RESET}")
    print("─" * 60)
    print(f"{Colors.HEADER}{'CUSTOMER NAME':<30} | {'PROJECTS':<10} | {'COLOR':<10}{Colors.RESET}")
    print("─" * 60)
    
    limit = 15
    start_idx = 0
    if selected_idx > limit - 1: start_idx = selected_idx - (limit - 1)
    visible = stats[start_idx : start_idx + limit]
    
    for i, s in enumerate(visible):
        real_idx = start_idx + i
        is_sel = (real_idx == selected_idx)
        
        c_ansi = Colors.hex_to_ansi(s['color'])
        name_display = f"{c_ansi}{s['name']}{Colors.RESET}"
        
        line = f"{name_display:<40} | {str(s['count']):<10} | {s['color']:<10}"
        
        if is_sel: print(f"{Colors.INVERT}{s['name']:<30} | {str(s['count']):<10} | {s['color']:<10}{Colors.RESET}")
        else: print(line)

    print("─" * 60)
    print(f"{Colors.YELLOW}[A]{Colors.RESET}dd  {Colors.RED}[D]{Colors.RESET}elete  {Colors.GREEN}[ENTER]{Colors.RESET} Edit  {Colors.GREEN}[O]{Colors.RESET}pen  {Colors.CYAN}[S]{Colors.RESET}ettings  {Colors.GREY}[ESC]{Colors.RESET} Back")

def command_customers_menu():
    settings = load_settings()
    selected_idx = 0
    
    while True:
        settings = load_settings() 
        stats = get_customer_stats(settings)
        
        if not stats: selected_idx = 0
        elif selected_idx >= len(stats): selected_idx = len(stats) - 1
        
        draw_customers_dashboard(stats, selected_idx)
        k = getch()
        
        if k == '\x1b': return 
        elif k == 'UP': selected_idx = max(0, selected_idx - 1)
        elif k == 'DOWN': selected_idx = min(len(stats) - 1, selected_idx + 1)
        elif k == 's': command_settings_menu()
        
        elif k == 'o': 
            if stats:
                c_name = stats[selected_idx]['name']
                open_file_explorer(os.path.join(settings.get("Projects_Directory"), c_name))
        
        elif k == 'a': 
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{Colors.GREEN}--- NEW CUSTOMER ---{Colors.RESET}")
            name = input_text_tui("Customer Name >")
            if name:
                root = settings.get("Projects_Directory")
                path = os.path.join(root, name)
                if not os.path.exists(path):
                    os.makedirs(path)
                    settings["Customers"].append(name)
                    if "Customer_Colors" not in settings: settings["Customer_Colors"] = {}
                    settings["Customer_Colors"][name] = "#FFFFFF"
                    save_settings_file(settings)
        
        elif k == 'd': 
            if stats:
                target = stats[selected_idx]
                os.system('cls' if os.name == 'nt' else 'clear')
                print(f"{Colors.RED_BG}{Colors.WHITE_TXT} DELETE CUSTOMER {Colors.RESET}")
                print(f"Customer: {Colors.BOLD}{target['name']}{Colors.RESET}")
                print(f"{Colors.RED}WARNING: This will delete the folder and ALL contained projects!{Colors.RESET}")
                print("Type 'DELETE' to confirm:")
                confirm = input_text_tui(">")
                if confirm == "DELETE":
                    root = settings.get("Projects_Directory")
                    path = os.path.join(root, target['name'])
                    if os.path.exists(path):
                        try: shutil.rmtree(path)
                        except Exception as e: print(f"Error: {e}"); time.sleep(2)
                    
                    settings["Customers"].remove(target['name'])
                    save_settings_file(settings)
                    
                    db = load_projects_db()
                    sections_to_remove = []
                    for section in db.sections():
                        if db.get(section, "Customer") == target['name']:
                            sections_to_remove.append(section)
                    for s in sections_to_remove: db.remove_section(s)
                    save_projects_db(db)
        
        elif k == '\r' or k == '\n': 
            if stats:
                target = stats[selected_idx]
                edit_customer_interactive(target['name'], settings)

def edit_customer_interactive(old_name, settings):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Colors.BLUE_BG}{Colors.WHITE_TXT} EDIT CUSTOMER {Colors.RESET}")
    print(f"Editing: {old_name}")
    print("-" * 30)
    
    new_name = input_text_tui("New Name (Enter to skip) >", default_val=old_name)
    old_color = settings.get("Customer_Colors", {}).get(old_name, "#FFFFFF")
    new_color = input_text_tui("New HEX Color (e.g #FF0000) >", default_val=old_color)
    
    root = settings.get("Projects_Directory")
    old_path = os.path.join(root, old_name)
    new_path = os.path.join(root, new_name)
    
    if new_name != old_name:
        if os.path.exists(old_path):
            renamed = False
            for i in range(3):
                try:
                    shutil.move(old_path, new_path)
                    renamed = True
                    break
                except PermissionError: time.sleep(0.5)
                except Exception as e:
                    print(f"{Colors.RED}FS Error: {e}{Colors.RESET}")
                    time.sleep(2); return
            
            if not renamed:
                print(f"{Colors.RED}Error: Folder is locked.{Colors.RESET}")
                time.sleep(2); return

            try:
                if old_name in settings["Customers"]:
                    idx = settings["Customers"].index(old_name)
                    settings["Customers"][idx] = new_name
                
                if old_name in settings.get("Customer_Colors", {}):
                    col = settings["Customer_Colors"].pop(old_name)
                    settings["Customer_Colors"][new_name] = col
                
                db = load_projects_db()
                for section in db.sections():
                    if db.get(section, "Customer") == old_name:
                        db.set(section, "Customer", new_name)
                save_projects_db(db)
            except: pass

    if "Customer_Colors" not in settings: settings["Customer_Colors"] = {}
    settings["Customer_Colors"][new_name] = new_color
    
    save_settings_file(settings)
    print(f"{Colors.GREEN}Saved!{Colors.RESET}")
    time.sleep(0.5)

# --- MAIN PROJECTS DASHBOARD ---

def get_project_list_flat():
    db = load_projects_db()
    settings = load_settings()
    colors = settings.get("Customer_Colors", {})
    
    projects = []
    for section in db.sections():
        cust = db.get(section, "Customer", fallback="?")
        projects.append({
            "id": section,
            "customer": cust,
            "deadline": db.get(section, "Deadline", fallback="--"),
            "color": colors.get(cust, "#FFFFFF")
        })
    projects.reverse()
    return projects

def draw_dashboard(projects, selected_idx):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Colors.BLUE_BG}{Colors.WHITE_TXT}  PROJECT MANAGEMENT  {Colors.RESET}")
    print(f"{Colors.GREY}Database: {len(projects)} projects{Colors.RESET}")
    print("─" * 60)
    print(f"{Colors.HEADER}{'PROJECT':<30} | {'CUSTOMER':<15} | {'DEADLINE':<10}{Colors.RESET}")
    print("─" * 60)
    
    limit = 15
    start_idx = 0
    if selected_idx > limit - 1: start_idx = selected_idx - (limit - 1)
    visible = projects[start_idx : start_idx + limit]
    
    if not projects:
        print(f"\n   {Colors.GREY}(No projects. Press 'a' to create){Colors.RESET}")
    
    for i, p in enumerate(visible):
        real_idx = start_idx + i
        is_sel = (real_idx == selected_idx)
        
        # --- SMART DISPLAY NAME CLEANING ---
        raw_name = p['id']
        cust_name = p['customer']
        
        display_name = raw_name
        
        # Case insensitive check
        if cust_name.lower() in raw_name.lower():
            # Remove customer name (case insensitive replace)
            start_index = raw_name.lower().find(cust_name.lower())
            end_index = start_index + len(cust_name)
            
            # Remove the name from the string
            temp_name = raw_name[:start_index] + raw_name[end_index:]
            
            # Clean leading separators/spaces
            # We strip common separators: space, dash, underscore
            display_name = temp_name.lstrip(" -_")
            
            # Fallback: if name became empty (project name WAS customer name), keep original
            if not display_name: display_name = raw_name

        # Truncate
        p_display = (display_name[:27] + '..') if len(display_name) > 29 else display_name
        c_display = (cust_name[:13] + '..') if len(cust_name) > 15 else cust_name
        
        # Apply Color
        c_ansi = Colors.hex_to_ansi(p['color'])
        c_final = f"{c_ansi}{c_display:<15}{Colors.RESET}"
        
        line = f"{p_display:<30} | {c_final} | {p['deadline']:<10}"
        
        if is_sel: print(f"{Colors.INVERT}{p_display:<30} | {c_display:<15} | {p['deadline']:<10}{Colors.RESET}")
        else: print(f"{Colors.BOLD}{line}{Colors.RESET}")

    print("─" * 60)
    print(f"{Colors.YELLOW}[A]{Colors.RESET}dd  {Colors.RED}[D]{Colors.RESET}elete  {Colors.GREEN}[O]{Colors.RESET}pen  {Colors.CYAN}[C]{Colors.RESET}ustomers  {Colors.CYAN}[S]{Colors.RESET}ettings  {Colors.GREEN}[ENTER]{Colors.RESET} Edit")

def edit_project_interactive(old_title):
    db = load_projects_db()
    settings = load_settings()
    
    if not db.has_section(old_title): return

    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Colors.BLUE_BG}{Colors.WHITE_TXT} EDIT PROJECT {Colors.RESET}")
    print(f"Project: {old_title}")
    
    new_title = input_text_tui("New Title >", default_val=old_title)
    
    if new_title == old_title: return

    cust = db.get(old_title, "Customer")
    root = settings.get("Projects_Directory")
    
    old_folder_name = old_title
    if settings.get("Title_AddCustomer", False): old_folder_name = f"{cust} - {old_title}"
    new_folder_name = new_title
    if settings.get("Title_AddCustomer", False): new_folder_name = f"{cust} - {new_title}"
    
    old_path = os.path.join(root, cust, old_folder_name)
    new_path = os.path.join(root, cust, new_folder_name)
    
    if not os.path.exists(old_path):
         old_path = os.path.join(root, cust, old_title)

    if os.path.exists(old_path):
        renamed = False
        for i in range(3):
            try:
                shutil.move(old_path, new_path)
                renamed = True
                break
            except PermissionError: time.sleep(0.5)
            except Exception as e:
                print(f"{Colors.RED}FS Error: {e}{Colors.RESET}")
                time.sleep(2); return
        
        if not renamed:
            print(f"{Colors.RED}Error: Folder locked.{Colors.RESET}")
            time.sleep(2); return
    
    data = dict(db.items(old_title))
    db.remove_section(old_title)
    db.add_section(new_title)
    for k, v in data.items(): db.set(new_title, k, v)
    
    save_projects_db(db)
    print(f"{Colors.GREEN}Project updated.{Colors.RESET}")
    time.sleep(1)

def command_view_interactive():
    settings = load_settings()
    # --- AUTO-SYNC ON STARTUP ---
    settings = sync_customers(settings)
    sync_projects_db(settings)
    
    selected_idx = 0
    
    while True:
        projects = get_project_list_flat()
        if not projects: selected_idx = 0
        elif selected_idx >= len(projects): selected_idx = len(projects) - 1
        
        draw_dashboard(projects, selected_idx)
        k = getch()
        
        if k == 'q' or k == '\x1b': sys.exit(0)
        elif k == 'UP': selected_idx = max(0, selected_idx - 1)
        elif k == 'DOWN': selected_idx = min(len(projects) - 1, selected_idx + 1)
        elif k == 's': command_settings_menu()
        elif k == 'c': command_customers_menu()
        elif k == 'a': command_add_interactive(); selected_idx = 0
        elif k == 'd': 
            if projects:
                command_delete_interactive(projects[selected_idx]['id'])
                if selected_idx >= len(projects) - 1: selected_idx = max(0, selected_idx - 1)
        elif k == 'o':
            if projects: open_project_folder(projects[selected_idx]['id'])
        elif k == '\r' or k == '\n':
             if projects: edit_project_interactive(projects[selected_idx]['id'])

def open_project_folder(project_name):
    settings = load_settings()
    db = load_projects_db()
    root = settings.get("Projects_Directory")
    cust = db.get(project_name, "Customer", fallback="")
    path1 = os.path.join(root, cust, project_name)
    path2 = os.path.join(root, cust, f"{cust} - {project_name}")
    
    found = None
    if os.path.exists(path1): found = path1
    elif os.path.exists(path2): found = path2
    
    if found: open_file_explorer(found)
    else:
        print(f"\n{Colors.RED}Folder not found!{Colors.RESET}")
        time.sleep(1)

def command_add_interactive():
    settings = load_settings()
    settings = sync_customers(settings)
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Colors.GREEN}--- NEW PROJECT ---{Colors.RESET}")
    
    customers = settings.get("Customers", [])
    if not customers:
        print(f"No customers found in: {settings.get('Projects_Directory')}")
        time.sleep(2); return

    print("Customer :")
    for i, c in enumerate(customers):
        print(f"  {Colors.CYAN}[{i+1}]{Colors.RESET} {c}")
    
    sel_cust = None
    while not sel_cust:
        res = input_text_tui("Number >")
        if not res: return
        try:
            idx = int(res) - 1
            if 0 <= idx < len(customers): sel_cust = customers[idx]
        except: pass
    
    title = ""
    while not title:
        title = input_text_tui("Project Title >")
        if not title: return

    events_to_create = []
    deadline_str = "N/A"
    
    if settings.get("GoogleAPI", False):
        receiver_path = os.path.join(SCRIPT_DIR, "GoogleCalendar.py")
        temp_dir = tempfile.gettempdir()
        exchange_file = os.path.join(temp_dir, "ProjectManager_date.tmp")
        
        if os.path.exists(receiver_path):
            steps = settings.get("Steps", []) or ["DEADLINE"]
            print(f"\n{Colors.YELLOW}Scheduling...{Colors.RESET}")
            for step in steps:
                if os.path.exists(exchange_file): os.remove(exchange_file)
                display = f"{title} ({step})"
                
                # UPDATED LINE: Added "--title" before the display variable
                subprocess.run([sys.executable, receiver_path, "--title", display, sel_cust])
                
                if os.path.exists(exchange_file):
                    with open(exchange_file, 'r') as f: date_s = f.read().strip()
                    if date_s:
                        d_obj = datetime.strptime(date_s, "%d-%m-%y")
                        evt_name = f"{sel_cust} - {title} - {step}" if step != "DEADLINE" else f"{sel_cust} - {title} - DEADLINE"
                        events_to_create.append({"title": evt_name, "date": d_obj, "raw": date_s})
                        print(f"  -> {step}: {Colors.GREEN}{date_s}{Colors.RESET}")
                    else: print(f"  -> {step}: {Colors.GREY}Skipped{Colors.RESET}")
                else: print(f"  -> {step}: {Colors.GREY}Skipped{Colors.RESET}")

    if events_to_create:
        events_to_create.sort(key=lambda x: x['date'])
        deadline_str = events_to_create[-1]['raw']

    print(f"\nCreate '{title}' for '{sel_cust}'? (Enter=YES, Esc=NO)")
    k = getch()
    if k == '\x1b': return

    if events_to_create and GoogleCalendar:
        try:
            srv = GoogleCalendar.get_calendar_service(APP_DIR)
            cals = GoogleCalendar.get_writable_calendars(srv)
            if cals:
                cal_id = cals[0]['id'] 
                for e in events_to_create:
                    GoogleCalendar.create_event(srv, cal_id, e['title'], e['date'])
                print(f"{Colors.GREEN}[API] Calendar updated.{Colors.RESET}")
        except: pass

    root = settings.get("Projects_Directory")
    cust_path = os.path.join(root, sel_cust)
    if not os.path.exists(cust_path): os.makedirs(cust_path)
    
    final_name = title
    if settings.get("Title_AddCustomer", False): final_name = f"{sel_cust} - {title}"
    
    final_path = os.path.join(cust_path, final_name)
    
    if os.path.exists(TEMPLATE_MAKER_SCRIPT):
        subprocess.run([sys.executable, TEMPLATE_MAKER_SCRIPT, cust_path, final_name])
    else: os.makedirs(final_path, exist_ok=True)

    db = load_projects_db()
    if not db.has_section(title): db.add_section(title)
    db.set(title, "Customer", sel_cust)
    db.set(title, "Deadline", deadline_str)
    save_projects_db(db)
    print(f"{Colors.GREEN}Project created!{Colors.RESET}")
    time.sleep(1)

def command_delete_interactive(target_name):
    db = load_projects_db()
    settings = load_settings()
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Colors.RED_BG}{Colors.WHITE_TXT} DELETION {Colors.RESET}")
    print(f"Project : {Colors.BOLD}{target_name}{Colors.RESET}")
    print(f"Confirm? (Press 'y')")
    if getch().lower() != 'y': return

    cust = db.get(target_name, "Customer")
    root = settings.get("Projects_Directory")
    p1 = os.path.join(root, cust, target_name)
    p2 = os.path.join(root, cust, f"{cust} - {target_name}")
    
    for p in [p1, p2]:
        if os.path.exists(p):
            try: shutil.rmtree(p); print(f"Deleted: {p}")
            except: pass
    
    db.remove_section(target_name)
    save_projects_db(db)
    time.sleep(1)

if __name__ == "__main__":
    try: command_view_interactive()
    except KeyboardInterrupt: sys.exit(0)