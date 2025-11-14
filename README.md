# Deepr AHK Framework

Deepr is a modular and dynamic framework designed to help you organize, manage, and build complex [AutoHotkey v2](https://www.autohotkey.com/) scripts. It takes the guesswork out of structuring your project by using a simple `settings.json` file as the single source of truth, automatically generating the necessary `#include` directives and a convenient `A_Path` class to access your project files.

Whether you want a fully managed framework for all your scripts or just want to browse a collection of useful, standalone AHK and Python modules, Deepr has you covered.

## 🛠️ Prerequisites

* **AutoHotkey v2.0+**: Download it from [autohotkey.com](https://www.autohotkey.com/).
* **Python 3.x**: Download it from [python.org](https://www.python.org/).
    * **Important:** During installation, make sure to check the box that says **"Add Python to PATH"**.

---

## ⚡ Core Features

* **Dynamic Project Structure:** No more manual `#include` management! Deepr's Python-based build script reads your `settings.json` and automatically generates the include files.
* **Smart Folder Detection:** Simply add a new folder to your `Library`, and the next time you run the launcher, Deepr will detect it and ask if you want to automatically add it to your `settings.json`.
* **Context-Aware Hotkeys:** Automatically wrap hotkeys in `#HotIf WinActive(...)` directives based on your settings, so your Premiere Pro shortcuts don't interfere with VS Code, and vice-versa.
* **Centralized Path Management:** Generates an `A_Path` class in AHK, giving you clean, intellisense-friendly access to all your project folders (e.g., `A_Path.Modules.PremierePro`).
* **Modular Library:** The entire framework is built around a `Library` folder, making it easy to grab individual modules (like `HandleKeyGestures`, `Application`, or `Window`) for use in your own projects.
* **Helpful Utilities:** Includes standalone Python scripts for common tasks, like `Backup_Maker.py` to back up your project files.

## 🚀 Just Need a Specific Tool? (Standalone Modules)

You don't have to use the whole framework! Most components in the `Library` are designed to be portable. Feel free to browse the repository and download anything you find useful.

**Notable Standalone Modules:**

* **AHK Modules (`Library/AHK`):**
    * **`HandleKeyGestures.ahk`**: A powerful function to create hotkeys that react differently to a **Tap**, **Double-Tap**, or **Hold**.
    * **`Application.ahk`**: An advanced class for launching, focusing, or minimizing applications, with special handling for File Explorer paths and tabs.
    * **`Window.ahk`**: Simple, effective functions to move and resize windows using your mouse.
    * **`Modules/Premiere Pro`**: A suite of tools for Adobe Premiere Pro, including:
        * `Panel.ahk`: Programmatically focus specific panels (e.CSS. `Timeline`, `EffectControls`).
        * `Paste.ahk`: A "smart paste" that detects if you're pasting clips or keyframes and focuses the correct panel automatically.
        * `Motion.ahk`: Uses ImageSearch to find and interact with effect properties like "Scale" and "Position" directly in the Effect Controls panel.
    * **`SideNote.ahk`**: A simple slide-out notepad GUI that docks to the right side of your screen.

* **Python Scripts (`Library/Pythons`):**
    * **`Backup_Maker.py`**: A simple CLI tool that reads a list of files/folders from a text file (`.config/.BackupMaker/Backup.txt`) and copies them (preserving directory structure) to a single `Backup` folder.
    * **`Template_Maker.py`**: A CLI tool to boilerplate new projects. Point it to a folder of templates, and it will ask you which one to copy and what to name the new project folder.

---

## 🚀 Quick Start (Using Framework)

This is the recommended way to use Deepr as a complete framework for your own scripts.

1.  **Download:** Grab the latest realease, it contains only `Launcher.ahk` and `main.py`.
2.  **Place Files:** Put both files into a new, empty folder. This will be your project's root.
3.  **Run:** Double-click `Launcher.ahk`.
    * A console window will appear. Because `settings.json` is missing, the script will ask you to provide a `RootName` for your new project folder (e.g., `MyScripts`).
    * The script will then automatically generate the default folder structure (`Library`, `.config`) and all the necessary configuration files (`settings.json`, `paths.ahk`, `.includes.ahk`).
    * Finally, it will create and launch your main script (e.g., `MyScripts.ahk`).
4.  **Done!** Your framework is ready. You can now start adding your own scripts to the `Library` folder.

## 🧩 How to Use & Add Modules

Deepr's main strength is how it handles new scripts. You don't need to manually edit `settings.json` or `.include.ahk` every time you add a new module.

### Adding a New Module

1.  **Create a Folder:** Create a new folder for your module inside `Library/AHK/Modules/`. For example: `Library/AHK/Modules/Photoshop`.
2.  **Add Scripts:** Place your `.ahk` files inside this new folder (e.g., `Photoshop_Hotkeys.ahk`).
3.  **Run Launcher:** Run `Launcher.ahk` again.
4.  **Auto-Configure:** The build script will detect a new "unknown" folder (`Photoshop`). It will ask you via a console prompt if you want to add this folder to your `settings.json`.
5.  **Confirm:** Press `a` (for Add). The script will automatically update `settings.json` and add the new module to your `.includes.ahk` file.
6.  **Add Context (Optional):**
    * Open `.config/settings.json`.
    * Find the new entry for "Photoshop".
    * Add an `"Active"` key to make all scripts in that folder context-sensitive:

    ```json
    {
        "name": "Photoshop",
        "type": "Photoshop",
        "Active": "ahk_exe Photoshop.exe",  // This makes it context-sensitive
        "is_include": "true",
        "is_path": "true"
    }
    ```

Now, any hotkeys inside `Photoshop_Hotkeys.ahk` will only work when Photoshop is the active window.

## 💫 Customization (`settings.json`)

The `settings.json` file is the heart of your project's configuration. Here are the key properties you can use for each folder entry:

**IMPORTANT:** Do not add new folder entries to this file manually. Instead, create the physical folder in your project and re-run Launcher.ahk. The script will detect it and offer to add it for you. You should only edit this file to modify the properties of existing folders.

* **`"name"`**: (Optional) The name of the folder on your disk. If omitted, the `"type"` value is used as the folder name.
* **`"type"`**: (Required) The name used to generate the variable in the `A_Path` class. For example, a "type" of "MyScripts" becomes accessible via `A_Path.MyScripts`.
* **`"Active"`**: (Optional) The `WinActive` condition for all scripts in this folder and its subfolders.
    * `"ahk_exe MyProgram.exe"`: Scripts only run when `MyProgram.exe` is active.
    * `"Windows"`: Scripts will be global (part of the main script).
    * If omitted, scripts are global.
* **`"is_include"`**: (Optional, defaults to `"true"`)
    * `"true"`: The build script will scan this folder (and its children) for `.ahk` files and `#include` them.
    * `"false"`: The build script will **ignore** this folder and all its children when looking for `.ahk` files.
* **`"is_path"`**: (Optional, defaults to `"true"`)
    * `"true"`: This folder will be added to the `A_Path` class.
    * `"false"`: This folder will be ignored by the `A_Path` class generator.
* **`"children"`**: (Optional) A list of nested folder objects that inherit properties (like `Active`) from their parent.