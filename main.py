import os
import sys
import json
import logging
import shutil 
import argparse
import configparser
import re
from datetime import datetime
from tkinter import (
    Tk, messagebox
)

# --- CONFIGURATION ---
SETTINGS_FILE = "settings.json"
LOG_FILE = "mainpy.log"
# Name of the AHK configuration file to generate
SETTINGS_OUTPUT = None
PATHFILE = None

# AHK local  variable name to use for the settings.json location
AHK_VAR_SETTINGS = "path_settings"
AHK_VAR_PYTHON_CMD = "cmd_python"
AHK_VAR_FINAL_SCRIPT = "StartFinalScript"
# The 'type' of item in settings.json to search for to find the config path
CONFIG_TYPE = "Configuration"



# The return code to indicate an error to the AHK script
EXIT_CODE_ERROR = 1

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        # Write logs to file, overwriting previous logs
        logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'),
        # Also output logs to the console
        logging.StreamHandler(sys.stdout)
    ]
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
    to extract the 'path_settings' and 'cmd_python' variables.

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
    vars_to_resolve = [AHK_VAR_SETTINGS, AHK_VAR_PYTHON_CMD, AHK_VAR_FINAL_SCRIPT]
    
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
                # For our simple config, we assume it's a direct value.
                # We don't handle complex AHK interpolation or expressions here.
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
    Attempts to load paths (settings_path and cmd_python) from the AHK file.
    
    Args:
        pathfile_path (str): The absolute path to the AHK file (path.ahk).
        
    Returns:
        tuple or None: (settings_json_path, python_cmd) if successful, else None.
    """
    parsed_data = retrieve_ahk_variables(pathfile_path)

    settings_path = parsed_data.get(AHK_VAR_SETTINGS)
    python_cmd = parsed_data.get(AHK_VAR_PYTHON_CMD)
    final_script_path = parsed_data.get(AHK_VAR_FINAL_SCRIPT)

    if not settings_path or not python_cmd or not final_script_path:
        logging.error(f"AHK variables '{AHK_VAR_SETTINGS}', '{AHK_VAR_PYTHON_CMD}', or '{AHK_VAR_FINAL_SCRIPT}' are missing or invalid in '{pathfile_path}'.")
        return None
    
    # Replace forward slashes with correct OS separators, just in case
    settings_path = settings_path.replace('/', os.sep)
    
    logging.info(f"Settings path (from AHK): {settings_path}")
    logging.info(f"Python command (from AHK): {python_cmd}")
    logging.info(f"Final Script path (from AHK): {final_script_path}")

    return settings_path, python_cmd, final_script_path

def load_settings_json(settings_json_path):
    """
    Attempts to load and validate the settings.json file.

    Args:
        settings_json_path (str): The path to the settings.json file.

    Returns:
        tuple or None: (settings_data, settings_abs_path) if successful, else None.
    """
    logging.info(f"Attempting to load settings.json from: {settings_json_path}")
    settings_abs_path = os.path.abspath(settings_json_path)

    if not os.path.exists(settings_abs_path):
        logging.error(f"settings.json file not found at: {settings_abs_path}")
        return None

    try:
        with open(settings_abs_path, 'r', encoding='utf-8') as f:
            settings_data = json.load(f)
        
        logging.info(f"settings.json loaded successfully from: {settings_abs_path}")
        return settings_data, settings_abs_path
    
    except json.JSONDecodeError as e:
        logging.error(f"JSON Decode Error in {settings_abs_path}: {e}")
        return None
    except Exception as e:
        logging.error(f"Error reading settings.json file: {e}")
        return None

def find_config_dir_path(settings, config_type_name):
    """
    Searches for the configuration directory path (relative to CWD) within the 
    settings.json structure, using the 'name' field as the folder name if present,
    otherwise using 'type'.
    """
    for item in settings.get('structure', []):
        if item.get('type') == config_type_name:
            # La clé 'type' reste la référence logique (CONFIG_TYPE) pour trouver l'élément.
            # Le chemin relatif est maintenant déterminé par get_folder_name.
            folder_name = get_folder_name(item) 
            if folder_name:
                return folder_name
            else:
                # Si ni 'name' ni 'type' n'est trouvé, cela est une erreur.
                return None 
    return None

def get_expected_paths(structure, base_path="."):
    """
    Génère une liste de chemins de dossiers attendus à partir de la structure JSON.
    Utilise 'name' comme nom de dossier si présent, sinon 'type', et reconstruit 
    le chemin de manière récursive.
    """
    expected_paths = []
    for item in structure:
        # Utiliser la nouvelle fonction de validation
        include_status = is_valid_include_setting(item)
        if include_status == 'ERROR':
            raise ValueError(f"Erreur de validation: La clé 'is_include' doit être 'true' ou 'false' (actuel: {item.get('is_include')}) dans l'élément: {item.get('type')}.")
        
        # Si 'is_include' est 'false', nous n'incluons pas le chemin.
        if include_status is False:
            # Nous incluons le chemin, mais nous n'inclurons PAS ses includes AHK plus tard.
            pass # Continuer pour vérifier les enfants car ils peuvent être "true"
        
        item_folder_name = get_folder_name(item)
        
        # Le dossier doit toujours être vérifié/créé s'il a un nom de dossier valide.
        if item_folder_name:
            current_path = os.path.join(base_path, item_folder_name)
            expected_paths.append(current_path)
            if item.get('children'):
                # Récursion, peu importe le statut 'is_include' du parent
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
    Crée les dossiers en se basant sur la structure définie dans settings.json.
    La création est inconditionnelle par rapport à 'is_include', car le dossier 
    doit exister pour la structure.
    """
    logging.info("Starting folder structure creation...")
    
    def recursive_create(structure, base_path="."):
        for item in structure:
            # 1. Vérification de la validité de la clé, mais sans action ici.
            # L'erreur de validation est levée dans get_expected_paths, que main_build intercepte.
            include_status = is_valid_include_setting(item)
            
            # Si le statut est ERROR, on ne fait rien pour la création/récursion
            # car le process s'arrêtera juste après dans main_build.
            if include_status == 'ERROR':
                continue
                
            item_folder_name = get_folder_name(item)
            
            if item_folder_name:
                folder_path = os.path.join(base_path, item_folder_name)
                try:
                    # 2. Création/Vérification du dossier (TOUJOURS FAITE)
                    os.makedirs(folder_path, exist_ok=True)
                    logging.info(f"Folder created/verified: {folder_path}")
                except Exception as e:
                    logging.error(f"Error creating folder {folder_path}: {e}")
                    raise # Renvoyer l'erreur à la fonction main
                
                # 3. Récursion (TOUJOURS FAITE)
                if item.get('children'):
                    recursive_create(item['children'], folder_path)

    try:
        recursive_create(settings.get('structure', []))
        logging.info("Folder structure creation finished.")
    except Exception:
        # S'assurer que le script s'arrête en cas d'erreur de création de dossier
        exit_script(EXIT_CODE_ERROR)

def clean_ahk_path(path_to_clean):
    """
    Cleans a file path for use in an AutoHotkey (v2) literal string.
    1. Normalizes the path (removes './' and '..').
    2. Escapes backslashes for AHK string syntax.

    Args:
        path_to_clean (str): The file path to prepare.

    Returns:
        str: The AHK-formatted path.
    """
    # 1. Normalize the path to remove './' and '..' (like in './.config')
    normalized_path = os.path.normpath(path_to_clean)
    
    # 2. Escape backslashes (convert \ to \\)
    ahk_escaped_path = normalized_path.replace('\\\\', '\\\\\\')
    
    return ahk_escaped_path

def post_build_actions(source_path, settings_data, is_initial_run, python_cmd_used, final_script_path):
    """
    Moves/copies the source settings.json to its final location and creates path.ahk.
    """
    # 1. Copy settings.json to its final destination
    config_relative_path = find_config_dir_path(settings_data, CONFIG_TYPE)
    if not config_relative_path:
        logging.error(f"The path for directory type '{CONFIG_TYPE}' was not found in settings.json.")
        exit_script(EXIT_CODE_ERROR)
        
    final_config_dir = os.path.join(os.getcwd(), config_relative_path)
    # Ensure the final absolute path is cleaned of '.' and '..'
    final_settings_path = os.path.normpath(os.path.join(final_config_dir, SETTINGS_FILE))

    if is_initial_run:
        # In 'Initial Run' mode, we MOVE the source file to its final destination.
        try:
            # The structure is already created by create_structure
            # os.makedirs(os.path.dirname(final_settings_path), exist_ok=True) 
            shutil.move(source_path, final_settings_path)
            logging.info(f"settings.json MOVED from '{source_path}' to '{final_settings_path}' (Initial Mode).")
        except Exception as e:
            logging.error(f"Error while moving settings.json: {e}")
            exit_script(EXIT_CODE_ERROR)
    elif not os.path.exists(final_settings_path):
        # If not initial run, but destination is missing, copy it (restore/repair case).
        try:
            shutil.copy2(source_path, final_settings_path)
            logging.info(f"settings.json copied from '{source_path}' to '{final_settings_path}'.")
        except Exception as e:
            logging.error(f"Error while copying settings.json: {e}")
            exit_script(EXIT_CODE_ERROR)
    else:
        logging.info(f"settings.json already exists at destination: {final_settings_path}. No copy/move action taken.")
        
    # 2. Create/Update path.ahk (the new path file)
    
    # IMPORTANT: Paths in the AHK file must escape backslashes for AHK literal strings.
    # Ex: C:\path\to -> "C:\\path\\to"
    final_settings_path_ahk = clean_ahk_path(final_settings_path)
    final_script_path_ahk = clean_ahk_path(final_script_path)
    
    ahk_content = f'{AHK_VAR_SETTINGS} := "{final_settings_path_ahk}"\n'
    ahk_content += f'{AHK_VAR_PYTHON_CMD} := "{python_cmd_used}"\n'
    ahk_content += f'{AHK_VAR_FINAL_SCRIPT} := "{final_script_path_ahk}"\n'
    
    paths_ahk_output_path = os.path.join(os.getcwd(), PATHFILE)
    
    try:
        with open(paths_ahk_output_path, 'w', encoding='utf-8') as f:
            f.write(ahk_content)
        logging.info(f"AHK config file '{PATHFILE}' created/updated successfully.")
    except Exception as e:
        logging.error(f"Error writing AHK file '{PATHFILE}': {e}")
        exit_script(EXIT_CODE_ERROR)

    return final_settings_path


# =================================================================
# HELPER FUNCTIONS FOR SETTINGS.AHK GENERATION
# =================================================================

def get_folder_name(item):
    """
    Détermine le nom du dossier à utiliser. Utilise 'name' si présent, sinon 'type'.
    """
    # Utilise 'name' si il est présent et non vide, sinon utilise 'type'.
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
    Valide et retourne la valeur booléenne de 'is_path'.
    Par défaut à True si la clé est absente.
    Retourne 'ERROR' en cas de valeur invalide.
    """
    path_setting = item.get('is_path', 'true') # Par défaut 'true' si absente
    
    if not isinstance(path_setting, str) or not path_setting.strip():
        if 'is_path' not in item:
            return True # Clé absente est valide, vaut True
        return 'ERROR' # Vide ou non-string
        
    path_setting_lower = path_setting.lower()
    
    if path_setting_lower == 'true':
        return True
    elif path_setting_lower == 'false':
        return False
    else:
        return 'ERROR' # Chaîne invalide

def generate_flat_path_structure(structure_list, parent_var_name):
    """
    Fonction récursive pour générer le code AHK pour les variables de chemin statiques
    au sein de la classe racine unique.
    """
    ahk_code_lines = []
    indent = "    " # 4 espaces

    for item in structure_list:
        class_type = item.get("type")
        if not class_type:
            logging.warning(f"Item skipped for AHK path var because 'type' is missing: {item}")
            continue
            
        path_status = is_valid_path_setting(item)
        
        if path_status == 'ERROR':
            # Cette erreur devrait être fatale et arrêtée plus tôt,
            # mais c'est un filet de sécurité.
            logging.error(f"Invalid 'is_path' value for type '{class_type}'. Skipping.")
            # Ne pas récurser si la configuration est invalide.
            continue
            
        item_folder_name = get_folder_name(item)
        if not item_folder_name:
            logging.warning(f"Item type '{class_type}' has no folder name ('name' or 'type'). Skipping path generation.")
            continue

        current_var_name = class_type
        children_to_process = item.get("children", [])
        
        # Déterminer le parent_var_name pour les enfants
        next_parent_var_name = parent_var_name # Par défaut, hérite du parent
        
        if path_status is True:
            # -----------------------------------------------------------------
            # 'is_path' est 'true', on génère la variable de chemin statique
            # -----------------------------------------------------------------
            
            # Le nom du dossier. AHKv2 peut concaténer une variable et une chaîne:
            # this.Library "\Core"
            ahk_path_segment = f'\\{item_folder_name}'
            
            # Générer la ligne
            # ex: static Core := this.Library "\Core"
            line = f'{indent}static {current_var_name} := {parent_var_name} "{ahk_path_segment}"'
            ahk_code_lines.append(line)
            
            # Le parent pour les enfants de cet item devient cet item
            next_parent_var_name = f'this.{current_var_name}'
            
        # else: (path_status is False)
            # On ne génère pas de ligne pour 'current_var_name'.
            # 'next_parent_var_name' reste 'parent_var_name' (le parent de cet item).
            # Les enfants seront donc rattachés au grand-parent.

        # 3. Récursion
        if children_to_process:
            ahk_code_lines.extend(generate_flat_path_structure(
                children_to_process, 
                next_parent_var_name
            ))
    
    return ahk_code_lines


    """
    Parcourt les dossiers supplémentaires (non définis dans settings.json)
    et demande à l'utilisateur s'il souhaite déplacer leur contenu.
    """
    import shutil, os, logging
    from tkinter import Tk, messagebox
    # S'assurer que 'time' est importé
    import time 
    
    logging.info(f"--- Démarrage de l'analyse des dossiers supplémentaires ---")
    if not extra_folders:
        logging.info("Aucun dossier supplémentaire trouvé. Suite.")
        return

    logging.info(f"Trouvé {len(extra_folders)} dossier(s) supplémentaire(s) : {extra_folders}")

    # 1. Initialisation critique de la fenêtre racine Tkinter
    try:
        root = Tk()
        root.withdraw() 
        # CORRECTION : Forcer Tkinter à traiter tous les événements.
        root.update()
        logging.debug("Tkinter root initialisé et mis à jour.")
    except Exception as e:
        logging.error(f"Erreur lors de l'initialisation de Tkinter: {e}. Arrêt de l'analyse.")
        return

    try:
        for folder in extra_folders:
            # 2. Vérifier si le dossier existe toujours
            if not os.path.exists(folder) or not os.path.isdir(folder):
                logging.info(f"'{folder}' n'existe plus ou n'est plus un dossier. Ignoré.")
                continue

            # 3. Demander pour déplacer
            move_q = (
                f"Le dossier suivant n'est pas défini dans settings.json :\n\n"
                f"{os.path.abspath(folder)}\n\n"
                f"Voulez-vous déplacer son contenu vers un dossier de projet valide ?"
            )
            
            # Utiliser root comme parent
            if not messagebox.askyesno("Dossier Inattendu Trouvé", move_q, parent=root): 
                logging.info(f"L'utilisateur a choisi d'ignorer le déplacement du contenu de '{folder}'.")
                continue 

            logging.info(f"L'utilisateur a choisi de déplacer le contenu de '{folder}'.")
            
            # 4. Si Oui, afficher le sélecteur de destination
            logging.info("Affichage du sélecteur...")
            destination = select_destination_dialog(root, expected_paths, folder)

            if not destination:
                logging.info(f"L'utilisateur a annulé la sélection de la destination pour '{folder}'.")
                continue 

            logging.info(f"L'utilisateur a sélectionné la destination '{destination}' pour le contenu de '{folder}'.")

            # 5. Déplacer le contenu (Logique inchangée)
            full_destination_path = os.path.join(os.getcwd(), destination)
            try:
                os.makedirs(full_destination_path, exist_ok=True)
                
                items_moved = 0
                
                if not os.listdir(folder):
                    logging.info(f"Le dossier '{folder}' est vide. Déplacement ignoré.")
                else:
                    for item_name in os.listdir(folder):
                        source_item = os.path.join(folder, item_name)
                        dest_item = os.path.join(full_destination_path, item_name)
                        
                        if os.path.exists(dest_item):
                            logging.warning(f"L'élément '{item_name}' existe déjà dans '{full_destination_path}'. Déplacement ignoré.")
                            continue
                            
                        shutil.move(source_item, dest_item)
                        logging.info(f"Déplacé : {source_item} -> {dest_item}")
                        items_moved += 1

                logging.info(f"Déplacement terminé pour '{folder}'. {items_moved} déplacé(s).")

            except Exception as e:
                logging.error(f"Erreur lors du déplacement du contenu de '{folder}' vers '{full_destination_path}': {e}")
                messagebox.showerror("Erreur de Déplacement", f"Une erreur est survenue lors du déplacement des fichiers de '{folder}':\n\n{e}", parent=root)
                continue 

            # 6. Demander pour supprimer (Logique inchangée)
            try:
                if not os.listdir(folder):
                    delete_q = f"Le dossier '{folder}' est maintenant vide.\n\nVoulez-vous le supprimer ?"
                    if messagebox.askyesno("Supprimer le Dossier Vide", delete_q, parent=root):
                        try:
                            os.rmdir(folder) 
                            logging.info(f"Dossier vide supprimé : {folder}")
                        except Exception as e:
                            logging.error(f"Échec de la suppression du dossier '{folder}': {e}")
                            messagebox.showerror("Erreur de Suppression", f"Impossible de supprimer le dossier '{folder}' (non-vide ou verrouillé):\n\n{e}", parent=root)
                else:
                    logging.info(f"Le dossier '{folder}' n'est pas vide après le déplacement. Suppression ignorée.")
            except Exception as e:
                logging.error(f"Erreur lors de la vérification si le dossier '{folder}' est vide : {e}")

    finally:
        # 7. Nettoyer la fenêtre racine cachée
        root.destroy()
        logging.info(f"--- Fin de l'analyse des dossiers supplémentaires ---")
    """
    Parcourt les dossiers supplémentaires (non définis dans settings.json)
    et demande à l'utilisateur s'il souhaite déplacer leur contenu.
    """
    import shutil, os, logging
    from tkinter import Tk, messagebox

    logging.info(f"--- Démarrage de l'analyse des dossiers supplémentaires ---")
    if not extra_folders:
        logging.info("Aucun dossier supplémentaire trouvé. Suite.")
        return

    logging.info(f"Trouvé {len(extra_folders)} dossier(s) supplémentaire(s) : {extra_folders}")

    # 1. Initialisation critique de la fenêtre racine Tkinter
    try:
        root = Tk()
        root.withdraw() # Garder la fenêtre racine cachée, mais active
        # CORRECTION CRITIQUE (Déjà appliquée): Forcer Tkinter à traiter tous les événements.
        root.update()
        logging.debug("Tkinter root initialisé et mis à jour.")
    except Exception as e:
        logging.error(f"Erreur lors de l'initialisation de Tkinter: {e}. Arrêt de l'analyse.")
        return

    try:
        for folder in extra_folders:
            # 2. Vérifier si le dossier existe toujours
            if not os.path.exists(folder) or not os.path.isdir(folder):
                logging.info(f"'{folder}' n'existe plus ou n'est plus un dossier. Ignoré.")
                continue

            # 3. Demander pour déplacer (utilise la fenêtre racine cachée 'root')
            move_q = (
                f"Le dossier suivant n'est pas défini dans settings.json :\n\n"
                f"{os.path.abspath(folder)}\n\n"
                f"Voulez-vous déplacer son contenu vers un dossier de projet valide ?"
            )
            
            if not messagebox.askyesno("Dossier Inattendu Trouvé", move_q, parent=root): 
                logging.info(f"L'utilisateur a choisi d'ignorer le déplacement du contenu de '{folder}'.")
                continue 

            logging.info(f"L'utilisateur a choisi de déplacer le contenu de '{folder}'.")
            
            # 4. Si Oui, afficher le sélecteur de destination (Appel à la fonction corrigée)
            logging.info("Affichage du sélecteur...")
            destination = select_destination_dialog(root, expected_paths, folder)

            if not destination:
                logging.info(f"L'utilisateur a annulé la sélection de la destination pour '{folder}'.")
                continue 

            logging.info(f"L'utilisateur a sélectionné la destination '{destination}' pour le contenu de '{folder}'.")

            # 5. Déplacer le contenu
            full_destination_path = os.path.join(os.getcwd(), destination)
            try:
                os.makedirs(full_destination_path, exist_ok=True)
                
                items_moved = 0
                
                if not os.listdir(folder):
                    logging.info(f"Le dossier '{folder}' est vide. Déplacement ignoré.")
                else:
                    for item_name in os.listdir(folder):
                        source_item = os.path.join(folder, item_name)
                        dest_item = os.path.join(full_destination_path, item_name)
                        
                        if os.path.exists(dest_item):
                            logging.warning(f"L'élément '{item_name}' existe déjà dans '{full_destination_path}'. Déplacement ignoré.")
                            continue
                            
                        shutil.move(source_item, dest_item)
                        logging.info(f"Déplacé : {source_item} -> {dest_item}")
                        items_moved += 1

                logging.info(f"Déplacement terminé pour '{folder}'. {items_moved} déplacé(s).")

            except Exception as e:
                logging.error(f"Erreur lors du déplacement du contenu de '{folder}' vers '{full_destination_path}': {e}")
                messagebox.showerror("Erreur de Déplacement", f"Une erreur est survenue lors du déplacement des fichiers de '{folder}':\n\n{e}", parent=root)
                continue 

            # 6. Demander pour supprimer
            try:
                if not os.listdir(folder):
                    delete_q = f"Le dossier '{folder}' est maintenant vide.\n\nVoulez-vous le supprimer ?"
                    if messagebox.askyesno("Supprimer le Dossier Vide", delete_q, parent=root):
                        try:
                            os.rmdir(folder) 
                            logging.info(f"Dossier vide supprimé : {folder}")
                        except Exception as e:
                            logging.error(f"Échec de la suppression du dossier '{folder}': {e}")
                            messagebox.showerror("Erreur de Suppression", f"Impossible de supprimer le dossier '{folder}' (non-vide ou verrouillé):\n\n{e}", parent=root)
                else:
                    logging.info(f"Le dossier '{folder}' n'est pas vide après le déplacement. Suppression ignorée.")
            except Exception as e:
                logging.error(f"Erreur lors de la vérification si le dossier '{folder}' est vide : {e}")

    finally:
        # 7. Nettoyer la fenêtre racine cachée
        root.destroy()
        logging.info(f"--- Fin de l'analyse des dossiers supplémentaires ---")
    """
    Parcourt les dossiers supplémentaires (non définis dans settings.json)
    et demande à l'utilisateur s'il souhaite déplacer leur contenu.
    """
    import shutil, os, logging
    from tkinter import Tk, messagebox

    logging.info(f"--- Démarrage de l'analyse des dossiers supplémentaires ---")
    if not extra_folders:
        logging.info("Aucun dossier supplémentaire trouvé. Suite.")
        return

    logging.info(f"Trouvé {len(extra_folders)} dossier(s) supplémentaire(s) : {extra_folders}")

    # 1. Initialisation critique de la fenêtre racine Tkinter
    try:
        root = Tk()
        root.withdraw() # Garder la fenêtre racine cachée, mais active
        # CORRECTION CRITIQUE (Déjà appliquée): Forcer Tkinter à traiter tous les événements.
        root.update()
        logging.debug("Tkinter root initialisé et mis à jour.")
    except Exception as e:
        logging.error(f"Erreur lors de l'initialisation de Tkinter: {e}. Arrêt de l'analyse.")
        return

    try:
        for folder in extra_folders:
            # 2. Vérifier si le dossier existe toujours
            if not os.path.exists(folder) or not os.path.isdir(folder):
                logging.info(f"'{folder}' n'existe plus ou n'est plus un dossier. Ignoré.")
                continue

            # 3. Demander pour déplacer (utilise la fenêtre racine cachée 'root')
            move_q = (
                f"Le dossier suivant n'est pas défini dans settings.json :\n\n"
                f"{os.path.abspath(folder)}\n\n"
                f"Voulez-vous déplacer son contenu vers un dossier de projet valide ?"
            )
            
            if not messagebox.askyesno("Dossier Inattendu Trouvé", move_q, parent=root): 
                logging.info(f"L'utilisateur a choisi d'ignorer le déplacement du contenu de '{folder}'.")
                continue 

            logging.info(f"L'utilisateur a choisi de déplacer le contenu de '{folder}'.")
            
            # 4. Si Oui, afficher le sélecteur de destination (Appel à la fonction corrigée)
            logging.info("Affichage du sélecteur...")
            destination = select_destination_dialog(root, expected_paths, folder)

            if not destination:
                logging.info(f"L'utilisateur a annulé la sélection de la destination pour '{folder}'.")
                continue 

            logging.info(f"L'utilisateur a sélectionné la destination '{destination}' pour le contenu de '{folder}'.")

            # 5. Déplacer le contenu
            full_destination_path = os.path.join(os.getcwd(), destination)
            try:
                os.makedirs(full_destination_path, exist_ok=True)
                
                items_moved = 0
                
                if not os.listdir(folder):
                    logging.info(f"Le dossier '{folder}' est vide. Déplacement ignoré.")
                else:
                    for item_name in os.listdir(folder):
                        source_item = os.path.join(folder, item_name)
                        dest_item = os.path.join(full_destination_path, item_name)
                        
                        if os.path.exists(dest_item):
                            logging.warning(f"L'élément '{item_name}' existe déjà dans '{full_destination_path}'. Déplacement ignoré.")
                            continue
                            
                        shutil.move(source_item, dest_item)
                        logging.info(f"Déplacé : {source_item} -> {dest_item}")
                        items_moved += 1

                logging.info(f"Déplacement terminé pour '{folder}'. {items_moved} déplacé(s).")

            except Exception as e:
                logging.error(f"Erreur lors du déplacement du contenu de '{folder}' vers '{full_destination_path}': {e}")
                messagebox.showerror("Erreur de Déplacement", f"Une erreur est survenue lors du déplacement des fichiers de '{folder}':\n\n{e}", parent=root)
                continue 

            # 6. Demander pour supprimer
            try:
                if not os.listdir(folder):
                    delete_q = f"Le dossier '{folder}' est maintenant vide.\n\nVoulez-vous le supprimer ?"
                    if messagebox.askyesno("Supprimer le Dossier Vide", delete_q, parent=root):
                        try:
                            os.rmdir(folder) 
                            logging.info(f"Dossier vide supprimé : {folder}")
                        except Exception as e:
                            logging.error(f"Échec de la suppression du dossier '{folder}': {e}")
                            messagebox.showerror("Erreur de Suppression", f"Impossible de supprimer le dossier '{folder}' (non-vide ou verrouillé):\n\n{e}", parent=root)
                else:
                    logging.info(f"Le dossier '{folder}' n'est pas vide après le déplacement. Suppression ignorée.")
            except Exception as e:
                logging.error(f"Erreur lors de la vérification si le dossier '{folder}' est vide : {e}")

    finally:
        # 7. Nettoyer la fenêtre racine cachée
        root.destroy()
        logging.info(f"--- Fin de l'analyse des dossiers supplémentaires ---")

    """
    Parcourt les dossiers supplémentaires (non définis dans settings.json)
    et demande à l'utilisateur s'il souhaite déplacer leur contenu.
    """
    import shutil, os, logging
    from tkinter import Tk, messagebox

    logging.info(f"--- Démarrage de l'analyse des dossiers supplémentaires ---")
    if not extra_folders:
        logging.info("Aucun dossier supplémentaire trouvé. Suite.")
        return

    logging.info(f"Trouvé {len(extra_folders)} dossier(s) supplémentaire(s) : {extra_folders}")

    # 1. Initialisation critique de la fenêtre racine Tkinter
    try:
        root = Tk()
        root.withdraw() # Garder la fenêtre racine cachée, mais active
        # CORRECTION CRITIQUE : Forcer Tkinter à traiter tous les événements.
        # Cela est ESSENTIEL pour s'assurer que les boîtes de dialogue modales (Toplevel/messagebox)
        # se dessinent correctement avant que l'exécution ne soit bloquée.
        root.update()
        logging.debug("Tkinter root initialisé et mis à jour.")
    except Exception as e:
        logging.error(f"Erreur lors de l'initialisation de Tkinter: {e}. Arrêt de l'analyse.")
        return

    try:
        for folder in extra_folders:
            # 2. Vérifier si le dossier existe toujours
            if not os.path.exists(folder) or not os.path.isdir(folder):
                logging.info(f"'{folder}' n'existe plus ou n'est plus un dossier. Ignoré.")
                continue

            # 3. Demander pour déplacer (utilise la fenêtre racine cachée 'root')
            move_q = (
                f"Le dossier suivant n'est pas défini dans settings.json :\n\n"
                f"{os.path.abspath(folder)}\n\n"
                f"Voulez-vous déplacer son contenu vers un dossier de projet valide ?"
            )
            
            if not messagebox.askyesno("Dossier Inattendu Trouvé", move_q, parent=root): 
                logging.info(f"L'utilisateur a choisi d'ignorer le déplacement du contenu de '{folder}'.")
                continue 

            logging.info(f"L'utilisateur a choisi de déplacer le contenu de '{folder}'.")
            
            # 4. Si Oui, afficher le sélecteur de destination (Appel à la fonction corrigée)
            logging.info("Affichage du sélecteur...")
            destination = select_destination_dialog(root, expected_paths, folder)

            if not destination:
                logging.info(f"L'utilisateur a annulé la sélection de la destination pour '{folder}'.")
                continue 

            logging.info(f"L'utilisateur a sélectionné la destination '{destination}' pour le contenu de '{folder}'.")

            # 5. Déplacer le contenu (Logique inchangée)
            full_destination_path = os.path.join(os.getcwd(), destination)
            try:
                os.makedirs(full_destination_path, exist_ok=True)
                
                items_moved = 0
                items_skipped = 0
                
                # ... (Logique de déplacement inchangée : listdir, shutil.move, etc.)
                
                # Vérifier si le dossier à déplacer est vide avant de lister
                if not os.listdir(folder):
                    logging.info(f"Le dossier '{folder}' est vide. Déplacement ignoré.")
                else:
                    for item_name in os.listdir(folder):
                        source_item = os.path.join(folder, item_name)
                        dest_item = os.path.join(full_destination_path, item_name)
                        
                        if os.path.exists(dest_item):
                            logging.warning(f"L'élément '{item_name}' existe déjà dans '{full_destination_path}'. Déplacement ignoré.")
                            items_skipped += 1
                            continue
                            
                        # Utilisation de shutil.move() pour déplacer l'élément
                        shutil.move(source_item, dest_item)
                        logging.info(f"Déplacé : {source_item} -> {dest_item}")
                        items_moved += 1

                logging.info(f"Déplacement terminé pour '{folder}'. {items_moved} déplacé(s), {items_skipped} ignoré(s).")

            except Exception as e:
                logging.error(f"Erreur lors du déplacement du contenu de '{folder}' vers '{full_destination_path}': {e}")
                messagebox.showerror("Erreur de Déplacement", f"Une erreur est survenue lors du déplacement des fichiers de '{folder}':\n\n{e}", parent=root)
                continue 

            # 6. Demander pour supprimer (Logique inchangée)
            try:
                if not os.listdir(folder):
                    delete_q = f"Le dossier '{folder}' est maintenant vide.\n\nVoulez-vous le supprimer ?"
                    if messagebox.askyesno("Supprimer le Dossier Vide", delete_q, parent=root):
                        try:
                            # os.rmdir ne supprime que les dossiers vides
                            os.rmdir(folder) 
                            logging.info(f"Dossier vide supprimé : {folder}")
                        except Exception as e:
                            logging.error(f"Échec de la suppression du dossier '{folder}': {e}")
                            messagebox.showerror("Erreur de Suppression", f"Impossible de supprimer le dossier '{folder}' (non-vide ou verrouillé):\n\n{e}", parent=root)
                else:
                    logging.info(f"Le dossier '{folder}' n'est pas vide après le déplacement. Suppression ignorée.")
            except Exception as e:
                logging.error(f"Erreur lors de la vérification si le dossier '{folder}' est vide : {e}")

    finally:
        # 7. Nettoyer la fenêtre racine cachée
        root.destroy()
        logging.info(f"--- Fin de l'analyse des dossiers supplémentaires ---")

    """
    Parcourt les dossiers supplémentaires (non définis dans settings.json)
    et demande à l'utilisateur s'il souhaite déplacer leur contenu.
    """
    import shutil, os, logging
    from tkinter import Tk, messagebox

    logging.info(f"--- Démarrage de l'analyse des dossiers supplémentaires ---")
    if not extra_folders:
        logging.info("Aucun dossier supplémentaire trouvé. Suite.")
        return

    logging.info(f"Trouvé {len(extra_folders)} dossier(s) supplémentaire(s) : {extra_folders}")

    # 1. Nous avons besoin d'une fenêtre racine cachée pour nos boîtes de dialogue
    try:
        root = Tk()
        root.withdraw() # Garder la fenêtre racine cachée, mais active
    except Exception as e:
        logging.error(f"Erreur lors de l'initialisation de Tkinter: {e}. Arrêt de l'analyse.")
        return

    try:
        for folder in extra_folders:
            # 2. Vérifier si le dossier existe toujours
            # Utilisation de os.path.isdir pour une vérification plus stricte
            if not os.path.exists(folder) or not os.path.isdir(folder):
                logging.info(f"'{folder}' n'existe plus ou n'est plus un dossier. Ignoré.")
                continue

            # 3. Demander pour déplacer
            move_q = (
                f"Le dossier suivant n'est pas défini dans settings.json :\n\n"
                f"{os.path.abspath(folder)}\n\n"
                f"Voulez-vous déplacer son contenu vers un dossier de projet valide ?"
            )
            
            # Utiliser root comme parent pour l'askyesno
            if not messagebox.askyesno("Dossier Inattendu Trouvé", move_q, parent=root): 
                logging.info(f"L'utilisateur a choisi d'ignorer le déplacement du contenu de '{folder}'.")
                continue 

            logging.info(f"L'utilisateur a choisi de déplacer le contenu de '{folder}'.")
            
            # 4. Si Oui, afficher le sélecteur de destination
            logging.info("Affichage du sélecteur...")
            # Appel à la fonction corrigée
            destination = select_destination_dialog(root, expected_paths, folder)

            if not destination:
                logging.info(f"L'utilisateur a annulé la sélection de la destination pour '{folder}'.")
                continue 

            logging.info(f"L'utilisateur a sélectionné la destination '{destination}' pour le contenu de '{folder}'.")

            # 5. Déplacer le contenu
            full_destination_path = os.path.join(os.getcwd(), destination)
            try:
                os.makedirs(full_destination_path, exist_ok=True)
                
                items_moved = 0
                items_skipped = 0
                
                # Vérifier si le dossier à déplacer est vide avant de lister
                if not os.listdir(folder):
                    logging.info(f"Le dossier '{folder}' est vide. Déplacement ignoré.")
                    items_skipped = 0
                else:
                    for item_name in os.listdir(folder):
                        source_item = os.path.join(folder, item_name)
                        dest_item = os.path.join(full_destination_path, item_name)
                        
                        if os.path.exists(dest_item):
                            logging.warning(f"L'élément '{item_name}' existe déjà dans '{full_destination_path}'. Déplacement ignoré.")
                            items_skipped += 1
                            continue
                            
                        shutil.move(source_item, dest_item)
                        logging.info(f"Déplacé : {source_item} -> {dest_item}")
                        items_moved += 1

                logging.info(f"Déplacement terminé pour '{folder}'. {items_moved} déplacé(s), {items_skipped} ignoré(s).")

            except Exception as e:
                logging.error(f"Erreur lors du déplacement du contenu de '{folder}' vers '{full_destination_path}': {e}")
                messagebox.showerror("Erreur de Déplacement", f"Une erreur est survenue lors du déplacement des fichiers de '{folder}':\n\n{e}", parent=root)
                continue 

            # 6. Demander pour supprimer
            try:
                # Re-vérifier si le dossier est vide APRES le déplacement
                if not os.listdir(folder):
                    delete_q = f"Le dossier '{folder}' est maintenant vide.\n\nVoulez-vous le supprimer ?"
                    if messagebox.askyesno("Supprimer le Dossier Vide", delete_q, parent=root):
                        try:
                            # Utiliser os.rmdir car il ne supprime que les dossiers vides
                            os.rmdir(folder) 
                            logging.info(f"Dossier vide supprimé : {folder}")
                        except Exception as e:
                            logging.error(f"Échec de la suppression du dossier '{folder}': {e}")
                            messagebox.showerror("Erreur de Suppression", f"Impossible de supprimer le dossier '{folder}' (il est peut-être à nouveau non-vide ou verrouillé):\n\n{e}", parent=root)
                else:
                    logging.info(f"Le dossier '{folder}' n'est pas vide après le déplacement. Suppression ignorée.")
            except Exception as e:
                logging.error(f"Erreur lors de la vérification si le dossier '{folder}' est vide : {e}")

    finally:
        # 7. Nettoyer la fenêtre racine cachée
        root.destroy()
        logging.info(f"--- Fin de l'analyse des dossiers supplémentaires ---")
    """
    Parcourt les dossiers supplémentaires (non définis dans settings.json)
    et demande à l'utilisateur s'il souhaite déplacer leur contenu.
    """
    logging.info(f"--- Démarrage de l'analyse des dossiers supplémentaires ---")
    if not extra_folders:
        logging.info("Aucun dossier supplémentaire trouvé. Suite.")
        return

    logging.info(f"Trouvé {len(extra_folders)} dossier(s) supplémentaire(s) : {extra_folders}")

    # 1. Nous avons besoin d'une fenêtre racine cachée pour nos boîtes de dialogue
    root = Tk()
    root.withdraw() # Garder la fenêtre racine cachée, mais active

    for folder in extra_folders:
        # 2. Vérifier si le dossier existe toujours
        if not os.path.exists(folder) or not os.path.isdir(folder):
            logging.info(f"'{folder}' n'existe plus ou n'est plus un dossier. Ignoré.")
            continue

        # 3. Demander pour déplacer
        move_q = (
            f"Le dossier suivant n'est pas défini dans settings.json :\n\n"
            f"{folder}\n\n"
            f"Voulez-vous déplacer son contenu vers un dossier de projet valide ?"
        )
        # Utiliser root comme parent pour l'askyesno
        if not messagebox.askyesno("Dossier Inattendu Trouvé", move_q, parent=root): 
            logging.info(f"L'utilisateur a choisi d'ignorer le déplacement du contenu de '{folder}'.")
            continue 

        logging.info(f"L'utilisateur a choisi de déplacer le contenu de '{folder}'.")
        
        # 4. Si Oui, afficher le sélecteur de destination
        # Le dialogue sera modal par rapport à 'root'
        logging.info("Affichage du sélecteur...")
        destination = select_destination_dialog(root, expected_paths, folder)

        if not destination:
            logging.info(f"L'utilisateur a annulé la sélection de la destination pour '{folder}'.")
            continue 

        logging.info(f"L'utilisateur a sélectionné la destination '{destination}' pour le contenu de '{folder}'.")

        # 5. Déplacer le contenu (Logique inchangée, elle est correcte)
        try:
            os.makedirs(destination, exist_ok=True)
            
            items_moved = 0
            items_skipped = 0
            
            for item_name in os.listdir(folder):
                source_item = os.path.join(folder, item_name)
                dest_item = os.path.join(destination, item_name)
                
                if os.path.exists(dest_item):
                    logging.warning(f"L'élément '{item_name}' existe déjà dans '{destination}'. Déplacement ignoré.")
                    items_skipped += 1
                    continue
                    
                shutil.move(source_item, dest_item)
                logging.info(f"Déplacé : {source_item} -> {dest_item}")
                items_moved += 1

            logging.info(f"Déplacement terminé pour '{folder}'. {items_moved} déplacé(s), {items_skipped} ignoré(s).")

        except Exception as e:
            logging.error(f"Erreur lors du déplacement du contenu de '{folder}' vers '{destination}': {e}")
            messagebox.showerror("Erreur de Déplacement", f"Une erreur est survenue lors du déplacement des fichiers de '{folder}':\n\n{e}", parent=root)
            continue 

        # 6. Demander pour supprimer (Logique inchangée, elle est correcte)
        try:
            if not os.listdir(folder):
                delete_q = f"Le dossier '{folder}' est maintenant vide.\n\nVoulez-vous le supprimer ?"
                if messagebox.askyesno("Supprimer le Dossier Vide", delete_q, parent=root):
                    try:
                        os.rmdir(folder)
                        logging.info(f"Dossier vide supprimé : {folder}")
                    except Exception as e:
                        logging.error(f"Échec de la suppression du dossier '{folder}': {e}")
                        messagebox.showerror("Erreur de Suppression", f"Impossible de supprimer le dossier '{folder}':\n\n{e}", parent=root)
            else:
                logging.info(f"Le dossier '{folder}' n'est pas vide après le déplacement. Suppression ignorée.")
        except Exception as e:
            logging.error(f"Erreur lors de la vérification si le dossier '{folder}' est vide : {e}")

    # 7. Nettoyer la fenêtre racine cachée
    root.destroy()
    logging.info(f"--- Fin de l'analyse des dossiers supplémentaires ---")
# =================================================================
# HELPER FUNCTIONS FOR AHK INCLUDES GENERATION & COMPARISON
# =================================================================

def is_valid_include_setting(item):
    """
    Valide et retourne si l'élément doit être inclus dans la structure (dossier) ET dans les includes AHK.
    """
    # Si la clé n'est pas présente, on suppose 'true' (l'ancienne logique)
    include_setting = item.get('is_include', 'true') 
    
    # Si la valeur n'est pas une chaîne ou si elle est vide après nettoyage, on retourne 'ERROR'
    if not isinstance(include_setting, str) or not include_setting.strip():
        # Si la clé est manquante (retourne la valeur par défaut 'true'), on ne retourne pas 'ERROR'
        # On utilise directement la valeur par défaut ici :
        if 'is_include' not in item:
            return True
        # Sinon, c'est une clé vide ou malformée
        return 'ERROR' 
        
    include_setting_lower = include_setting.lower()
    
    if include_setting_lower == 'true':
        return True
    elif include_setting_lower == 'false':
        return False
    else:
        # Toute autre chaîne est invalide
        return 'ERROR'  

def extract_ahk_generated_content(settings, root_name):
    """
    Génère les lignes AHK pour la structure de classe (plate) et les includes.

    Returns:
        tuple: (structure_lines, include_string)
    """
    structure_lines = []
    structure_list = settings.get("structure", [])
    
    # --- 1. New class structure generation (Flat) ---
    if root_name != "Unknown_Root":
        # Start of the root class
        structure_lines.append(f'class A_Path\n{{')
        
        # Add the base rootDir
        structure_lines.append(f"    static rootDir := A_ScriptDir")
        
        # Add any other root-level properties from settings.json (e.g., if user added custom ones)
        for key, val in settings.items():
            if key not in ("structure", "RootName"):
                formatted_val = format_ahk_value(val)
                structure_lines.append(f"    static {key} := {formatted_val}")

        # Recursive call for children path variables
        path_var_lines = generate_flat_path_structure(
            structure_list, 
            "this.rootDir"
        )
        structure_lines.extend(path_var_lines)
        
        structure_lines.append(f'\n}}') # Close the root class

    # --- 2. Generate #include directives (Unchanged) ---
    base_project_dir = os.getcwd() 
    include_string = generate_ahk_includes(structure_list, root_name, base_project_dir, CONFIG_TYPE)
    
    return "\n".join(structure_lines), include_string

def generate_ahk_includes(structure_list, root_name, base_dir, config_type_name):
    """
    Analyse récursivement la structure du projet à la recherche de fichiers .ahk et génère
    les déclarations #include, regroupées par contexte Active.

    Le chemin du système de fichiers est maintenant reconstruit en utilisant la clé 'type'.
    """
    # Utilisation d'un dictionnaire pour grouper les includes par leur condition WinActive.
    # La clé None est réservée aux includes globaux (pas de HotIf).
    grouped_includes = {}
    
    # Utilise %A_ScriptDir% pour rendre les inclusions relatives au script AHK principal
    ahk_root = "%A_ScriptDir%" 

    def find_files_recursive(node_list, fs_path_prefix, ahk_path_prefix, inherited_win_active=None, inherited_include_status=True):
        """Helper récursif pour trouver les fichiers et les trier."""
        
        for node in node_list:
            node_type = node.get("type")

            #Récupère le statut du nœud actuel (True, False, ou 'ERROR')
            node_include_status = is_valid_include_setting(node)
        
            if node_include_status == 'ERROR':
                # L'erreur est gérée en amont, mais c'est un filet de sécurité.
                logging.error(f"Validation d'include échouée pour le nœud {node_type}. Skipping includes.")
                continue
        
            # Le statut d'inclusion effectif est la combinaison du statut hérité et du statut local.
            # Si l'héritage est False, l'effectif doit être False.
            current_effective_include_status = inherited_include_status and node_include_status
            
            # Détermine le winActive pour ce nœud : soit celui du nœud, soit celui hérité.
            current_win_active = node.get("Active", inherited_win_active)

            # 1. Ignorer complètement le répertoire de configuration
            if node_type == config_type_name:
                logging.info(f"Skipping include scan for node type: {node_type}")
                if node.get("children"):
                    find_files_recursive(node.get("children"), fs_path_prefix, ahk_path_prefix, current_win_active)
                continue
                
            if not node_type:
                if node.get("children"):
                    find_files_recursive(node.get("children"), fs_path_prefix, ahk_path_prefix, current_win_active)
                continue
                
            # 2. Reconstruire le chemin du système de fichiers (fs_path)
            current_fs_path_segment = get_folder_name(node)
            full_fs_path = os.path.normpath(os.path.join(base_dir, fs_path_prefix, current_fs_path_segment))
            
            # 3. Reconstruire le chemin de la classe AHK (ahk_path)
            current_ahk_path_list = ahk_path_prefix + [node_type]
            
            # 4. Scanner les fichiers .ahk dans le chemin du nœud
            found_ahk_files = []

            # --- Condition de scan avec le statut EFFECTIF ---
            if current_effective_include_status is True and os.path.isdir(full_fs_path):
                logging.debug(f"Scanning for AHK files in: {full_fs_path}")
                # Parcourir uniquement le répertoire courant (pas de récursion)
                for item_name in os.listdir(full_fs_path):
                    if item_name.lower().endswith(".ahk") and os.path.isfile(os.path.join(full_fs_path, item_name)):
                        # Créer un chemin relatif depuis la racine du projet (base_dir)
                        relative_path = os.path.relpath(os.path.join(full_fs_path, item_name), base_dir)
                        logging.debug(f"AHK files found: {relative_path}")
                        # Formater pour AHK (barres obliques inverses)
                        ahk_include_path = relative_path.replace(os.sep, "\\")

                        # Utiliser %A_ScriptDir% pour la portabilité
                        found_ahk_files.append(f'#include "{ahk_root}\\{ahk_include_path}"')
            elif current_effective_include_status is False:
                # Ce log confirmera que le scan a été sauté à cause de l'héritage de 'false'
                logging.info(f"Skipping AHK includes for node type: {node_type} (effective 'is_include': 'false')")
            
            # 5. Assigner les fichiers trouvés à la bonne liste
            if found_ahk_files:
                # FIX: Utiliser None pour toutes les conditions globales ("Windows" ou aucune)
                if current_win_active and current_win_active.lower() == "windows":
                    context_key = None
                    context_description = "Global (Windows/Always Active)"
                elif current_win_active:
                    context_key = current_win_active # Contexte spécifique (ex: ahk_class Premiere Pro)
                    context_description = current_win_active
                else:
                    context_key = None # Contexte totalement global (pas de winActive)
                    context_description = "Global (Always Active)"

                if context_key not in grouped_includes:
                    grouped_includes[context_key] = []
                
                # Ajouter un commentaire de source pour faciliter la maintenance
                grouped_includes[context_key].append(f"\n; --- Source: {'.'.join(current_ahk_path_list)} ---")
                grouped_includes[context_key].extend(sorted(found_ahk_files))

            # 6. Récursion dans les enfants
            if node.get("children"): 
                # IMPORTANT : On transmet le current_win_active aux enfants
                find_files_recursive(
                    node.get("children"),
                    os.path.join(fs_path_prefix, current_fs_path_segment),
                    current_ahk_path_list,
                    current_win_active,
                    current_effective_include_status
                )

    # Initial call to the recursive helper
    # base_dir est os.getcwd() passé depuis generate_SETTINGS_OUTPUT
    find_files_recursive(structure_list, '', [root_name])
    
    # --- 7. Génération du contenu final des includes ---
    final_includes = []
    SECTION_SEPARATOR = "=" * 40
    
    final_includes.append(f'\n; {SECTION_SEPARATOR}\n; --- AUTO-GENERATED SCRIPT INCLUDES ---\n; {SECTION_SEPARATOR}\n')
    
    # A. Global Includes (key None) - Mergés et sans HotIf
    global_content = grouped_includes.pop(None, [])
    
    if global_content:
        final_includes.append(f'; --- 1. Global Includes (Always Active) ---\n')
        final_includes.extend(global_content)
        
    # B. Context-Sensitive Includes (Tous les autres clés)
    if grouped_includes:
        final_includes.append(f'\n; --- 2. Context-Sensitive (HotIf) Includes ---\n')
        
        # Trie les clés pour un ordre de sortie stable (alphabétique)
        sorted_keys = sorted(grouped_includes.keys())
        
        for win_active_condition in sorted_keys:
            
            includes = grouped_includes[win_active_condition]
            
            # Début du bloc #HotIf
            final_includes.append(f'\n; --- Context: {win_active_condition} ---')
            final_includes.append(f'#HotIf WinActive("{win_active_condition}")')
            
            # Ajout des includes
            final_includes.extend(includes)
            
            # Fin du bloc #HotIf
            final_includes.append(f'#HotIf ; End context {win_active_condition}')
            
    # Réinitialisation finale pour s'assurer qu'aucun contexte ne subsiste dans le thread principal du script
    final_includes.append("\n#HotIf ; Final context reset")
    
    return "\n".join(final_includes)

# =================================================================
# GENERATION FUNCTION
# =================================================================

def generate_SETTINGS_OUTPUT(settings, final_settings_path, python_cmd_used, is_initial_run, final_script_path):
    """
    Generates the settings.ahk file used by the AHK application,
    including the class structure based on settings.json.
    """
    logging.info(f"Generating output AHK file: {SETTINGS_OUTPUT}")
    
    # Escape the path for the AHK_SETTINGS_FILE variable
    settings_path_ahk = clean_ahk_path(final_settings_path)
    final_script_path_ahk = clean_ahk_path(final_script_path)
    root_name = settings.get("RootName", "Unknown_Root")
    output_path = os.path.join(os.getcwd(), SETTINGS_OUTPUT)

    # --- 1. Base AHK content (Variables) ---
    # Ces variables doivent TOUJOURS être mises à jour pour s'assurer que les chemins sont corrects.
    ahk_base_vars_content = [
        f'{AHK_VAR_SETTINGS} := "{settings_path_ahk}"',
        f'{AHK_VAR_PYTHON_CMD} := "{python_cmd_used}"',
        f'{AHK_VAR_FINAL_SCRIPT} := "{final_script_path_ahk}"',
        f'AHK_ROOT_NAME := "{root_name}"'
    ]


    # --- 2. Générer le contenu dynamique (Classes et Includes) ---
    generated_structure_string, generated_include_string = extract_ahk_generated_content(settings, root_name)

    # --- 3. Comparaison (si non initial run et fichier existant) ---
    should_rewrite = True
    
    if not is_initial_run and os.path.exists(output_path):
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            
            # Pour la comparaison, on ne prend que la partie générée (structure + includes)
            # On cherche le début de la structure de classe, ou le début des includes
            
            # Le RootName est le marqueur de début de la structure de classe
            structure_start_marker = f'class {root_name}'
            
            # Le contenu généré à comparer (structure + includes)
            new_generated_content = (
                f'\n; Configuration structure based on {SETTINGS_FILE}' + '\n' +
                generated_structure_string + '\n' + 
                generated_include_string
            ).strip()

            # Tenter de trouver le contenu existant généré
            if generated_structure_string:
                # Si la structure de classe est générée, on cherche à partir de son début
                start_index = existing_content.find(structure_start_marker)
            elif generated_include_string:
                # Sinon, on cherche à partir du début des includes
                start_index = existing_content.find('; ========================================================')
            else:
                start_index = -1 # Aucun contenu dynamique

            if start_index != -1:
                existing_generated_content = existing_content[start_index:].strip()
                
                # Comparaison
                if existing_generated_content == new_generated_content:
                    # Pour être sûr, on vérifie aussi les variables de base
                    if all(line in existing_content for line in ahk_base_vars_content):
                        logging.info("AHK configuration file content (Classes/Includes) is identical. Skipping rewrite.")
                        should_rewrite = False
                        
        except Exception as e:
            logging.warning(f"Error during existing AHK file comparison: {e}. Forcing rewrite.")
            # should_rewrite reste à True
    
    # --- 4. Écriture du fichier si nécessaire ---
    if not should_rewrite:
        return # Fin de la fonction sans écriture

    # --- 5. Reconstruction du contenu AHK final ---
    ahk_content_lines = [
        f'; Configuration file generated by {os.path.basename(__file__)} on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        f'#Requires AutoHotkey v2.0\n',
        
        f'; Specific structure variables (Can be expanded if needed)',
        ahk_base_vars_content[3], # AHK_ROOT_NAME
    ]
    
    if generated_structure_string:
        ahk_content_lines.append(f'\n; Configuration structure based on {SETTINGS_FILE}')
        ahk_content_lines.append(generated_structure_string)
        
    if generated_include_string:
        ahk_content_lines.append(generated_include_string)
    
    # --- 6. Write the file ---
    ahk_content = "\n".join(ahk_content_lines)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ahk_content)
        logging.info(f"AHK file '{SETTINGS_OUTPUT}' generated successfully at: {output_path}")
    except Exception as e:
        logging.error(f"Error writing AHK file '{SETTINGS_OUTPUT}': {e}")
        exit_script(EXIT_CODE_ERROR)

def final_script_actions(final_script_name, is_initial_run, generated_ahk_config_file):
    """
    Gère la création initiale du script AHK final ou son lancement.
    MODIFIÉ: Le script AHK est maintenant lancé lors d'une exécution standard.
    """
    script_path = os.path.join(os.getcwd(), final_script_name)
    # Récupère le nom du fichier AHK de configuration (ex: settings.ahk)
    script_path_ahk = os.path.basename(generated_ahk_config_file)
    
    if is_initial_run:
        logging.info(f"Initial run: Creating base AHK script '{final_script_name}'.")
        
        # Le contenu minimal pour le script AHK final
        base_content = [
            f'; Auto-generated start script for {final_script_name}',
            f'#Requires AutoHotkey v2.0',
            f'#include "{script_path_ahk}"', # Inclure le fichier settings.ahk/Includes.ahk généré
            f'\n; Your custom code starts here'
        ]
        
        try:
            # 'w' assure que si le fichier existe, son contenu est écrasé/mis à jour avec la base.
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(base_content))
            logging.info(f"Base AHK script '{final_script_name}' created successfully.")
        except Exception as e:
            logging.error(f"Error writing base AHK script '{final_script_name}': {e}")
            # Le processus de construction n'est pas interrompu
            
    else:
        # Lancer le script AHK
        logging.info(f"Standard run: Attempting to launch '{final_script_name}'.")

        if os.path.exists(script_path):
            try:
                # Lance le script AHK en utilisant le programme associé (AutoHotkey)
                os.startfile(script_path)
                logging.info(f"Launched '{final_script_name}' successfully.")
            except Exception as e:
                # En cas d'échec de lancement
                logging.error(f"Failed to launch '{final_script_name}'. Please launch it manually. Error: {e}")
        else:
            logging.warning(f"File '{final_script_name}' not found at '{script_path}'. Skipping launch.")
            
# =================================================================
# EXECUTIONS
# =================================================================
def main_build():

    # ------------------------------------------------------------------------------------
    # 0. Try to get the python command, the output 'path' en 'include' file name passed as arguments
    # ------------------------------------------------------------------------------------
    global SETTINGS_OUTPUT, PATHFILE, AHK_VAR_FINAL_SCRIPT_PATH 
    
    AHK_VAR_FINAL_SCRIPT_PATH = None 

    try:
        # sys.argv[2] est le chemin de la commande Python
        python_absolutePath = sys.argv[2] 
        logging.info(f"Python command detected via command-line argument: {python_absolutePath}")

        # sys.argv[3] est le nom du fichier AHK de sortie (ex: Includes.ahk)
        PATHFILE = sys.argv[3] # PATHFILE est un alias de SETTINGS_OUTPUT
        logging.info(f"Output PATHFILE file name detected via command-line argument: {PATHFILE}")

        # sys.argv[3] est le nom du fichier AHK Path de sortie (ex: path.ahk)
        SETTINGS_OUTPUT = sys.argv[4]
        logging.info(f"Output SETTINGS_OUTPUT file name detected via command-line argument: {SETTINGS_OUTPUT}")

    except IndexError:
        # L'argument du script AHK final n'est plus obligatoire (arg 4)
        raise ValueError("Error: Arguments are missing. Please provide the Python command (arg 2) AND the AHK output file name (arg 3). The final script name is now read from 'RootName' in settings.json.")

    # ------------------------------------------------------------------------------------
    # 1. Parse path.ahk to get the location of settings.json
    # ------------------------------------------------------------------------------------
    logging.info(f"Attempting to load paths from AHK file: {PATHFILE}")
    
    paths_ahk_abs_path = os.path.join(os.getcwd(), PATHFILE)
    
    settings_path_from_ahk = None
    is_initial_run = False # Flag to track if this is a first-time setup

    if os.path.exists(paths_ahk_abs_path):
        # Try to load paths from the existing path.ahk
        paths_info = read_ahk_variables(paths_ahk_abs_path) 
        if paths_info:
            settings_path_from_ahk, python_absolutePath, AHK_VAR_FINAL_SCRIPT_PATH = paths_info
    
    # This is the path where we expect to find settings.json on an initial run
    settings_json_source_abs_path = os.path.join(os.getcwd(), SETTINGS_FILE)

    # ------------------------------------------------------------------------------------
    # 2. If path.ahk is missing, invalid, or settings.json not found at its usual spot,
    #    try loading settings.json from the current directory.
    # ------------------------------------------------------------------------------------
    settings_data = None
    
    if settings_path_from_ahk and os.path.exists(settings_path_from_ahk):
        # path.ahk is present and valid, so settings.json is found via path.ahk
        settings_data_check = load_settings_json(settings_path_from_ahk)
        if settings_data_check:
            settings_data, _ = settings_data_check
            logging.info(f"Configuration path confirmed by '{PATHFILE}'.")
        else:
            # The path exists but the JSON is invalid, switching to local mode.
            logging.warning(f"Remote settings.json file is invalid. Attempting local load.")
    
    if not settings_data:
        # Try to load settings.json from the current directory
        local_settings_data_check = load_settings_json(settings_json_source_abs_path)
        
        # ------------------------------------------------------------------------------------
        # 3. If settings.json is in the current directory, this is a 'New Structure' run.
        # ------------------------------------------------------------------------------------
        if local_settings_data_check:
            settings_data, settings_json_source_abs_path = local_settings_data_check
            is_initial_run = True # Set the initial run flag
            logging.info("'New Structure' mode detected: Loading settings.json locally.")

    # ------------------------------------------------------------------------------------
    # 4. If settings.json is missing locally, throw a fatal error.
    # ------------------------------------------------------------------------------------
    if not settings_data:
        logging.fatal(f"Could not find or load '{SETTINGS_FILE}' locally or via '{PATHFILE}'.")
        exit_script(EXIT_CODE_ERROR)

    root_name = settings_data.get("RootName") 
    if not root_name:
        raise ValueError("Error: 'RootName' key is missing in your settings.json file. It is now mandatory to define the final script name.")
        
    # Le nom du script final est 'RootName' + '.ahk'
    AHK_VAR_FINAL_SCRIPT_PATH = f"{root_name}.ahk"
    logging.info(f"Final AHK Script file name determined from 'RootName': {AHK_VAR_FINAL_SCRIPT_PATH}")

    # ------------------------------------------------------------------------------------
    # 5. path.ahk present and valid... (This case was already handled in step 2)
    # ------------------------------------------------------------------------------------
    
    # ------------------------------------------------------------------------------------
    # 6. Check for the 'structure' key (regardless of load mode)
    # ------------------------------------------------------------------------------------

    # Validation 1: structure
    if 'structure' not in settings_data:
        logging.error("The 'structure' key is missing in the settings.json file.")
        exit_script(EXIT_CODE_ERROR)

    is_valid = True
    
    # Validation 2: RootName
    if 'RootName' not in settings_data or not settings_data.get('RootName'):
        logging.error("Mandatory key 'RootName' is missing or empty in settings.json.")
        is_valid = False
    
    # Validation 3: Configuration path
    # Utilise la fonction existante pour trouver le chemin de configuration
    config_relative_path = find_config_dir_path(settings_data, CONFIG_TYPE)
    if not config_relative_path:
        logging.error(f"Mandatory key 'type' for structure item type '{CONFIG_TYPE}' is missing or empty in settings.json.")
        is_valid = False

    if not is_valid:
        # Sortir du script avec une erreur fatale si les validations échouent
        exit_script(EXIT_CODE_ERROR) 
        
    logging.info("Mandatory keys 'RootName' and 'Configuration' path are present.")
        

    # ------------------------------------------------------------------------------------
    # 7. Generate expected paths from the JSON
    # ------------------------------------------------------------------------------------
    try:
        expected_paths = get_expected_paths(settings_data['structure'])
    except ValueError as e:
        # CAPTURE l'erreur de validation levée dans get_expected_paths
        logging.fatal(f"FATAL VALIDATION ERROR: {e}")
        exit_script(EXIT_CODE_ERROR)
    
    # ------------------------------------------------------------------------------------
    # 8. Compare current structure and ask for user confirmation.
    # 9. The warning is skipped if is_initial_run is True.
    # ------------------------------------------------------------------------------------
    missing_folders = compare_structure(expected_paths, is_initial_run)
    
    # ------------------------------------------------------------------------------------
    # 10. Generate structure and run Post-build: Copy original settings.json and create path.ahk
    # ------------------------------------------------------------------------------------
    # Create the structure (safe to run even if folders exist)
    create_structure(settings_data)
    
    # Post-build (Copy/Move JSON and write new path.ahk)
    final_settings_path = post_build_actions(
        source_path=settings_json_source_abs_path,
        settings_data=settings_data,
        is_initial_run=is_initial_run,
        python_cmd_used=python_absolutePath,
        final_script_path=AHK_VAR_FINAL_SCRIPT_PATH
    )
    
    # ------------------------------------------------------------------------------------
    # 11. Generate the AHK configuration file (now with the class structure)
    # ------------------------------------------------------------------------------------
    generate_SETTINGS_OUTPUT(settings_data, final_settings_path, python_absolutePath, is_initial_run, AHK_VAR_FINAL_SCRIPT_PATH)
    
    # ------------------------------------------------------------------------------------
    # 12. Final script action: Create (initial run) or Launch (standard run)
    # ------------------------------------------------------------------------------------
    # Le fichier de configuration AHK généré est le SETTINGS_OUTPUT (ex: Includes.ahk)
    final_script_actions(AHK_VAR_FINAL_SCRIPT_PATH, is_initial_run, SETTINGS_OUTPUT) 

    exit_script(0)

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("❌ Erreur: Argument de mode ou de commande manquant.")
        print("Utilisation: main.py build <python_cmd> <ahk_output_file>")
        sys.exit(1)
        
    mode = sys.argv[1].lower()
    
    if mode == "build":
        # Vérifie si le 3ème argument (le nom du fichier AHK de sortie) est présent.
        # Total : 5 arguments (main.py build python_cmd ahk_output_file)
        if len(sys.argv) < 5: # <--- (vérifie 5 arguments nécessaires)
            print("❌ Erreur de lancement (BUILD)")
            print("Utilisation: main.py build <python_cmd> <ahk_path_file> <ahk_include_file>")
            sys.exit(1)

        try:
            main_build()
        # 💡 AJOUTER CE BLOC: Capture toutes les exceptions non gérées dans main_build
        except Exception as e:
            # Imprime la trace complète dans la console pour un diagnostic immédiat
            print(f"\n❌ CRASH NON GÉRÉ DANS main_build:\n{e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            logging.error(f"Crash non géré. Voir la console. Erreur: {e}")
            exit_script(EXIT_CODE_ERROR) # Tentative d'arrêt propre

    elif mode == "parser":
        logging.error(f"Parsed Mode previously removed. Need to work on it.")
        exit_script(EXIT_CODE_ERROR) # Tentative d'arrêt propre
    else:
        print(f"❌ Erreur: Mode non reconnu: {mode}")
        print("Modes disponibles: build, parser")
        sys.exit(1)