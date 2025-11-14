#!/usr/bin/env python3

"""
Template_Maker.py

A simple command-line utility to copy template directories.

This script manages a central template source directory. It lists all
subdirectories within that source as selectable templates. The user can
then choose a template, provide a new name, and select a destination,
and the script will copy the entire template structure to the new location.

The template source directory path is stored in a config file located
in the user's platform-specific application data directory.
"""

import os
import sys
import shutil
import configparser
from typing import Optional, Tuple

# --- Constants ---

def get_config_path() -> str:
    """
    Gets the platform-specific config file path.
    Ensures the directory exists.
    """
    APP_NAME = "TemplateMaker"
    CONFIG_NAME = "templates.ini"
    
    try:
        if sys.platform == "win32":
            # Windows (e.g., C:\Users\<User>\AppData\Roaming\TemplateMaker)
            base_dir = os.getenv('APPDATA')
            if not base_dir:
                raise OSError("APPDATA environment variable not set.")
            config_dir = os.path.join(base_dir, APP_NAME)
        elif sys.platform == "darwin":
            # macOS (e.g., /Users/<User>/Library/Application Support/TemplateMaker)
            config_dir = os.path.join(os.path.expanduser('~/Library/Application Support'), APP_NAME)
        else:
            # Linux (e.g., /home/<User>/.config/TemplateMaker)
            config_dir = os.path.join(
                os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config')), APP_NAME
            )
        
        # Ensure the directory exists before trying to read/write the file
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, CONFIG_NAME)

    except (OSError, TypeError) as e:
        # Fallback to current directory if we can't create the config dir
        print(f"[WARNING] Could not create or access platform config directory: {e}")
        print(f"Falling back to local file: ./{CONFIG_NAME}")
        return CONFIG_NAME # Return the original local file name

# This function call replaces the original static string
CONFIG_FILE = get_config_path() 
CONFIG_SECTION = "Settings"
CONFIG_KEY = "Directory"


def handle_config_error() -> bool:
    """
    Handles a missing or corrupt config file.
    Asks the user if they want to continue (and create a new file) or abort.
    """
    print(f"\n[WARNING] Config file '{CONFIG_FILE}' not found or is corrupt.")
    while True:
        choice = input("Continue (will create/overwrite) or Abort? (y/n): ").strip().lower()
        if choice == 'n':
            print("Aborting.")
            return False
        if choice == 'y':
            print("Continuing. A new config file will be created if needed.")
            return True
        print("Invalid choice. Please enter 'c' or 'a'.")


def prompt_for_new_source_dir(message: str) -> str:
    """
    Prompts the user to enter a valid directory path until one is given.
    """
    print(f"\n{message}")
    while True:
        path = input("Enter path to your templates directory: ").strip()
        if os.path.isdir(path):
            return path
        else:
            print(f"Error: '{path}' is not a valid directory. Please try again.")


def get_template_source_dir() -> Optional[str]:
    """
    Loads the template source directory from the config file.
    Handles all error cases:
    1. File not found -> Asks to create.
    2. File corrupt -> Asks to overwrite.
    3. Key missing in file -> Asks to set.
    4. Path in file is invalid -> Asks to update.
    """
    config = configparser.ConfigParser()
    source_dir = None
    needs_save = False

    try:
        if not os.path.exists(CONFIG_FILE):
            if not handle_config_error():
                return None  # User aborted
            needs_save = True
        else:
            config.read(CONFIG_FILE)
            if config.has_option(CONFIG_SECTION, CONFIG_KEY):
                source_dir = config.get(CONFIG_SECTION, CONFIG_KEY)
            else:
                # File exists, but key is missing
                print(f"[INFO] Config file found, but '{CONFIG_KEY}' is not set.")
                needs_save = True

    except configparser.Error as e:
        print(f"Error reading config file: {e}")
        if not handle_config_error():
            return None  # User aborted
        config = configparser.ConfigParser()  # Reset config object
        needs_save = True

    # --- Validate the path ---

    if not source_dir:
        # Path was never set or config was just created
        message = "Please specify the main directory containing your templates:"
        source_dir = prompt_for_new_source_dir(message)
    
    elif not os.path.isdir(source_dir):
        # Path was set, but is no longer valid
        message = (
            f"The previously saved directory is missing or invalid:\n'{source_dir}'\n"
            "Please enter a new path:"
        )
        source_dir = prompt_for_new_source_dir(message)
        needs_save = True

    # --- Save if necessary ---
    if needs_save:
        try:
            if not config.has_section(CONFIG_SECTION):
                config.add_section(CONFIG_SECTION)
            config.set(CONFIG_SECTION, CONFIG_KEY, source_dir)
            with open(CONFIG_FILE, 'w') as configfile:
                config.write(configfile)
            print(f"Saved template source directory: {source_dir}")
            print(f"Config file location: {CONFIG_FILE}")
        except OSError as e:
            print(f"Error saving config file: {e}")
            return None

    return source_dir


def select_template(source_dir: str) -> Optional[Tuple[str, str]]:
    """
    Lists subdirectories in source_dir and prompts user to select one.
    Returns (path_to_template, template_name) or None.
    """
    try:
        all_entries = os.listdir(source_dir)
        # Filter for directories only
        templates = [d for d in all_entries if os.path.isdir(os.path.join(source_dir, d))]
    except OSError as e:
        print(f"Error reading template directory '{source_dir}': {e}")
        return None

    if not templates:
        print(f"No template directories found in '{source_dir}'.")
        print("Please create subdirectories in this folder to use as templates.")
        return None

    print("\n--- Available Templates ---")
    for i, template_name in enumerate(templates):
        print(f"[ {i + 1} ] - {template_name}")

    while True:
        try:
            choice_str = input("\nSelect a template by number: ")
            choice_int = int(choice_str) - 1  # Convert to 0-based index
            
            if 0 <= choice_int < len(templates):
                selected_name = templates[choice_int]
                selected_path = os.path.join(source_dir, selected_name)
                print(f"Selected: {selected_name}")
                return selected_path, selected_name
            else:
                print(f"Invalid number. Please enter a number between 1 and {len(templates)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def get_destination_path() -> str:
    """
    Asks the user for a destination path.
    Defaults to the current working directory.
    """
    default_path = os.getcwd()
    print(f"\nWhere do you want to generate the template?")
    print(f"(Default: Current directory '{default_path}')")
    
    while True:
        dest_path = input("Enter destination path (or press Enter for default): ").strip()
        
        if not dest_path:
            dest_path = default_path
            print(f"Using default path: {dest_path}")
            return dest_path
        
        if os.path.isdir(dest_path):
            return dest_path
        else:
            print(f"Error: '{dest_path}' is not a valid directory. Please try again.")


def get_new_template_name() -> str:
    """
    Asks the user for the name of the new copied folder.
    """
    print("\nEnter a name for the new project folder:")
    while True:
        new_name = input("New project name: ").strip()
        if new_name:
            # You could add more validation here (e.g., check for invalid chars)
            return new_name
        else:
            print("Name cannot be empty. Please enter a name.")


def copy_template(source_template_path: str, destination_dir: str, new_name: str) -> None:
    """
    Copies the selected template directory to the destination with the new name.
    Uses shutil.copytree to copy all contents.
    """
    final_destination_path = os.path.join(destination_dir, new_name)

    # --- CRITICAL: Check if destination already exists ---
    if os.path.exists(final_destination_path):
        print(f"\n[ERROR] A file or directory named '{new_name}' already exists at:")
        print(f"'{destination_dir}'")
        print("Aborting to prevent overwriting.")
        return

    try:
        print(f"\nCopying template from '{source_template_path}'...")
        print(f"To: '{final_destination_path}'")
        
        # This is the function that copies the entire directory tree
        shutil.copytree(source_template_path, final_destination_path)
        
        print("\n✅ Template copied successfully!")

    except OSError as e:
        print(f"\n❌ Error copying template: {e}")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred during copy: {e}")


def main():
    """
    Main function to orchestrate the script flow.
    """
    print("--- Template Generator ---")
    
    # 1. Get and validate the template source directory
    source_dir = get_template_source_dir()
    if not source_dir:
        return  # User aborted or critical error

    # 2. List and select a template
    selection = select_template(source_dir)
    if not selection:
        return  # No templates found or user error
    
    source_template_path, template_name = selection

    # 3. Get destination path
    dest_dir = get_destination_path()

    # 4. Get new project name
    new_name = get_new_template_name()

    # 5. Perform the copy
    copy_template(source_template_path, dest_dir, new_name)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user. Exiting.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FATAL ERROR] An unexpected error occurred: {e}")
        sys.exit(1)
    finally:
        # This keeps the window open when double-clicked on Windows
        print("\n--------------------------")
        input("Press Enter to exit.")