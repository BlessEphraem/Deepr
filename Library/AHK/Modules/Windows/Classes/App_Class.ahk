#Requires AutoHotkey v2.0


class Application_Class {

    static WinStart := {
        fullName: "Start",
        winTitle: "ahk_class Windows.UI.Core.CoreWindow"
    }

    static OneCommander := {
        winTitle: "ahk_exe OneCommander.exe",
        path: "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\OneCommander\OneCommander.lnk"
    }


    static PremierePro := {
        winTitle: "ahk_exe Adobe Premiere Pro.exe",
        winClass: "ahk_class Premiere Pro",
        path: "C:\Program Files\Adobe\Adobe Premiere Pro 2025\Adobe Premiere Pro.exe"
    }

    static PremierePro_BETA := {
        winTitle: "ahk_exe Adobe Premiere Pro (Beta).exe",
        path: "C:\Program Files\Adobe\Adobe Premiere Pro (Beta)\Adobe Premiere Pro (Beta).exe"
    }

    static Resolve := {
        winTitle: "ahk_exe Resolve.exe",
        path: "C:\Program Files\Blackmagic Design\DaVinci Resolve\Resolve.exe"
    }

    static AfterFX := {
        winTitle: "ahk_exe AfterFX.exe",
        path: "C:\Program Files\Adobe\Adobe After Effects 2025\Support Files\AfterFX.exe"
    }

    static Illustrator := {
        winTitle: "ahk_exe Illustrator.exe",
        winClass: "ahk_class illustrator",
        path: "C:\Program Files\Adobe\Adobe Illustrator 2025\Support Files\Contents\Windows\Illustrator.exe"
    }

    static MediaEncoder := {
        winTitle: "ahk_class Adobe Media Encoder 2025",
        path: "C:\Program Files\Adobe\Adobe Media Encoder 2025\Adobe Media Encoder.exe"
    }

    static Audition := {
        winTitle: "ahk_exe Adobe Audition.exe",
        path: "C:\Program Files\Adobe\Adobe Audition 2025\Adobe Audition.exe"
    }

    static Photoshop := {
        winTitle: "ahk_class Photoshop",
        path: "C:\Program Files\Adobe\Adobe Photoshop 2025\Photoshop.exe"
    }

    static Explorer := {
        winTitle: "ahk_exe explorer.exe",
        winClass: "ahk_class CabinetWClass",
        path: "C:\Users\Default\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\File Explorer"
    }

    static Arc := {
        fullName: "Arc",
        winTitle: "ahk_exe Arc.exe",
        path: "C:\Users\Default\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Arc.exe"
    }

    static Edge := {
        fullName: "Microsoft Edge",
        winTitle: "ahk_exe msedge.exe",
        path: "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    }

    static Blender := {
        winTitle: "ahk_exe blender.exe",
        path: "C:\Program Files\Blender Foundation\Blender 4.3\blender.exe"
    }

    static Code := {
        winTitle: "ahk_exe Code.exe",
        path: "C:\Users\Ephraem\AppData\Local\Programs\Microsoft VS Code\Code.exe"
    }

    static Voicemeeter := {
        winTitle: "ahk_exe voicemeeter8x64.exe",
        path: "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\VB Audio\VoiceMeeter\Voicemeeter Potato x64"
    }

    static Discord := {
        fullName: "Discord",
        winTitle: "ahk_exe Discord.exe",
        path: "C:\Users\Ephraem\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Discord Inc\Discord"
    }

    static Obsidian := {
        winTitle: "ahk_exe Obsidian.exe",
        path: "C:\Users\Ephraem\AppData\Local\Programs\obsidian\Obsidian.exe"
    }

    static Notion := {
        winTitle: "ahk_exe Notion.exe",
        path: "C:\Users\Ephraem\AppData\Local\Programs\Notion\Notion.exe"
    }

    static FlowLauncher := {
        winTitle: "Flow.Launcher.exe",
        path: "C:\Users\Ephraem\AppData\Local\FlowLauncher\Flow.Launcher.exe"
    }

}
