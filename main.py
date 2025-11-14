import os
import sys
import json
import logging
import shutil 
import argparse
import configparser
import re
import subprocess
from datetime import datetime
from tkinter import (
    Tk, messagebox
)

# --- CONFIGURATION ---
SETTINGS_FILE = "settings.json"
LOG_FILE = "mainpy.log"
SCRIPT_VERSION = "7.0"
# Name of the AHK configuration file to generate
PATHFILE = None
INCLUDE_OUTPUT = None

# AHK local variable name to use for the settings.json location
AHK_VAR_SETTINGS = "path_settings"
AHK_VAR_PYTHON_CMD = "cmd_python"
AHK_VAR_FINAL_SCRIPT = "StartFinalScript"
# The 'type' of item in settings.json to search for to find the config path
json_keyConfig = "Configuration"



# The return code to indicate an error to the AHK script
EXIT_CODE_ERROR = 1

# --- LOGGING SETUP ---
def setup_logging(enable_file_log=False):
    """
    Initializes the logging system. StreamHandler (console) is always active.
    FileHandler (.log) is added only if enable_file_log is True.
    """
       
    # The StreamHandler is always active for console display
    handlers = [
        logging.StreamHandler(sys.stdout)
    ]
    
    if enable_file_log:
        # If --log is specified, add the FileHandler
        # Writes logs to the file, overwriting previous ones
        handlers.append(logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'))

    # Initialize logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

def exit_script(code=0):
    """
    Closes the script with the specified exit code and displays a
    user-friendly message box.
    """
    if code == 0:
        logging.info(f"Operation finished successfully. Exit code: {code}")
    else:
        logging.error(f"Operation finished with error. Exit code: {code}")
    
    # Display a message box to inform the user of the outcome.
    # The main Tk window is hidden to avoid showing an empty window.
    root = Tk()
    root.withdraw() # Hide the main window
    
    if code == 0:
        messagebox.showinfo("Success", "The project structure has been verified and/or created successfully.")
    else:
        # FATAL ERROR. The calling AHK script is expected to detect exit code 1 and halt.
        messagebox.showerror("Fatal Error", f"A critical error occurred (see {LOG_FILE}). The process is terminated.")
    
    root.destroy()

    for handler in logging.root.handlers:
        handler.flush()

    sys.exit(code)

# =================================================================
# INTEGRATED AHK PARSER
# =================================================================
def retrieve_ahk_variables(ahk_filepath):
    """
    Reads an AutoHotkey file (v2 variable declaration style) and attempts
    to extract 'path_settings' and 'StartFinalScript' variables.

    Args:
        ahk_filepath (str): The path to the AHK file to read.

    Returns:
        dict: A dictionary containing the resolved variables and their values.
    """
    resolved_vars = {}
    
    # Regular expression to capture: VARIABLE := VALUE ; (with or without quotes, with or without comments)
    # 1: Variable name
    # 2: Raw value (everything after := until EOL, or ; at EOL)
    variable_pattern = re.compile(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:=\s*(.*?)\s*(?:;.*)?$', re.MULTILINE)
    
    logging.info(f"--- Starting AHK Parse of {os.path.basename(ahk_filepath)} ---")
    
    try:
        with open(ahk_filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        logging.error(f"AHK file not found: {ahk_filepath}")
        return {}
    except Exception as e:
        logging.error(f"Error reading AHK file {ahk_filepath}: {e}")
        return {}

    # First pass: Capture all raw definitions
    raw_definitions = variable_pattern.findall(content)

    # Second pass: Variable resolution
    # We only focus on the specific variables we need
    vars_to_resolve = [AHK_VAR_SETTINGS, AHK_VAR_FINAL_SCRIPT]
    
    # Build a reference map for resolution
    definitions_map = {name: value.strip() for name, value in raw_definitions}

    for name in vars_to_resolve:
        if name in definitions_map:
            value_expression = definitions_map[name]
            
            # Remove quotes from a string literal
            if value_expression.startswith('"') and value_expression.endswith('"'):
                resolved_value = value_expression[1:-1].replace('""', '"') # Remove quotes and handle AHK escapes
            else:
                # If it's not a quoted literal string, take it as-is.
                resolved_value = value_expression 

            # Replace double backslashes (AHK escape) with a single backslash for Python
            final_value = resolved_value.replace('\\\\', '\\')
            
            resolved_vars[name] = final_value
            logging.info(f"Resolved variable: {name} = '{final_value}' (Raw expression: {value_expression})")
        else:
            logging.warning(f"Variable '{name}' not found in the AHK file.")
            
    logging.info(f"--- Finished AHK Parse ---")
    
    return resolved_vars

def read_ahk_variables(pathfile_path):
    """
    Attempts to load paths (settings_path and StartFinalScript) from the AHK file.
    
    Args:
        pathfile_path (str): The absolute path to the AHK file (path.ahk).
        
    Returns:
        tuple or None: (settings_json_path, StartAHKScriptOutput) if successful, else None.
    """
    parsed_data = retrieve_ahk_variables(pathfile_path)

    settings_path = parsed_data.get(AHK_VAR_SETTINGS)
    StartAHKScriptOutput = parsed_data.get(AHK_VAR_FINAL_SCRIPT)

    if not settings_path or not StartAHKScriptOutput:
        logging.error(f"AHK variables '{AHK_VAR_SETTINGS}' or '{AHK_VAR_FINAL_SCRIPT}' are missing or invalid in '{pathfile_path}'.")
        return None
    
    # Replace forward slashes with correct OS separators, just in case
    settings_path = settings_path.replace('/', os.sep)
    
    logging.info(f"Settings path (from AHK): {settings_path}")
    logging.info(f"Final Script path (from AHK): {StartAHKScriptOutput}")

    return settings_path, StartAHKScriptOutput

def load_settings_json(settings_json_path):
    """
    Attempts to load and validate the settings.json file.

    Args:
        settings_json_path (str): The path to the settings.json file.

    Returns:
        tuple or None: (json_data, settings_abs_path) if successful, else None.
    """
    logging.info(f"Attempting to load settings.json from: {settings_json_path}")
    settings_abs_path = os.path.abspath(settings_json_path)

    if not os.path.exists(settings_abs_path):
        logging.error(f"settings.json file not found at: {settings_abs_path}")
        return None

    try:
        with open(settings_abs_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        logging.info(f"settings.json loaded successfully from: {settings_abs_path}")
        return json_data, settings_abs_path
    
    except json.JSONDecodeError as e:
        logging.error(f"JSON Decode Error in {settings_abs_path}: {e}")
        return None
    except Exception as e:
        logging.error(f"Error reading settings.json file: {e}")
        return None

def find_config_dir_path(settings, json_keyConfig_name):
    """
    Searches for the configuration directory path (relative to CWD) within the 
    settings.json structure, using 'name' or 'type'.
    """
    for item in settings.get('structure', []):
        if item.get('type') == json_keyConfig_name:
            # The 'type' key remains the logical reference to find the element.
            # The relative path is determined by get_folder_name.
            folder_name = get_folder_name(item) 
            if folder_name:
                return folder_name
            else:
                # If neither 'name' nor 'type' is found, this is an error.
                return None 
    return None

def get_expected_paths(structure, base_path="."):
    """
    Generates a list of expected folder paths from the JSON structure.
    Uses 'name' as the folder name if present, otherwise 'type', and reconstructs 
    the path recursively.
    """
    expected_paths = []
    for item in structure:
        # Use the new validation function
        include_status = is_valid_include_setting(item)
        if include_status == 'ERROR':
            raise ValueError(f"Validation Error: 'is_include' key must be 'true' or 'false' (current: {item.get('is_include')}) in element: {item.get('type')}.")
        
        # If 'is_include' is 'false', we do not include the path.
        if include_status is False:
            # We include the path, but we will NOT include its AHK includes later.
            pass # Continue to check children as they might be "true"
        
        item_folder_name = get_folder_name(item)
        
        # The folder must always be checked/created if it has a valid folder name.
        if item_folder_name:
            current_path = os.path.join(base_path, item_folder_name)
            expected_paths.append(current_path)
            if item.get('children'):
                # Recursion, regardless of the parent's 'is_include' status
                expected_paths.extend(get_expected_paths(item['children'], current_path))
                
    return expected_paths

def compare_structure(expected_paths, is_initial_run):
    """
    Compares expected paths with the actual folder structure and asks
    for confirmation if folders are missing.
    """
    missing_folders = []
    for path in expected_paths:
        if not os.path.exists(path):
            missing_folders.append(path)

    if missing_folders:
        logging.warning(f"{len(missing_folders)} folders are missing:")
        for folder in missing_folders:
            logging.warning(f"- {folder}")

        if not is_initial_run:
            # Only ask for confirmation if it's not a forced initial run
            root = Tk()
            root.withdraw()
            msg = (
                f"WARNING: {len(missing_folders)} folders from the expected structure are missing.\n\n"
                f"Do you want the script to create them now?\n"
                f"(Cancel will stop the script)."
            )
            response = messagebox.askyesno("Structure Check", msg)
            root.destroy()

            if not response:
                logging.info("Structure creation cancelled by user.")
                exit_script(EXIT_CODE_ERROR)
    
    return missing_folders

def create_structure(settings):
    """
    Creates folders based on the structure defined in settings.json.
    Creation is unconditional regarding 'is_include', as the folder
    must exist for the structure.
    """
    logging.info("Starting folder structure creation...")
    
    def recursive_create(structure, base_path="."):
        for item in structure:
            # 1. Key validation, but no action here.
            # The validation error is raised in get_expected_paths, which main_build intercepts.
            include_status = is_valid_include_setting(item)
            
            # If status is ERROR, do nothing for creation/recursion
            # as the process will stop in main_build shortly.
            if include_status == 'ERROR':
                continue
                
            item_folder_name = get_folder_name(item)
            
            if item_folder_name:
                folder_path = os.path.join(base_path, item_folder_name)
                try:
                    # 2. Folder creation/verification (ALWAYS DONE)
                    os.makedirs(folder_path, exist_ok=True)
                    logging.info(f"Folder created/verified: {folder_path}")
                except Exception as e:
                    logging.error(f"Error creating folder {folder_path}: {e}")
                    raise # Rethrow the error to the main function
                
                # 3. Recursion (ALWAYS DONE)
                if item.get('children'):
                    recursive_create(item['children'], folder_path)

    try:
        recursive_create(settings.get('structure', []))
        logging.info("Folder structure creation finished.")
    except Exception:
        # Ensure the script stops on a folder creation error
        exit_script(EXIT_CODE_ERROR)

def clean_ahk_path(path_to_clean):
    """
    Cleans a file path for use in an AHK string by replacing single
    backslashes with double backslashes.
    """
    return path_to_clean.replace(os.sep, "\\\\")

def post_build_actions(source_path, json_data, is_initial_run, StartAHKScriptOutput):
    """
    Handles final actions: moves settings.json on initial run and writes the
    root 'paths.ahk' file with a relative path to settings.json for portability.
    """
    # 1. Find the config directory path
    config_relative_path = find_config_dir_path(json_data, json_keyConfig)
    if not config_relative_path:
        logging.error(f"Could not find the configuration directory path ('type': '{json_keyConfig}') in settings.json during post-build.")
        exit_script(EXIT_CODE_ERROR)

    config_absolute_path = os.path.join(os.getcwd(), config_relative_path)
    
    # 2. Define the destination for settings.json
    json_destination_path = os.path.join(config_absolute_path, SETTINGS_FILE)

    # 3. Move settings.json if it's an initial run and the source is different
    if is_initial_run and os.path.abspath(source_path) != os.path.abspath(json_destination_path):
        try:
            shutil.move(source_path, json_destination_path)
            logging.info(f"Successfully moved '{os.path.basename(source_path)}' to '{config_relative_path}'.")
        except Exception as e:
            logging.error(f"Error moving '{os.path.basename(source_path)}' to '{config_relative_path}': {e}")
            exit_script(EXIT_CODE_ERROR)
    
    # 4. Write the PATHFILE (e.g., paths.ahk) to the ROOT directory
    pathfile_output_path = os.path.join(os.getcwd(), PATHFILE)
    
    # Create a relative path for settings.json from the project root for AHK
    settings_path_for_ahk = os.path.relpath(json_destination_path, os.getcwd())
    settings_path_for_ahk = settings_path_for_ahk.replace(os.sep, "\\")

    # The content for paths.ahk using the relative path
    pathfile_content = (
        f'{AHK_VAR_SETTINGS} := "{settings_path_for_ahk}"\n'
        f'{AHK_VAR_FINAL_SCRIPT} := "{StartAHKScriptOutput}"'
    )
    
    try:
        # Check if the file exists and if its content is the same to avoid unnecessary writes
        rewrite = True
        if os.path.exists(pathfile_output_path):
            with open(pathfile_output_path, 'r', encoding='utf-8') as f:
                if f.read().strip() == pathfile_content.strip():
                    rewrite = False
                    logging.info(f"'{PATHFILE}' is already up-to-date. Skipping write.")
        
        if rewrite:
            with open(pathfile_output_path, 'w', encoding='utf-8') as f:
                f.write(pathfile_content)
            logging.info(f"Successfully wrote configuration to '{PATHFILE}'.")
            
    except Exception as e:
        logging.error(f"Error writing to '{PATHFILE}': {e}")
        exit_script(EXIT_CODE_ERROR)
        
    # Return the absolute path for the rest of the Python script's execution,
    # and the relative path for the config directory.
    return json_destination_path, config_relative_path

# =================================================================
# HELPER FUNCTIONS FOR SETTINGS.AHK GENERATION
# =================================================================

def get_folder_name(item):
    """
    Determines the folder name to use. Prefers 'name' if present, otherwise 'type'.
    """
    # Use 'name' if it is present and non-empty, otherwise use 'type'.
    return item.get('name') or item.get('type')

def format_ahk_value(value):
    """
    Formats a Python value into a correct AHK literal string.
    """
    if isinstance(value, bool):
        return str(value).lower()  # True -> true, False -> false
    if isinstance(value, (int, float)):
        return str(value)
    if value is None:
        return '""'  # Represent None as an empty string
    
    # For strings, escape quotes (") to ("") and surround with quotes
    str_val = str(value).replace('"', '""')
    return f'"{str_val}"'

def is_valid_path_setting(item):
    """
    Validates and returns the boolean value of 'is_path'.
    Defaults to True if the key is absent.
    Returns 'ERROR' for invalid values.
    """
    path_setting = item.get('is_path', 'true') # Default 'true' if absent
    
    if not isinstance(path_setting, str) or not path_setting.strip():
        if 'is_path' not in item:
            return True # Absent key is valid, defaults to True
        return 'ERROR' # Empty or non-string
        
    path_setting_lower = path_setting.lower()
    
    if path_setting_lower == 'true':
        return True
    elif path_setting_lower == 'false':
        return False
    else:
        return 'ERROR' # Invalid string

def generate_nested_path_structure(structure_list, parent_class_path_str, parent_base_str, indent_level):
    """
    Recursive function to generate AHK code for a NESTED class structure,
    mimicking the sample.ahk file.
    
    Args:
        structure_list (list): The list of node items (from settings.json).
        parent_class_path_str (str): The AHK path of the parent class (e.g., "A_Path" or "A_Path.Library").
        parent_base_str (str): The AHK variable for the parent's base path (e.g., "A_Path.rootDir" or "A_Path.Library._base").
        indent_level (int): The current indentation level.
    """
    ahk_code_lines = []
    indent = "    " * indent_level

    for item in structure_list:
        class_type = item.get("type")
        if not class_type:
            logging.warning(f"Item skipped for AHK path class, 'type' is missing: {item}")
            continue
        
        # --- Check if THIS path should be included at all ---
        path_status = is_valid_path_setting(item)
        if path_status == 'ERROR':
            logging.error(f"Invalid 'is_path' value for type '{class_type}'. Skipping class/var generation.")
            continue
        if path_status is False:
            logging.info(f"Skipping AHK path generation for '{class_type}' (is_path: false).")
            continue
        # --- End Check ---
        
        item_folder_name = get_folder_name(item)
        if not item_folder_name:
            logging.warning(f"Item type '{class_type}' has no folder name ('name' or 'type'). Skipping path generation.")
            continue

        ahk_path_segment = f'\\{item_folder_name}'
        
        # --- NOUVELLE LOGIQUE : PRÉ-FILTRER LES ENFANTS ---
        children = item.get("children", [])
        valid_path_children = []
        if children:
            for child in children:
                # Vérifier si cet enfant va réellement générer un chemin
                child_class_type = child.get("type")
                if not child_class_type:
                    continue
                
                child_path_status = is_valid_path_setting(child)
                if child_path_status == 'ERROR' or child_path_status is False:
                    continue
                    
                if not get_folder_name(child):
                    continue
                
                # Si on arrive ici, l'enfant est valide
                valid_path_children.append(child)
        # --- Fin de la nouvelle logique ---

        # MODIFIÉ : Vérifier la liste pré-filtrée
        if valid_path_children:
            # --- This item has valid children, so it becomes a CLASS ---
            current_class_name = class_type
            
            # 1. Start Class definition
            ahk_code_lines.append(f'\n{indent}class {current_class_name} extends A_Path.PathNode')
            ahk_code_lines.append(f'{indent}{{')
            
            # 2. Define its 'static _base'
            line = f'{indent}    static _base := {parent_base_str} "{ahk_path_segment}"'
            ahk_code_lines.append(line)
            
            # 3. Recurse for its children
            new_parent_class_path = f"{parent_class_path_str}.{current_class_name}"
            new_parent_base_str = f"{new_parent_class_path}._base"
            
            child_lines = generate_nested_path_structure(
                valid_path_children, # MODIFIÉ : Utiliser la liste filtrée
                new_parent_class_path,
                new_parent_base_str,
                indent_level + 1
            )
            
            if child_lines:
                ahk_code_lines.append(f'') # Add a newline for readability
                ahk_code_lines.extend(child_lines)
            
            # 4. Close Class
            ahk_code_lines.append(f'{indent}}}')
            
        else:
            # --- No valid children, so it becomes a STATIC VARIABLE ---
            current_var_name = class_type
            
            # Determine the base variable (e.g., A_Path.rootDir or this._base)
            base_var_to_use = "this._base"
            if parent_class_path_str == "A_Path": 
                # This item is a direct child of A_Path (like Configuration)
                base_var_to_use = parent_base_str # which is A_Path.rootDir
            
            line = f'{indent}static {current_var_name} := {base_var_to_use} "{ahk_path_segment}"'
            ahk_code_lines.append(line)
    
    return ahk_code_lines

def is_valid_include_setting(item):
    """
    Validates and returns if the item should be included in the AHK includes.
    """
    # If the key is not present, default to 'true'
    include_setting = item.get('is_include', 'true') 
    
    # If the value is not a string or is empty, return 'ERROR'
    if not isinstance(include_setting, str) or not include_setting.strip():
        # If the key was missing (using default 'true'), do not return 'ERROR'
        if 'is_include' not in item:
            return True
        # Otherwise, it's an empty or malformed key
        return 'ERROR' 
        
    include_setting_lower = include_setting.lower()
    
    if include_setting_lower == 'true':
        return True
    elif include_setting_lower == 'false':
        return False
    else:
        # Any other string is invalid
        return 'ERROR'  

def extract_ahk_generated_content(settings, FINAL_rootName, include_file_dir):
    """
    Generates the AHK lines for the NESTED class structure and the includes.

    Returns:
        tuple: (structure_lines, include_string)
    """
    structure_lines = []
    structure_list = settings.get("structure", [])
    
    # --- 1. New class structure generation (Nested) ---
    if FINAL_rootName != "Unknown_Root":
        # Start of the root class
        structure_lines.append(f'class A_Path\n{{')
        
        # Add the base rootDir
        structure_lines.append(f"    static rootDir := A_ScriptDir")
        
        # Add any other root-level properties from settings.json
        # (e.g., if you have "Version": "1.0" at the root of settings.json)
        for key, val in settings.items():
            if key not in ("structure", "RootName"):
                formatted_val = format_ahk_value(val)
                structure_lines.append(f"    static {key} := {formatted_val}")

        # Add the helper PathNode class (from sample.ahk)
        structure_lines.append(f'\n    class PathNode {{')
        structure_lines.append(f'        static _base := ""')
        structure_lines.append(f'        static __Call() {{')
        structure_lines.append(f'            return this._base')
        structure_lines.append(f'        }}')
        structure_lines.append(f'    }}\n')

        # Recursive call for children path variables
        path_var_lines = generate_nested_path_structure(
            structure_list, 
            "A_Path",         # parent_class_path_str
            "A_Path.rootDir", # parent_base_str
            1                 # indent_level (starts at 1 for 4 spaces)
        )
        structure_lines.extend(path_var_lines)
        
        structure_lines.append(f'\n}}') # Close the root class

    # --- 2. Generate #include directives (This part is unchanged) ---
    base_project_dir = os.getcwd() 
    include_string = generate_ahk_includes(structure_list, FINAL_rootName, base_project_dir, json_keyConfig, include_file_dir)
    
    return "\n".join(structure_lines), include_string

def generate_ahk_includes(structure_list, FINAL_rootName, base_dir, json_keyConfig_name, include_file_dir):
    """
    Recursively scans the project structure for .ahk files and generates
    #include declarations, grouped by Active context. Paths are relative
    to the generated include file itself.
    """
    # Use a dictionary to group includes by their WinActive condition.
    # The key None is reserved for global includes (no HotIf).
    grouped_includes = {}

    def find_files_recursive(node_list, fs_path_prefix, ahk_path_prefix, inherited_win_active=None, inherited_include_status=True):
        """Recursive helper to find and sort files."""
        
        for node in node_list:
            node_type = node.get("type")

            # Get the status of the current node (True, False, or 'ERROR')
            node_include_status = is_valid_include_setting(node)
        
            if node_include_status == 'ERROR':
                # Error is handled upstream, but this is a safety net.
                logging.error(f"Include validation failed for node {node_type}. Skipping includes.")
                continue
        
            # The effective include status is a combination of inherited and local status.
            # If inheritance is False, effective must be False.
            current_effective_include_status = inherited_include_status and node_include_status
            
            # Determine the winActive for this node: either its own or inherited.
            current_win_active = node.get("Active", inherited_win_active)

            # 1. Completely ignore the configuration directory
            if node_type == json_keyConfig_name:
                logging.info(f"Skipping include scan for node type: {node_type}")
                if node.get("children"):
                    find_files_recursive(node.get("children"), fs_path_prefix, ahk_path_prefix, current_win_active)
                continue
                
            if not node_type:
                if node.get("children"):
                    find_files_recursive(node.get("children"), fs_path_prefix, ahk_path_prefix, current_win_active)
                continue
                
            # 2. Reconstruct the filesystem path (fs_path)
            current_fs_path_segment = get_folder_name(node)
            full_fs_path = os.path.normpath(os.path.join(base_dir, fs_path_prefix, current_fs_path_segment))
            
            # 3. Reconstruct the AHK class path (ahk_path)
            current_ahk_path_list = ahk_path_prefix + [node_type]
            
            # 4. Scan for .ahk files in the node's path
            found_ahk_files = []

            # --- Scan condition with EFFECTIVE status ---
            if current_effective_include_status is True and os.path.isdir(full_fs_path):
                logging.debug(f"Scanning for AHK files in: {full_fs_path}")
                # Iterate only the current directory (no recursion)
                for item_name in os.listdir(full_fs_path):
                    if item_name.lower().endswith(".ahk") and os.path.isfile(os.path.join(full_fs_path, item_name)):
                        
                        # Get the full absolute path of the found .ahk file
                        found_file_full_path = os.path.join(full_fs_path, item_name)
                        
                        # Create a relative path from the location of the generated include file
                        relative_path_for_include = os.path.relpath(found_file_full_path, include_file_dir)
                        
                        logging.debug(f"AHK file found: {relative_path_for_include}")
                        
                        # Format for AHK (backslashes)
                        ahk_include_path = relative_path_for_include.replace(os.sep, "\\")

                        # Use the new relative path
                        found_ahk_files.append(f'#include "{ahk_include_path}"')
            elif current_effective_include_status is False:
                # This log confirms the scan was skipped due to 'false' inheritance
                logging.info(f"Skipping AHK includes for node type: {node_type} (effective 'is_include': 'false')")
            
            # 5. Assign found files to the correct list
            if found_ahk_files:
                # Use None for all global conditions ("Windows" or none)
                if current_win_active and current_win_active.lower() == "windows":
                    context_key = None
                    context_description = "Global (Windows/Always Active)"
                elif current_win_active:
                    context_key = current_win_active # Specific context (e.g., ahk_class Premiere Pro)
                    context_description = current_win_active
                else:
                    context_key = None # Totally global context (no winActive)
                    context_description = "Global (Always Active)"

                if context_key not in grouped_includes:
                    grouped_includes[context_key] = []
                
                # Add a source comment for easier maintenance
                grouped_includes[context_key].append(f"\n; --- Source: {'.'.join(current_ahk_path_list)} ---")
                grouped_includes[context_key].extend(sorted(found_ahk_files))

            # 6. Recurse into children
            if node.get("children"): 
                # IMPORTANT: Pass the current_win_active to children
                find_files_recursive(
                    node.get("children"),
                    os.path.join(fs_path_prefix, current_fs_path_segment),
                    current_ahk_path_list,
                    current_win_active,
                    current_effective_include_status
                )

    # Initial call to the recursive helper
    find_files_recursive(structure_list, '', [FINAL_rootName])
    
    # --- 7. Generation of the final includes content ---
    final_includes = []
    SECTION_SEPARATOR = "=" * 40
    
    final_includes.append(f'\n; {SECTION_SEPARATOR}\n; --- AUTO-GENERATED SCRIPT INCLUDES ---\n; {SECTION_SEPARATOR}\n')
    
    # A. Global Includes (key None) - Merged and without HotIf
    global_content = grouped_includes.pop(None, [])
    
    if global_content:
        final_includes.append(f'; --- 1. Global Includes (Always Active) ---\n')
        final_includes.extend(global_content)
        
    # B. Context-Sensitive Includes (All other keys)
    if grouped_includes:
        final_includes.append(f'\n; --- 2. Context-Sensitive (HotIf) Includes ---\n')
        
        # Sort keys for stable output order (alphabetical)
        sorted_keys = sorted(grouped_includes.keys())
        
        for win_active_condition in sorted_keys:
            
            includes = grouped_includes[win_active_condition]
            
            # Start of the #HotIf block
            final_includes.append(f'\n; --- Context: {win_active_condition} ---')
            final_includes.append(f'#HotIf WinActive("{win_active_condition}")')
            
            # Add the includes
            final_includes.extend(includes)
            
            # End of the #HotIf block
            final_includes.append(f'#HotIf ; End context {win_active_condition}')
            
    # Final reset to ensure no context persists in the script's main thread
    final_includes.append("\n#HotIf ; Final context reset")
    
    return "\n".join(final_includes)

# =================================================================
# GENERATION FUNCTION
# =================================================================

def generate_INCLUDE_OUTPUT(settings, Param_pathsAHK_jsonPathVar, is_initial_run, Param_StartAHKScriptOutput, config_path):
    """
    Generates the INCLUDE_OUTPUT file (e.g., Includes.ahk) in the config directory,
    including the class structure and #include directives based on settings.json.
    """
    global INCLUDE_OUTPUT # Use the global variable for the output file name

    # 1. Determination of the AHK INCLUDE FILE path to write
    # This path (INCLUDE_OUTPUT) comes from sys.argv[4].
    if not INCLUDE_OUTPUT:
        logging.error("Global variable INCLUDE_OUTPUT is not defined. Cannot write AHK include file.")
        exit_script(EXIT_CODE_ERROR)

    # Build the output path using the config folder
    # config_path is (e.g., ".config"), INCLUDE_OUTPUT is (e.g., ".include.ahk")
    FINAL_INCLUDE_FILE_PATH = os.path.join(os.getcwd(), config_path, INCLUDE_OUTPUT)
    FINAL_INCLUDE_FILE_PATH = os.path.abspath(FINAL_INCLUDE_FILE_PATH) # Clean up
    
    # Get the directory where the include file will be written
    include_file_dir = os.path.dirname(FINAL_INCLUDE_FILE_PATH)
    
    rootName = settings.get("RootName", "Unknown_Root")

    # --- Debug variables ---
    logging.debug(f"DEBUG - rootName: {rootName}")
    logging.debug(f"DEBUG - FINAL_INCLUDE_FILE_PATH (File to Write): {FINAL_INCLUDE_FILE_PATH}")

    # --- 2. Generate dynamic content (Classes and Includes) ---
    # The rootName is used for the class (A_Path)
    generated_structure_string, generated_include_string = extract_ahk_generated_content(settings, rootName, include_file_dir)
    logging.debug(f"DEBUG - Generated structure and include strings created.")

    # --- 3. Reconstruction of the final AHK content ---
    ahk_content_lines = [
        f'; Configuration file generated by {os.path.basename(__file__)} on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        f'#Requires AutoHotkey v2.0\n',
    ]
    
    if generated_structure_string:
        ahk_content_lines.append(f'\n; Configuration structure based on {SETTINGS_FILE}')
        ahk_content_lines.append(generated_structure_string)
        
    if generated_include_string:
        ahk_content_lines.append(generated_include_string)
    
    ahk_content = "\n".join(ahk_content_lines)

    # --- 4. Comparison (if not initial run and file exists) ---
    should_rewrite = True
    
    if not is_initial_run and os.path.exists(FINAL_INCLUDE_FILE_PATH):
        try:
            with open(FINAL_INCLUDE_FILE_PATH, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            
            # Simple content comparison
            if existing_content.strip() == ahk_content.strip():
                logging.info(f"AHK include file content (Classes/Includes) is identical. Skipping rewrite.")
                should_rewrite = False
                
        except Exception as e:
            logging.warning(f"Error during existing AHK include file comparison: {e}. Forcing rewrite.")
            # should_rewrite remains True
    
    # --- 5. Write the file ---
    if should_rewrite:
        try:
            # Write to FINAL_INCLUDE_FILE_PATH
            with open(FINAL_INCLUDE_FILE_PATH, 'w', encoding='utf-8') as f:
                f.write(ahk_content)
            logging.info(f"AHK include file generated successfully at: {FINAL_INCLUDE_FILE_PATH}")
        except Exception as e:
            # Show the actual filename that caused the error
            logging.error(f"Error writing AHK include file '{FINAL_INCLUDE_FILE_PATH}': {e}")
            exit_script(EXIT_CODE_ERROR)
    else:
         # End function without writing
         logging.info(f"Skipping rewrite of AHK include file: {FINAL_INCLUDE_FILE_PATH}")

def final_script_actions(StartAHKFileOutput, is_initial_run, generated_INCLUDE_OUTPUT_filename, config_path):
    """
    Manages the initial creation of the final AHK script or its launch.
    The AHK script is created from a template if not found or on 'initial run'.
    
    StartAHKFileOutput: Name of the main script (e.g., Deepr.ahk)
    generated_INCLUDE_OUTPUT_filename: Name of the include file (e.g., .include.ahk)
    config_path: Relative path of the config folder (e.g., .config)
    """
    # The `StartAHKFileOutput` (e.g., Deepr.ahk) is at the ROOT.
    script_path = os.path.join(os.getcwd(), StartAHKFileOutput) 

    create_base_script = False
    if is_initial_run:
        logging.info(f"Initial run: Creating/updating base AHK script '{StartAHKFileOutput}'.")
        create_base_script = True
    elif not os.path.exists(script_path):
        logging.info(f"Final script not found. Creating base AHK script '{StartAHKFileOutput}'.")
        create_base_script = True
    else:
         logging.info(f"Final script '{StartAHKFileOutput}' already exists. Skipping base content creation.")

    if create_base_script:
        # The AHK include path must be relative to the script at root (e.g., .config\.includes.ahk)
        include_file_name_for_ahk = os.path.join(config_path, generated_INCLUDE_OUTPUT_filename)
        include_file_name_for_ahk = include_file_name_for_ahk.replace(os.sep, "\\")

        current_date = datetime.now().strftime("%Y/%m/%d")
        
        # Template for the initial script, based on sample.txt
        # Note: {{ and }} are used to escape curly braces in the f-string for AHK code blocks.
        base_content = f"""\
/***********************************************************************************
 * 
 * @description A fully modulable ahk script with per application hotkeys layering.
 * @author Ephraem
 * @date {current_date}
 * @version {SCRIPT_VERSION}
 * 
/**********************************************************************************/
/***********************************************************************************
                                        @Notes
* 

*
***********************************************************************************/

/***********************************************************************************
                                        @Init
***********************************************************************************/

#include "{include_file_name_for_ahk}"

    full_command_line := DllCall("GetCommandLine", "str")

    if not (A_IsAdmin or RegExMatch(full_command_line, " /restart(?!\S)")) {{
        try {{
            if A_IsCompiled 
                Run '*RunAs "' A_ScriptFullPath '" /restart'
            else
                Run '*RunAs "' A_AhkPath '" /restart "' A_ScriptFullPath '"'
        }} ExitApp
    }}

    ;E.g: TraySetIcon(A_Path.Icons "\\YourIcon.png")
    
    #ESC::Run '*RunAs "' A_ScriptDir "\\Launcher.ahk" '" /restart "' 

/***********************************************************************************
                                    @SetTimers
***********************************************************************************/
  
    ;E.g: SetTimer((*) => YourFunctions() , 1000)

/***********************************************************************************
                                        @GUI
***********************************************************************************/
"""
        try:
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(base_content)
            logging.info(f"Base AHK script '{StartAHKFileOutput}' created/updated successfully from template.")
        except Exception as e:
            logging.error(f"Error writing base AHK script '{StartAHKFileOutput}': {e}")
            # Do not stop, but launch will probably fail
    
    # Attempt to launch the script ONLY if it's NOT an 'initial run'
    if not is_initial_run:
        logging.info(f"Standard run: Attempting to launch '{StartAHKFileOutput}'.")
        if os.path.exists(script_path):
            try:
                # Launch the AHK script using the associated program (AutoHotkey)
                os.startfile(script_path)
                logging.info(f"Launched '{StartAHKFileOutput}' successfully.")
            except Exception as e:
                # On launch failure
                logging.error(f"Failed to launch '{StartAHKFileOutput}'. Please launch it manually. Error: {e}")
        else:
            logging.warning(f"File '{StartAHKFileOutput}' not found at '{script_path}'. Skipping launch (write may have failed).")

def get_paths_to_ignore_for_scan(structure, base_path="."):
    """
    Recursively generates a list of folder paths that should be ignored
    during the unknown folder scan, based on 'is_include': 'false'.
    If a parent is ignored, all its children are also ignored.
    """
    ignored_paths = []
    for item in structure:
        include_status = is_valid_include_setting(item)
        
        item_folder_name = get_folder_name(item)
        if not item_folder_name:
            continue

        current_path = os.path.join(base_path, item_folder_name)

        if include_status is False:
            # If this item is set to not be included, add it and all its children.
            ignored_paths.append(current_path)
            if item.get('children'):
                # Use get_expected_paths to quickly get all children paths recursively
                ignored_paths.extend(get_expected_paths(item['children'], current_path))
        elif item.get('children'):
            # If this item is included, we still need to check its children.
            ignored_paths.extend(get_paths_to_ignore_for_scan(item['children'], current_path))
            
    return ignored_paths

def find_unknown_folders(expected_paths, paths_to_ignore_scan):
    """
    Scans the project directory and finds all folders that exist on disk
    but are NOT part of the expected_paths list. It also ignores folders
    explicitly marked for exclusion from the scan.
    
    This version DOES NOT prune unknown folders, allowing os.walk to
    descend into them to find unknown children.
    """
    # Use sets for fast lookup
    expected_paths_set = set(os.path.normpath(p) for p in expected_paths)
    ignore_scan_paths_set = set(os.path.normpath(p) for p in paths_to_ignore_scan)
    
    # Standard directories to ignore during the scan
    ignore_dirs = {'.git', 'venv', '.venv', '__pycache__', '.vscode'}
    
    unknown_folders = []
    
    # Walk the directory structure from the root
    for root, dirs, files in os.walk(os.getcwd(), topdown=True):
        
        # Iterate over a copy of dirs so we can modify the original 'dirs' list
        # to prune traversal for 'ignore_dirs' and 'ignore_scan_paths'
        dirs_copy = list(dirs)
        
        for d in dirs_copy:
            full_path = os.path.normpath(os.path.join(root, d))
            relative_path = os.path.relpath(full_path, os.getcwd())

            # 1. Prune standard ignored directories
            if d in ignore_dirs:
                dirs.remove(d)
                continue

            # 2. Prune directories explicitly set to 'is_include: false'
            if relative_path in ignore_scan_paths_set:
                logging.info(f"Ignoring folder during scan (is_include: false): {relative_path}")
                dirs.remove(d) # Prune from traversal
                continue

            # 3. Check if it's an expected path
            if relative_path in expected_paths_set:
                # This is a known folder, allow os.walk to descend
                continue
            else:
                # 4. This is an UNKNOWN folder
                logging.warning(f"Found unknown folder: {relative_path}")
                unknown_folders.append(relative_path)
                # We DO NOT prune. We let os.walk descend into it.
            
    return unknown_folders

def select_action_cli(unknown_folder, structure_json):
    """
    Asks the user what to do with an unknown folder.
    
    Returns:
        tuple: (action, data)
        - ('skip', None)
        - ('move', 'destination_path')
        - ('add', 'parent_path') 
    """
    print(f"\n────────────────────────────────────────────────────────")
    print(f" ❓ Dossier inconnu trouvé : '{unknown_folder}'")
    print(f"────────────────────────────────────────────────────────")
    print("Que souhaitez-vous faire ?")
    print("  [ m ]  Déplacer le *contenu* vers un dossier existant.")
    print("  [ a ]  Ajouter ce dossier (et ses enfants) à settings.json (parent auto-détecté).")
    print("  [ 0 ]  Ignorer ce dossier (et scanner ses enfants).")
    print(f"────────────────────────────────────────────────────────")

    action_choice = ''
    while action_choice not in ['m', 'a', '0']:
        try:
            action_choice = input("Votre choix (m, a, 0) : ").lower().strip()
        except (KeyboardInterrupt, EOFError):
            print("\nOpération annulée. Ignorer ce dossier.")
            return 'skip', None
    
    if action_choice == '0':
        logging.info(f"Utilisateur a choisi [0] Ignorer pour {unknown_folder}.")
        return 'skip', None
    
    # --- NOUVELLE LOGIQUE POUR 'ADD' (AUTO-DÉTECTION) ---
    if action_choice == 'a':
        # 1. Calculer automatiquement le chemin du parent
        parent_path = os.path.dirname(unknown_folder)
        if not parent_path: # Gère les dossiers à la racine
            parent_path = "."
        
        logging.info(f"Utilisateur a choisi d'AJOUTER '{unknown_folder}'. Parent auto-détecté : '{parent_path}'.")
        
        # 2. Vérifier que le parent auto-détecté existe bien dans le JSON
        parent_node = find_parent_node_in_json(structure_json, os.path.normpath(parent_path))
        
        if not parent_node:
            logging.error(f"Échec de l'ajout auto : Le parent '{parent_path}' n'a pas été trouvé dans settings.json.")
            print(f"ERREUR : Impossible d'ajouter '{unknown_folder}'.")
            print(f"Le parent auto-détecté ('{parent_path}') n'existe pas dans l'arbre settings.json.")
            print("Veuillez d'abord ajouter le dossier parent (s'il est aussi inconnu), ou ignorer celui-ci.")
            try:
                input("Appuyez sur Entrée pour continuer...") # Pause pour que l'utilisateur voie l'erreur
            except (KeyboardInterrupt, EOFError):
                pass
            return 'skip', None # Échec gracieux
        
        # 3. Le parent existe, retourner l'action 'add' avec le parent trouvé
        print(f"Parent trouvé : '{parent_path}'. Ajout de '{unknown_folder}' en cours...")
        return 'add', parent_path

    # --- LOGIQUE EXISTANTE POUR 'MOVE' (DEMANDE DE DESTINATION) ---
    if action_choice == 'm':
        print("\nOù souhaitez-vous DÉPLACER le *contenu* ?")
        prompt_text = "Entrez un numéro de destination (0 pour annuler) : "

        # --- CLI Tree Display Logic (Seulement pour 'move') ---
        cli_destinations = [] # (display_line, path_value)

        def build_cli_options(structure_list, base_path=".", indent_str=""):
            """Populate cli_destinations recursively."""
            prefix_mid = "├─ "
            prefix_last = "└─ "
            indent_mid = "│  "
            indent_last = "   "
            
            valid_items = [item for item in structure_list if get_folder_name(item)]
            
            for i, item in enumerate(valid_items):
                item_folder_name = get_folder_name(item)
                current_path = os.path.join(base_path, item_folder_name)
                is_last = (i == len(valid_items) - 1)
                prefix = prefix_last if is_last else prefix_mid
                
                display_line = f"{indent_str}{prefix}{item_folder_name}"
                cli_destinations.append((display_line, current_path))
                
                if item.get('children'):
                    new_indent = indent_last if is_last else indent_mid
                    build_cli_options(item['children'], current_path, indent_str + new_indent)

        # Build and display options
        build_cli_options(structure_json, ".")
        
        print("\n[ 0 ]  Annuler / Ignorer")
        print("-" * 30)
        for i, (display_line, path) in enumerate(cli_destinations):
            print(f"[ {i+1:<2} ] {display_line:<30} (-> {path})")
        print("-" * 30)
        
        # Input loop for destination
        while True:
            try:
                choice_str = input(prompt_text)
                choice_int = int(choice_str)
                
                if choice_int == 0:
                    logging.info(f"Utilisateur a choisi [0] Annuler pour {unknown_folder}.")
                    return 'skip', None # Treat cancel as skip
                
                if 1 <= choice_int <= len(cli_destinations):
                    selected_path = cli_destinations[choice_int - 1][1]
                    
                    logging.info(f"Utilisateur a choisi de DÉPLACER vers [{choice_int}] {selected_path}.")
                    return 'move', selected_path
                else:
                    print(f"Numéro invalide. Doit être entre 0 et {len(cli_destinations)}.")
            except ValueError:
                print("Entrée invalide. Veuillez entrer un numéro.")
            except (KeyboardInterrupt, EOFError):
                print("\nOpération annulée. Ignorer ce dossier.")
                logging.warning(f"Saisie annulée pour {unknown_folder}. Ignoré.")
                return 'skip', None
    
    # Fallback (ne devrait pas être atteint)
    return 'skip', None

def find_parent_node_in_json(structure_list, target_path, base_path="."):
    """
    Recursively searches the json structure for the node matching target_path.
    Returns the node (dict) if found, else None.
    """
    for item in structure_list:
        item_folder_name = get_folder_name(item)
        if not item_folder_name:
            continue
        
        current_path = os.path.normpath(os.path.join(base_path, item_folder_name))
        
        if current_path == target_path:
            return item # Found it
        
        if item.get('children'):
            found = find_parent_node_in_json(item['children'], target_path, current_path)
            if found:
                return found
    return None

def scan_disk_for_children(parent_disk_path):
    """
    Scans a directory on disk and returns a list of JSON objects
    for its subdirectories.
    """
    children_nodes = []
    try:
        for entry in os.scandir(parent_disk_path):
            if entry.is_dir():
                # Ignore hidden/system folders
                if entry.name.startswith('.') or entry.name in ('__pycache__', 'venv', '.venv'):
                    continue
                
                folder_name = entry.name
                logging.info(f"  -> Trouvé sous-dossier : {folder_name}")
                
                new_node = {
                    "type": folder_name, # Use folder name as type
                    "is_include": "true",
                    "is_path": "true"
                }
                
                # Recurse to find grand-children
                grand_children = scan_disk_for_children(entry.path)
                if grand_children:
                    new_node["children"] = grand_children
                
                children_nodes.append(new_node)
                
    except FileNotFoundError:
        logging.warning(f"Scan error: Dossier {parent_disk_path} non trouvé.")
    except Exception as e:
        logging.error(f"Erreur lors du scan de {parent_disk_path}: {e}")
        
    return children_nodes

def add_folder_to_settings(json_data, unknown_folder_path, parent_path, settings_json_path):
    """
    Adds the unknown folder and its children to settings.json
    under the specified parent_path.
    """
    logging.info(f"Tentative d'ajout de '{unknown_folder_path}' à settings.json sous '{parent_path}'...")
    
    # 1. Find the parent node in the JSON structure
    parent_node = find_parent_node_in_json(json_data.get('structure', []), os.path.normpath(parent_path))
    
    if not parent_node:
        logging.error(f"Impossible de trouver le noeud parent '{parent_path}' dans settings.json. Ajout annulé.")
        print(f"ERREUR: Parent '{parent_path}' non trouvé dans JSON. Annulé.")
        return

    # 2. Get the name of the new folder (the last part of the path)
    new_folder_name = os.path.basename(unknown_folder_path)
    
    # 3. Create the new JSON node for this folder
    new_node = {
        "type": new_folder_name, # Default to folder name
        "is_include": "true",
        "is_path": "true"
    }
    
    # 4. Scan the folder on disk for its children
    full_disk_path = os.path.join(os.getcwd(), unknown_folder_path)
    children = scan_disk_for_children(full_disk_path)
    if children:
        new_node["children"] = children

    # 5. Add the new node to the parent's "children" list
    if "children" not in parent_node:
        parent_node["children"] = []
    
    parent_node["children"].append(new_node)
    logging.info(f"Noeud {new_folder_name} ajouté avec succès à la structure JSON (en mémoire).")
    
    # 6. Write the modified json_data back to the settings.json file
    try:
        with open(settings_json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4) # indent=4 for pretty print
        logging.info(f"'{settings_json_path}' mis à jour avec succès sur le disque.")
        print(f"'{settings_json_path}' a été mis à jour.")
        
    except Exception as e:
        logging.error(f"ERREUR fatale: Impossible d'écrire dans '{settings_json_path}': {e}")
        print(f"ERREUR: Impossible de sauvegarder les modifications dans '{settings_json_path}'.")

def copy_folder_contents(src, dst, root_tk):
    """
    Copies all contents from src to dst.
    Uses shutil.copytree with dirs_exist_ok=True.
    """
    logging.info(f"Attempting to copy contents from '{src}' to '{dst}'...")
    try:
        # This copies all files and subfolders from src into dst
        shutil.copytree(src, dst, dirs_exist_ok=True)
        logging.info("Copy successful.")
        
    except Exception as e:
        logging.error(f"Error copying files from '{src}' to '{dst}': {e}")
        messagebox.showerror("Copy Error", f"Failed to copy files from '{src}' to '{dst}'.\n\nError: {e}", parent=root_tk)
   
def delete_source_folder(src, root_tk):
    """
    Deletes the source folder after a successful copy.
    """
    logging.info(f"Tentative de suppression du dossier d'origine : '{src}'...")
    try:
        shutil.rmtree(src)
        logging.info("Dossier d'origine supprimé avec succès.")
        print(f"Nettoyage : Suppression de '{src}' terminée.")
    except Exception as e:
        logging.error(f"Erreur lors de la suppression du dossier '{src}': {e}")
        messagebox.showerror("Erreur de suppression", f"Échec de la suppression du dossier d'origine '{src}'.\n\nVous devrez peut-être le supprimer manuellement.\n\nErreur: {e}", parent=root_tk)

def create_minimal_settings():
    """
    Prompts the user to create a minimal settings.json file when it's missing
    during an initial run.
    
    Returns:
        tuple or None: (json_data, settings_abs_path) if successful, else None.
    """
    logging.info(f"Fonction 'create_minimal_settings' appelée.")
    
    # 1. Vérifier si la console est interactive
    if not sys.stdout.isatty():
        logging.fatal("Pas de terminal interactif (isatty=False). Impossible de demander le RootName.")
        root_err = Tk()
        root_err.withdraw()
        messagebox.showerror(
            "Erreur Critique", 
            "Impossible de trouver settings.json.\n\n"
            "Un terminal interactif est requis pour la configuration initiale (définir le RootName)."
        )
        root_err.destroy()
        return None # Signal d'échec

    # 2. Demander le RootName à l'utilisateur
    root_name = ""
    print("\n--- CONFIGURATION INITIALE ---")
    print(f"Le fichier '{SETTINGS_FILE}' est introuvable.")
    while not root_name:
        try:
            root_name = input("Veuillez entrer un nom pour votre projet (ex: MonProjet) : ").strip()
            if not root_name:
                print("Le nom ne peut pas être vide.")
            # Valide que le nom est simple (lettres, chiffres, underscore)
            elif not re.match(r"^[A-Za-z0-9_]+$", root_name):
                 print("Le nom ne doit contenir que des lettres (A-Z, a-z), des chiffres (0-9) et des underscores (_).")
                 root_name = ""

        except (KeyboardInterrupt, EOFError):
            logging.warning("Création minimale annulée par l'utilisateur.")
            print("\nConfiguration annulée.")
            return None # Signal d'échec

    logging.info(f"RootName fourni par l'utilisateur : {root_name}")

    # 3. Définir la structure JSON minimale
    # Utilise la variable globale json_keyConfig pour le type "Configuration"
    minimal_data = {
        "RootName": root_name,
        "structure": [
            {
                "type": json_keyConfig, # "Configuration"
                "name": ".config",      # Dossier où settings.json sera déplacé
                "is_include": "false",
                "is_path": "true"
            },
            {
                "type": "Library",
                "name": "Library",
                "is_include": "true",
                "is_path": "true"
            }
        ]
    }
    
    # 4. Définir le chemin de destination (à la racine)
    settings_abs_path = os.path.abspath(os.path.join(os.getcwd(), SETTINGS_FILE))
    
    # 5. Écrire le fichier
    try:
        with open(settings_abs_path, 'w', encoding='utf-8') as f:
            json.dump(minimal_data, f, indent=4)
        
        logging.info(f"Fichier '{SETTINGS_FILE}' minimal créé avec succès à : {settings_abs_path}")
        print(f"'{SETTINGS_FILE}' créé avec succès.")
        
        # 6. Retourner les données et le chemin
        return minimal_data, settings_abs_path
        
    except Exception as e:
        logging.error(f"Erreur lors de l'écriture du fichier '{settings_abs_path}': {e}")
        root_err = Tk()
        root_err.withdraw()
        messagebox.showerror("Erreur d'écriture", f"Impossible de créer le fichier {SETTINGS_FILE}.\n\nErreur: {e}")
        root_err.destroy()
        return None # Signal d'échec

# =================================================================
# EXECUTIONS
# =================================================================

def main_build():
    """
    Main build process:
    1. Detects initial run vs. standard run.
    2. Loads settings.json (from root or config path).
    3. Validates settings and structure.
    4. Creates folder structure.
    5. Moves settings.json and writes paths.ahk (root).
    6. Generates .include.ahk (in config path).
    7. Creates/Launches the main RootName.ahk script (root).
    """

    # ------------------------------------------------------------------------------------
    # 0. Get arguments (PYTHON_CMD, PATHFILE, INCLUDE_OUTPUT)
    # ------------------------------------------------------------------------------------
    global INCLUDE_OUTPUT, PATHFILE, StartAHKScriptOutput 
    
    StartAHKScriptOutput = None # Will be set by RootName
    config_relative_path = None # Will be set after reading settings.json

    try:
        # sys.argv[2] is the Python command path
        PYTHON_CMD = sys.argv[2] 
        logging.info(f"Python command detected via command-line argument: {PYTHON_CMD}")

        # sys.argv[3] is the output AHK Path file name (e.g., paths.ahk)
        PATHFILE = sys.argv[3]
        logging.info(f"Output PATHFILE (path config) file name detected via command-line argument: {PATHFILE}")

        # sys.argv[4] is the output AHK include file name (e.g., .includes.ahk)
        INCLUDE_OUTPUT = sys.argv[4]
        logging.info(f"Output INCLUDE_OUTPUT (includes) file name detected via command-line argument: {INCLUDE_OUTPUT}")

    except IndexError:
        raise ValueError("Error: Arguments are missing. Usage: main.py build <python_cmd> <ahk_path_file> <ahk_include_file> [--log]")

    # ------------------------------------------------------------------------------------
    # 1. Determine 'is_initial_run' by reading PATHFILE at the ROOT
    # ------------------------------------------------------------------------------------
    
    logging.info(f"--- Build Process Started ---")
    
    # Look for PATHFILE (e.g., paths.ahk) at the ROOT
    pathsAHK_source = os.path.join(os.getcwd(), PATHFILE) 
    
    pathsAHK_jsonPathVar = None # This is the path to .config/settings.json
    is_initial_run = False 

    if os.path.exists(pathsAHK_source):
        # Case 1: 'paths.ahk' exists. 'is_initial_run = False'.
        # Read the settings.json path from this file.
        logging.info(f"Attempting to load paths from AHK file: {PATHFILE}")
        pathsAHK_infos = read_ahk_variables(pathsAHK_source) 
        if pathsAHK_infos:
            pathsAHK_jsonPathVar, StartAHKScriptOutput = pathsAHK_infos
            logging.info(f"Loaded config from '{PATHFILE}'. Settings.json should be at '{pathsAHK_jsonPathVar}'.")
        else:
            logging.warning(f"File '{PATHFILE}' exists but variables could not be read. Proceeding as partial initial run.")
            is_initial_run = True 
    else:
        # Case 2: 'paths.ahk' does NOT exist. 'is_initial_run = True'.
        is_initial_run = True
        logging.info(f"File '{PATHFILE}' not found at root. Assuming initial run.")
    
    # ------------------------------------------------------------------------------------
    # 2. Load settings.json
    #    (Either from the remote path or from root if 'initial_run')
    # ------------------------------------------------------------------------------------
    
    json_source_absolutePath = os.path.join(os.getcwd(), SETTINGS_FILE) # Local source (root)
    json_data = None
    loaded_settings_json_path = None # <--- VARIABLE AJOUTÉE POUR STOCKER LE CHEMIN
    
    if pathsAHK_jsonPathVar and os.path.exists(pathsAHK_jsonPathVar) and not is_initial_run:
        # Standard Run: load the remote settings.json (from .config/settings.json)
        json_data_check = load_settings_json(pathsAHK_jsonPathVar)
        if json_data_check:
            # CORRECTION : Capturer le chemin absolu qui a été chargé
            json_data, loaded_settings_json_path = json_data_check
            logging.info(f"Configuration path confirmed by '{PATHFILE}'.")
        else:
            logging.warning(f"Remote settings.json file at '{pathsAHK_jsonPathVar}' is invalid. Attempting local load.")
            is_initial_run = True # Treat as initial run if remote JSON is broken
    
    if not json_data:
        # Initial Run (or fallback): load settings.json from ROOT
        logging.info("Attempting to load local settings.json (Initial Run or Fallback).")
        local_json_data_check = load_settings_json(json_source_absolutePath)
        
        if local_json_data_check:
            # CAS 1: settings.json existe à la racine
            json_data, loaded_settings_json_path = local_json_data_check
            json_source_absolutePath = loaded_settings_json_path
            
            if not is_initial_run:
                is_initial_run = True 
            logging.info("'New Structure' mode detected: Loading settings.json locally.")
        
        elif is_initial_run:
            # CAS 2: settings.json n'existe pas ET on est en initial run
            logging.warning(f"Initial run mode, but '{SETTINGS_FILE}' not found locally at '{json_source_absolutePath}'.")
            logging.info("Attempting to create a minimal settings.json file...")
            
            # Appel de la nouvelle fonction pour créer le fichier
            minimal_json_check = create_minimal_settings()
            
            if minimal_json_check:
                # La création a réussi
                json_data, loaded_settings_json_path = minimal_json_check
                # Le 'source' path est le chemin qui vient d'être créé
                json_source_absolutePath = loaded_settings_json_path
                logging.info(f"Minimal '{SETTINGS_FILE}' created and loaded.")
            else:
                # La création a échoué (l'utilisateur a annulé ou erreur d'écriture)
                logging.fatal("Failed to create minimal settings.json. Exiting.")
                exit_script(EXIT_CODE_ERROR)
        
        else:
            # CAS 3: settings.json n'existe pas, et on N'EST PAS en initial run
            # (signifie que paths.ahk est corrompu ou pointe vers un fichier supprimé)
            logging.fatal(f"'{SETTINGS_FILE}' not found locally or at the configured path '{pathsAHK_jsonPathVar}'.")
            exit_script(EXIT_CODE_ERROR)
    
    # CORRECTION : Vérifier aussi que le chemin a bien été stocké
    if not json_data or not loaded_settings_json_path:
        # Cette condition est maintenant la sécurité finale si tout a échoué
        logging.fatal(f"Could not find or load '{SETTINGS_FILE}'.")
        exit_script(EXIT_CODE_ERROR)

    # ------------------------------------------------------------------------------------
    # 3. Validate settings.json and find config_relative_path
    # ------------------------------------------------------------------------------------
    
    if 'structure' not in json_data:
        logging.error("The 'structure' key is missing in the settings.json file.")
        exit_script(EXIT_CODE_ERROR)

    # Validate RootName
    FINAL_rootName = json_data.get("RootName") 
    if not FINAL_rootName:
        logging.error("Error: 'RootName' key is missing in your settings.json file.")
        exit_script(EXIT_CODE_ERROR)
    
    # Validate and FIND config_relative_path (e.g., .config)
    config_relative_path = find_config_dir_path(json_data, json_keyConfig)
    if not config_relative_path:
        logging.error(f"Mandatory key 'type' for structure item type '{json_keyConfig}' is missing or empty in settings.json.")
        exit_script(EXIT_CODE_ERROR) 
        
    logging.info(f"Mandatory keys 'RootName' ('{FINAL_rootName}') and 'Configuration' path ('{config_relative_path}') are present.")
        
    # --- RootName Change Detection and Migration ---
    
    # The new, expected script name based on settings.json
    new_start_script_name = f"{FINAL_rootName}.ahk"
    
    # StartAHKScriptOutput still holds the OLD name from PATHFILE if it's not an initial run
    old_start_script_name = StartAHKScriptOutput 
    
    if not is_initial_run and old_start_script_name and (old_start_script_name != new_start_script_name):
        # RootName change detected
        logging.warning(f"RootName change detected: '{old_start_script_name}' -> '{new_start_script_name}'.")
        
        # We must now use the NEW name for all subsequent operations
        StartAHKScriptOutput = new_start_script_name
        
        # Check if the old script file exists at the root
        old_script_path = os.path.join(os.getcwd(), old_start_script_name)
        new_script_path = os.path.join(os.getcwd(), new_start_script_name)

        if os.path.exists(old_script_path):
            logging.info(f"Found existing script file: '{old_start_script_name}'")
            
            # Ask the user if they want to migrate content
            root = Tk()
            root.withdraw()
            msg = (
                f"RootName Change Detected\n\n"
                f"The script name has changed from:\n{old_start_script_name}\n\n"
                f"To:\n{new_start_script_name}\n\n"
                f"Do you want to move your custom code from the old file to the new file?\n\n"
                f"(Yes = Move content and delete old file)\n"
                f"(No = Create a new blank file for {new_start_script_name})"
            )
            response = messagebox.askyesno("Migrate Script Content?", msg)
            root.destroy()
            
            if response:
                # User selected YES: Move content
                try:
                    # Use copy2 to preserve metadata, then remove
                    shutil.copy2(old_script_path, new_script_path)
                    os.remove(old_script_path)
                    logging.info(f"Successfully migrated content from '{old_start_script_name}' to '{new_start_script_name}'.")
                except Exception as e:
                    logging.error(f"Error during script migration: {e}")
                    # Show an error, but continue. The new file might be incomplete.
                    root_err = Tk()
                    root_err.withdraw()
                    messagebox.showerror("Migration Error", f"Failed to move content from {old_start_script_name} to {new_start_script_name}.\n\nError: {e}")
                    root_err.destroy()
            else:
                # User selected NO: Do nothing.
                logging.info(f"User opted not to migrate content. A new '{new_start_script_name}' will be created if needed.")
        else:
            # Old script file not found, nothing to migrate
            logging.info(f"Old script file '{old_start_script_name}' not found. No migration necessary.")
            
    else:
        # No change, or initial run. Set the name as normal.
        StartAHKScriptOutput = new_start_script_name
        
    logging.info(f"Final StartAHKScriptOutput file name determined: {StartAHKScriptOutput}")
    # --- End of RootName Change Detection ---
        
    # ------------------------------------------------------------------------------------
    # 4. Generate folder structure
    # ------------------------------------------------------------------------------------
    try:
        expected_paths = get_expected_paths(json_data['structure'])
    except ValueError as e:
        logging.fatal(f"FATAL VALIDATION ERROR: {e}")
        exit_script(EXIT_CODE_ERROR)
    
    # This step asks to create missing folders
    compare_structure(expected_paths, is_initial_run)
    # This step creates all defined folders
    create_structure(json_data)
    
    # ------------------------------------------------------------------------------------
    # 4.5. Handle unknown folders
    # ------------------------------------------------------------------------------------
    logging.info("--- Checking for unknown folders not defined in settings.json ---")
    
    # Get a list of folders to ignore based on "is_include": "false"
    paths_to_ignore = get_paths_to_ignore_for_scan(json_data['structure'])
    unknown_folders = find_unknown_folders(expected_paths, paths_to_ignore)
    
    if unknown_folders:
        
        # --- NOUVELLE VÉRIFICATION DE CONSOLE ---
        if not sys.stdout.isatty():
            logging.warning("Dossiers inconnus trouvés, mais pas de terminal interactif (isatty=False).")
            logging.info("Tentative de relance dans une nouvelle console...")

            command_args = [sys.executable] + sys.argv
            cmd_string = f'cmd.exe /k "{" ".join(command_args)}"'
            
            try:
                subprocess.Popen(cmd_string, creationflags=subprocess.CREATE_NEW_CONSOLE)
                logging.info(f"Script relancé avec succès dans une nouvelle console. Ce processus (caché) va se terminer.")
                exit_script(0) 
                return
            
            except Exception as e:
                logging.error(f"Échec de la relance dans une nouvelle console: {e}")
                root_err = Tk()
                root_err.withdraw()
                messagebox.showerror("Erreur Critique", f"Impossible d'ouvrir un terminal pour gérer les dossiers inconnus.\n\nErreur: {e}")
                root_err.destroy()
                exit_script(EXIT_CODE_ERROR)
                return
        
        # --- SI ON EST ICI, LA CONSOLE EST VISIBLE ---
        logging.warning(f"Found {len(unknown_folders)} unknown folders.")
        
        dialog_root = Tk()
        dialog_root.withdraw()
        
        structure_json_list = json_data.get('structure', [])
        
        # NEW: Set to track folders that have been moved or added
        handled_paths = set() 
        
        print(f"\n--- GESTION DES {len(unknown_folders)} DOSSIERS INCONNUS ---")
        
        for unknown_folder in unknown_folders:
            
            # --- NEW: Check if this folder is a child of an already handled one ---
            is_already_handled = False
            for handled_root in handled_paths:
                # Check if unknown_folder starts with "handled_root/"
                if unknown_folder.startswith(handled_root + os.sep):
                    logging.info(f"Skipping '{unknown_folder}' as it is a child of already handled '{handled_root}'.")
                    is_already_handled = True
                    break
            
            if is_already_handled:
                continue
            # --- End of check ---

            # 1. Call the new action function
            action, data = select_action_cli(
                unknown_folder,
                structure_json_list
            )
            
            if action == 'move':
                # 2. User chose 'move'
                destination = data
                src_path = os.path.join(os.getcwd(), unknown_folder)
                dst_path = os.path.join(os.getcwd(), destination)
                
                print(f"Déplacement de '{src_path}' vers '{dst_path}'...")
                
                copy_folder_contents(src_path, dst_path, dialog_root)
                delete_source_folder(src_path, dialog_root)
                
                # Add to handled set so we skip its children
                handled_paths.add(unknown_folder) 
                
            elif action == 'add':
                # 3. User chose 'add'
                parent_path = data
                
                # Call the new function to write to settings.json
                # We pass the *full* json_data dict, and the path to settings.json
                add_folder_to_settings(
                    json_data,          # The full dict
                    unknown_folder,     # e.g., "Library/NewModule"
                    parent_path,        # e.g., "Library"
                    loaded_settings_json_path # <--- CORRECTION : Utiliser le chemin chargé
                )
                
                # Add to handled set so we skip its children
                handled_paths.add(unknown_folder)

            else:
                # 4. User chose 'skip'
                logging.info(f"L'utilisateur a ignoré le déplacement/ajout pour {unknown_folder}.")
                print(f"Dossier '{unknown_folder}' ignoré.")
                # We DO NOT add to handled_paths, allowing children to be processed
        
        # Clean up the hidden Tk root
        dialog_root.destroy()
        logging.info("--- Fin du traitement des dossiers inconnus ---")
        
    else:
        logging.info("No unknown folders found. Structure is clean.")
    # ------------------------------------------------------------------------------------
    # 5. Post-build (Move JSON and write PATHFILE to ROOT)
    # ------------------------------------------------------------------------------------
    
   # Call the corrected function (post_build_actions)
    # It writes PATHFILE to root and returns the paths we need.
    pathsAHK_jsonPathVar_result, config_relative_path_result = post_build_actions(
        source_path=json_source_absolutePath, # The local settings.json (root)
        json_data=json_data,
        is_initial_run=is_initial_run,
        StartAHKScriptOutput=StartAHKScriptOutput
    )
    # Ensure we use the returned config_path (e.g., .config)
    config_relative_path = config_relative_path_result
    pathsAHK_jsonPathVar = pathsAHK_jsonPathVar_result
    
    
    # ------------------------------------------------------------------------------------
    # 6. Generate the INCLUDE_OUTPUT file (in .config)
    # ------------------------------------------------------------------------------------
    
    # generate_INCLUDE_OUTPUT expects 'config_relative_path'
    generate_INCLUDE_OUTPUT(
        json_data, 
        pathsAHK_jsonPathVar, 
        is_initial_run, 
        StartAHKScriptOutput,
        config_relative_path # <- Pass the config path (e.g., .config)
    )
    
    # ------------------------------------------------------------------------------------
    # 7. Action on the Final script (e.g., Deepr.ahk)
    # ------------------------------------------------------------------------------------
    
    # final_script_actions expects 'config_relative_path'
    # INCLUDE_OUTPUT is the *filename* (e.g., .include.ahk)
    final_script_actions(
        StartAHKScriptOutput,       # e.g., Deepr.ahk (at root)
        is_initial_run, 
        INCLUDE_OUTPUT,             # e.g., .include.ahk (filename)
        config_relative_path        # e.g., .config (folder where the include is)
    ) 

    exit_script(0)
    
if __name__ == "__main__":
    
    enable_logging = False
    if "--log" in sys.argv:
        enable_logging = True
        # Remove the '--log' argument from sys.argv so that the indices
        # of positional arguments (build, python_cmd, etc.) remain correct.
        sys.argv.remove("--log")

    setup_logging(enable_logging)

    if len(sys.argv) < 2:
        print("❌ Error: Mode or command argument missing.")
        print("Usage: main.py build <python_cmd> <ahk_output_file>")
        sys.exit(1)
        
    mode = sys.argv[1].lower()
    
    if mode == "build":
        # Check if the 3rd argument (the output AHK file name) is present.
        # Total: 5 arguments (main.py build python_cmd ahk_output_file)
        if len(sys.argv) < 5: # <--- (checks 5 necessary arguments)
            print("❌ Launch Error (BUILD)")
            print("Usage: main.py build <python_cmd> <ahk_path_file> <ahk_include_file> [--log]")
            sys.exit(1)

        try:
            main_build()
        # Capture all unhandled exceptions in main_build
        except Exception as e:
            # Print the full trace to the console for immediate diagnosis
            print(f"\n❌ UNHANDLED CRASH IN main_build:\n{e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            logging.error(f"Unhandled crash. See console. Error: {e}")
            exit_script(EXIT_CODE_ERROR) # Attempt clean exit

    elif mode == "parser":
        logging.error(f"Parsed Mode previously removed. Need to work on it.")
        exit_script(EXIT_CODE_ERROR) # Attempt clean exit
    else:
        print(f"❌ Error: Unrecognized mode: {mode}")
        print("Available modes: build, parser")
        sys.exit(1)