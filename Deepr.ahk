/***********************************************************************************
 * 
 * @description A fully modulable ahk script with per application hotkeys layering.
 * @author Ephraem
 * @date 2021/05/10
 * @version 6.0 BETA (Trying with Python integration)
 * 
/**********************************************************************************/
/***********************************************************************************
                                        @Notes
* 
-- FOR THE CORE
Need to finish "CustomDevice.ini", "Hotkeys.ahk" inside "Z:\Files\parsertest"
Need to do a Milanote work and make layout for Premiere MacroPad
Need to work on class file generated inside start_deepr, see "Test_Class" function.
Need more accurate Return result for GUI_Debug
Need search about "Hotkeys" dynamic functions
Need to do a script that will copy/paste all hotkeys script for github, with "Blank"
Need "Keyboard Display GUI" to show a keyboard with assigned key with color, text.. Adapt for macro pad (VERY BIG WORK HERE) 

-- FOR "Premiere_Hotkeys"
Need to do a "Double Value Copy/Paste" func for pasting double values (ex: Motion/Position -> "960", "540")

*
***********************************************************************************/

/***********************************************************************************
                                        @Init
***********************************************************************************/

#include "%A_ScriptDir%\.includes.ahk"

    full_command_line := DllCall("GetCommandLine", "str")

    if not (A_IsAdmin or RegExMatch(full_command_line, " /restart(?!\S)")) {
        try {
            if A_IsCompiled 
                Run '*RunAs "' A_ScriptFullPath '" /restart'
            else
                Run '*RunAs "' A_AhkPath '" /restart "' A_ScriptFullPath '"'
        } ExitApp
    }

    TraySetIcon(A_Path.Icons "\deepr_Icon.png")

    if (PID := !ProcessExist("komorebi.exe"))
        Komorebic("start", &Result)
    
    #ESC::Run '*RunAs "' A_ScriptDir "\Launcher.ahk" '" /restart "' 

/***********************************************************************************
                                    @SetTimers
***********************************************************************************/

    global MsgboxTitle := "Deepr"
    global Err := MsgboxTitle " Error"

    g_AppsToPin := [
    "ahk_class ApplicationFrameWindow",
    "ahk_class CabinetWClass",
    Application_Class.MediaEncoder.winTitle
    ]

    g_childAppsToPin := [
        "Keyboard Shortcuts",
        "Track Fx Editor - ",
        "Clip Fx Editor - "
    ]
    
    SetTimer(WatchTooltip, 300)
    SetTimer(WatchError, 300)
    SetTimer((*) => WatchApp(g_AppsToPin, ), 300)
    SetTimer((*) => WatchChildApp(Application_Class.PremierePro.winTitle, g_childAppsToPin), 300)

   

;SetTimer((*) => RandomFunctions() , 1000)

/***********************************************************************************
                                        @GUI
***********************************************************************************/

    GUI_Debug.Init()
    SetTimer((*) => GUI_Debug.Update() , 100) ; Check every 100 ms
    GUI_SideNote.Init()



