# Deepr AHK Framework

Welcome to Deepr, a lightweight, file-based framework designed to manage and organize complex AutoHotkey (AHK) v2 scripts. It uses a Python build script to parse a central `settings.json` file, dynamically generating your script's structure, include files, and context-sensitive hotkeys.

This framework is ideal for users who want to separate their hotkeys by application (e.g., global hotkeys, Photoshop-specific, Premiere Pro-specific) without managing complex `#Include` directives and window-group logic manually.

## 🛠️ Prerequisites

To build and run the framework, you need:

* **Python 3.x**
* **AutoHotkey v2.0+**

## ⚙️ Core Features

* **Python Build System**: A single `main.py` script builds your entire AHK environment.
* **Centralized Configuration**: `settings.json` acts as the single source of truth for your project's folder structure, file includes, and hotkey contexts.
* **Dynamic Path Class**: Automatically generates an `A_Path` class in AHK, giving you easy, intellisense-friendly access to all your project folders (e.g., `A_Path.Core`, `A_Path.Modules.PremierePro`).
* **Context-Aware Hotkeys**: Automatically wraps modules in `#HotIf WinActive(...)` blocks based on your configuration, so hotkeys for a specific app only work when that app is active.
* **Modular by Design**: Easily add or disable new applications, scripts, or libraries just by updating `settings.json`.
* **Smart Folder Detection**: If you add new folders to your project that aren't defined in `settings.json`, the build script will detect them and ask if you want to move their contents into your managed structure.

## ⚡ Not interested in the full framework? Use the modules independently!

While Deepr is designed as an integrated system, many of its components are modular and can be easily adapted for your own AutoHotkey projects with minimal modification.

### Standalone Python Utilities

Located in `SupportFiles/Pythons/`, you can find useful helper scripts:

* **`Backup_Maker.py`**: A simple but powerful Python utility. It reads a list of file and folder paths from `.config/Backup.txt` and copies them into a new `Backup` folder at a location you specify. This is perfect for quickly backing up your important configurations or project files.

* **`Template_Maker.py`**: A command-line tool to boilerplate new projects. It lets you define a central folder of templates (e.g., for different video projects, coding assignments, etc.). When run, it presents a list of these templates, asks for a new project name, and copies the entire chosen template structure to a new location.

### Standalone AutoHotkey Modules

Most `.ahk` files in the `Library/` directory can be included and used in your own scripts.

**Core Functions (`Library/Core/Functions/`)**
This folder contains the backbone of Deepr's interactivity:

* **`HandleKeyGestures.ahk`**: A robust function for creating complex, multi-action hotkeys (e.g., distinguishing between a simple tap, a double-tap, and a long-press).
* **`WatchApp.ahk`**: A function that can be run on a timer to ensure specific windows are always "kept on top" (e.g., keeping Task Manager visible).
* **`WatchError.ahk`**: A simple watchdog that automatically dismisses error message boxes, preventing them from halting your workflow.
* **`WatchMouse.ahk`**: A utility for reporting which window and control is currently under the mouse cursor, excellent for debugging or creating context-aware tools.

**Window Management (`Library/Modules/Windows/`)**
This module is packed with functions for controlling your desktop environment:

* **`Application.ahk`**: A powerful class for launching, focusing, or minimizing applications. It's particularly useful for handling programs that manage multiple windows or tabs, like File Explorer.
* **`Komorebic.ahk`**: A simple wrapper that allows you to send commands to the [Komorebi tiling window manager](https://github.com/LGUG2Z/komorebi) directly from AHK.
* **`Window.ahk`**: Provides convenient `Window.Move()` and `Window.Resize()` functions, perfect for binding to mouse-based hotkeys.
* **`Volume.ahk`**: Includes functions to control system/application volume via NirCmd and a helper class to toggle and position the Windows Volume Mixer (SndVol.exe).
* **`AlwaysOnTop.ahk`**: A simple toggle function for the active window.

**Adobe Modules (`Library/Modules/Premiere Pro/`)**
This module is highly specific to Adobe Premiere Pro and demonstrates advanced automation:

* **`Panel.ahk`**: A class dedicated to identifying and focusing specific Premiere Pro panels (e.g., "Timeline", "Project", "EffectControls") by sending the correct keyboard shortcuts.
* **`Motion.ahk`**: A class that uses ImageSearch and PixelSearch to find and interact with effect properties (like "Scale" or "Position") directly in the Effect Controls panel.
* **`Paste.ahk`**: A context-aware "smart paste". It detects whether you are pasting a *clip*, a *project item*, or *keyframes* and automatically focuses the correct panel (like Effect Controls) before pasting.
* **`ApplyPreset.ahk`**: A helper function that streamlines the process of dragging and dropping effects or presets onto clips.

## 🚀 Quick Start & Releases

There are two ways to get started with Deepr.

### 1. 📦 Deepr Package (Recommended)
This is the "plug-and-play" option. It includes the core framework and all the modules and functions shown in this repository (e.g., Windows, Premiere Pro, After Effects).

1.  Download the latest "Deepr Package" release.
2.  Extract it to your desired location (e.g., `C:\MyScripts\Deepr`).
3.  Ensure you have **Python 3.x** installed and added to your system's PATH.
4.  Run `Launcher.ahk`.
5.  The first time you run it, a Python console will appear and build the necessary files (`paths.ahk`, `.includes.ahk`, and `Deepr.ahk`).
6.  Once complete, `Deepr.ahk` will be launched. You'll see its icon in your system tray, and your hotkeys will be active.

### 2. 📦 From Scratch

This option is for users who want to build their own configuration from the ground up.

1.  Download the "From Scratch" release.
2.  This package contains only three essential files: `main.py`, `Launcher.ahk`, and `settings.json`.
3.  Before running, you **must** edit the `settings.json` file to define your project. At a minimum, it requires a `RootName` (which will be the name of your main `.ahk` script) and a `structure` array containing at least one item with `"type": "Configuration"` (this tells the script where to store itself).

    **Minimal `settings.json`:**
    ```json
    {
        "RootName": "MyScript",
        "structure": [
            {
                "name": ".config",
                "type": "Configuration",
                "is_include": "true"
            }
        ]
    }
    ```
4.  Run `Launcher.ahk`. The build script will perform the initial setup:
    * It will create the `.config` and `Library` folders.
    * It will move `settings.json` into the `.config` folder.
    * It will generate `paths.ahk` (which tells the launcher where to find `settings.json` from now on).
    * It will generate `.includes.ahk` in the `.config` folder.
    * It will generate `MyScript.ahk` (based on your `RootName`) in the root folder.
5.  You can now start adding your own `.ahk` files into the `Library` folder and updating `settings.json` to organize them.

## 💫 Customization

### Changing Generated File Names

The main generated files are `.includes.ahk`, `.paths.ahk` and `.Deepr.ahk`. If you wish to change thoses :

For `.includes.ahk`:
1.  Open `Launcher.ahk` in an editor.
2.  Find the `Files` class near the top.
3.  Change the value of `static outputIncludes` to your desired name (e.g., `static outputIncludes := "MyGenIncludes.ahk"`).

For `.paths.ahk`:
1.  Open `settings.json` in an editor.
2.  Find the key value `"type":"Configuration"` to find the `"path"` key value.
3.  Change the value of `"path"` to your desired name (e.g., `"path":"MyGenPaths.ahk"`).

For `Deepr.ahk`:
1.  Open `settings.json` in an editor.
2.  Find the key value `"rootName":"Deepr"` near the top.
3.  Change the value of `"rootName"` to your desired name (e.g., `"rootName":"MyScript.ahk"`).

**Note:** If you change the `RootName` in `settings.json` (e.g., from "Deepr" to "MyScript"), the build script will detect this. It will automatically rename `Deepr.ahk` to `MyScript.ahk` and present a message box asking if you want to migrate your custom code from the old file to the new one.

### Adding New Modules (Folders)

To add a new set of hotkeys (e.g., for Photoshop):

1.  Create a new folder, for example: `Library/Modules/Photoshop`.
2.  Add your `.ahk` files (e.g., `Photoshop_Hotkeys.ahk`) inside this new folder.
3.  Open `settings.json` and add a new object to the "Modules" `children` array:

    ```json
    {
        "name": "Photoshop",
        "type": "Photoshop",
        "Active": "ahk_class Photoshop",
        "is_include": "true"
    }
    ```
4.  Run `Launcher.ahk`. The build script will automatically find your new files and add them to `.includes.ahk` under the correct `#HotIf WinActive("ahk_class Photoshop")` directive.

For more details on configuration, please see the **[settings.json Documentation](settings.json)**.

### Handling Unknown Folders

If you create a folder in your project directory that is **not** defined in `settings.json`, the build script (`main.py`) will detect it. You will be prompted with a message box asking if you want to move the contents of this unknown folder into one of your existing, managed folders.

