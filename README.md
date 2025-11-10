# 🕳️ Deepr

## 🛠️ Prerequisites

To build and run the framework, you need:

* **Python 3.x**
* **AutoHotkey v2.0+**

## 💫 Overview

Deepr is a robust and highly modular scripting framework designed to streamline complex workflows using AutoHotkey v2.0, managed entirely by a foundational Python build script.

The project structure is driven by a single JSON file, ensuring consistency, easy maintenance, and rapid deployment of environment-specific automation logic.

* **Python-Driven Build Process:** The [main.py](\main.py) script automatically generates the entire AHK configuration, including path variables and #include directives, based on the settings.json file.

* **Volume Manager:** Quickly and easily control individual application volumes using the ``NirCmd`` utility (included). 

* **Dynamic Volume Mixer:** Launch, position, and resize the native Windows Volume Mixer (SndVol.exe) window with a single command.

* **Dynamic AHK Structure with JSON:** Generates a complete A_Path class in AHK, providing static and reliable paths to all project resources (Libraries, Functions, Icons, etc.).

* **Context-Aware Scripting:** Automatically groups AHK includes and hotkeys by target application using #HotIf WinActive(...), ensuring your automation logic only runs where it's needed (e.g., specific functions only load when Premiere Pro is active).

* **Modular Architecture:** The [settings.json](.config\settings.json) file defines a clean, hierarchical structure, making it simple to add, organize, and activate new modules or applications without manually editing the AHK include files.

* **Media Production:** Includes comprehensive function stubs and includes for common post-production tasks like [ClipGain.ahk](Library\Modules\Premiere%20Pro\Functions\ClipGain.ahk), [Keyframe.ahk](Library\Modules\Premiere%20Pro\Functions\Keyframe.ahk), [Motion.ahk](Library\Modules\Premiere%20Pro\Functions\Motion.ahk), and [Panel.ahk](Library\Modules\Premiere%20Pro\Functions\Motion.ahk) in Premiere Pro.

## 🚀 First run & after editing

### Setup ``settings.json``
*(Need once, except when you need to make changes )*

If you want to change rootname ("Deepr"), change it inside [settings.json](.config\settings.json) file, and look for [settings.md](.config\settings.md) for more informations. Major modification is made inside the .json file.
Then, rename your root folder too. (I need some implementation here, still in progress)

### Run ``Launcher.ahk``
You just need to start ``Launcher.ahk``.
The entire AHK environment is constructed via the primary Python script.

```autohotkey

class Files {
    static mainPy := "main.py" ; <-- generate/verify "settings.json" structure
    static outputIncludes := ".includes.ahk" ; <-- generated ahk file for include 
}

; You don't need to touch theses.
; If one of thoses return false = Fatal Error
Launcher.Check.IsAdmin
Launcher.Check.Python(&pythonCmd)
Launcher.Check.mainPy(A_ScriptDir, Files.mainPy)
Launcher.Build(pythonCmd, Files.mainPy, Files.outputIncludes)
ExitApp
```

