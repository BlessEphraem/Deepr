## 💫 Overview

Deepr is a robust and highly modular scripting framework designed to streamline complex workflows using AutoHotkey v2.0, managed entirely by a foundational Python build script.

The project structure is driven by a single JSON file, ensuring consistency, easy maintenance, and rapid deployment of environment-specific automation logic.

* **Python-Driven Build Process:** The ``main.py`` script automatically generates the entire AHK configuration, including path variables and #include directives, based on the settings.json file.


* **Dynamic AHK Structure with JSON:** Generates a complete A_Path class in AHK, providing static and reliable paths to all project resources (Libraries, Functions, Icons, etc.).

* **Context-Aware Scripting:** Automatically groups AHK includes and hotkeys by target application using #HotIf WinActive(...), ensuring your automation logic only runs where it's needed (e.g., specific functions only load when Premiere Pro is active).

* **Modular Architecture:** The [settings.json](https://github.com/BlessEphraem/Deepr/blob/main/.config/settings.json) file defines a clean, hierarchical structure, making it simple to add, organize, and activate new modules or applications without manually editing the AHK include files.

* **Media Production:** Includes comprehensive function stubs and includes for common post-production tasks like [ClipGain.ahk](https://github.com/BlessEphraem/Deepr/blob/main/Library/Modules/Premiere%20Pro/Functions/ClipGain.ahk), [Keyframe.ahk](https://github.com/BlessEphraem/Deepr/blob/main/Library/Modules/Premiere%20Pro/Functions/Keyframe.ahk), [Motion.ahk](https://github.com/BlessEphraem/Deepr/blob/main/Library/Modules/Premiere%20Pro/Functions/Motion.ahk), and [Panel.ahk](https://github.com/BlessEphraem/Deepr/blob/main/Library/Modules/Premiere%20Pro/Functions/Panel.ahk) in Premiere Pro.

## 🛠️ Prerequisites

To build and run the framework, you need:

* **Python 3.x**
* **AutoHotkey v2.0+**

## 🚀 Choose your release!

Two types of releases are available for you:
### 1. The Full Package *(Recommended)*
This includes all scripts and a ready-to-use configuration, which I personally use. I recommend starting with this even if you plan to modify it.

### 2. From Scratch
This contains only the essential files required to launch the script with a default configuration.

#### Usage
Using my `Launcher.ahk` file with class included :
```autohotkey
class Files {
    static mainPy := "main.py" ; <-- don't edit
    static outputPath := "paths.ahk"  ; <-- You can edit
    static outputIncludes := ".includes.ahk" ; <-- You can edit
}

; Essential Checks (A Fatal Error occurs if any of these return false)
Launcher.Check.IsAdmin
Launcher.Check.Python(&pythonCmd)
Launcher.Check.mainPy(A_ScriptDir, Files.mainPy)
Launcher.Build(pythonCmd, Files.mainPy, Files.outputPath, Files.outputIncludes)
ExitApp
```
<details>
<summary>View Detailed Explanation</summary>

The `Launcher.Build()` command executes Python with all necessary arguments. For example:

```bash
python main.py build python "path.ahk" "Includes.ahk"
```

**Argument Breakdown**

- `main.py build`: Specifies the script and the execution mode.

- `python`: The calling method for Python (e.g., the command used to execute the interpreter).

- `"path.ahk"`: The name of the AHK file to generate that stores all configuration paths (like the `settings.json` location).

- `"Includes.ahk"`:  The name of the main AHK include file to generate, containing the `A_Path` class and all dynamic `#include` directives.

The script operates in two distinct modes, determined automatically by the presence of the specified paths.ahk file (e.g., `Z:\Deepr\paths.ahk` when launching `Z:\Deepr\main.py`).

*Recommendation: It is best practice to keep your paths.ahk file located in the same directory as the main.py file.*

**1. Initial Run (Project Setup)**
This mode runs when `paths.ahk` **is not found** in the script's launch directory.

The script will :
- Read the local settings.json.
- Create the full directory structure defined in structure.
- Move the root `settings.json` into the folder you defined with `"type": "Configuration"`.
- Generate `path.ahk`: This new file will contain the absolute paths to the new location of settings.json, the Python command, and the main script.
- Generate `Includes.ahk`: This new file will contain the `A_Path` class and all `#includes` found (which will be few, as the project is new).
- Generate `[RootName].ahk`: (e.g., `MyProject.ahk`, based on the `RootName` key). This is the main AHK script for you to edit. It's created with a single `#include "Includes.ahk"` line.

**2. Standard Run (Update & Launch)**
This mode runs when `paths.ahk` **is found** in the script's launch directory.

The script will:
- Read the existing `path.ahk` to find the real settings.json location.
- Verify the directory structure. If any folders from settings.json are missing, it will ask for confirmation before creating them.
- Re-scan the entire project for .ahk files.
- Overwrite `Includes.ahk`: This file is updated with any new .ahk files you've added to the project, correctly sorting them by their Active context.
- Launch `[RootName].ahk`: The script finishes by executing your main AHK script.

</details>



### Important Files

#### `/main.py`
The core Python script for initializing, managing, and running complex AutoHotkey (AHK) v2 projects. Automates directory creation, generates dynamic AHK configuration files, and manages script includes based on a central `settings.json` file.

#### `/Launcher.ahk`
Checks if all prerequisites are met before launching `main.py`. Here you can change the final `outputIncludes` and `outputPath` filenames.
- Can be renamed manually with your explorer.
- Can be edited to change the auto-generated files name.

#### `/settings.json`
Acts as a blueprint used by `main.py` to generate and verify the folder structure and the AHK script found.
**IMPORTANT: YOU CAN'T RENAME IT.**
***or you will need to edit the `main.py` file directly***
- You can **(and should)** edit it to suit your needs.

### Auto-Generated Files

#### `/Deepr.ahk`
The main AHK script for you to edit. Has `#include Includes.ahk` in it.
- You can rename it from `settings.json`
- Created only on a first time run.

#### `/.includes.ahk`
The main generated file. Contains the `A_Path` class and `#include` directives.
- You can rename it from `Launcher.ahk`
- Created/Overwritten on every run.

#### `/.paths.ahk`
Stores important variables location for `main.py`. (paths to `settings.json`, `python.exe`, etc.).
**IMPORTANT: DO NOT MOVE IT FROM THE `main.py` LOCATION.**
***or you will need to edit the `main.py` file directly***
- You can rename it from `Launcher.ahk`
- Created/Overwritten on every run.
