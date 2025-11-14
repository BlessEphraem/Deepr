/*************************************************************************************************************
**************************************************************************************************************
                                                @README
**************************************************************************************************************
*************************************************************************************************************/
/**
 * Some windows default hotkey are awfull and useless. Like if you do in this right order :
 * {LWin} + {LAlt} + {LShift} + {LCtrl}, it will open "https://m365.cloud.microsoft/?from=OfficeKey"
 * because microsoft want to reminds you that your computer is not yours. Lol.
 * I tried everything, and you can still have this F*CKING page showing up, so if you want to remove it
 * completly, use Regedit (you should have a warning box when you launch my script, if not then : )
 * 
 * Open CMD as admin and write down :
 * REG ADD HKCU\Software\Classes\ms-officeapp\Shell\Open\Command /t REG_SZ /d rundll32
 * 
 * Not harmfull at all, will only remove THIS microsoft shortcut DEFINITELY. Be sure before doing so.
 * 
 */

/*************************************************************************************************************
**************************************************************************************************************
                                                    @MOUSE
**************************************************************************************************************
*************************************************************************************************************/

Mbutton::{
    Window.Move "MButton"
    GUI_Debug.ReturnDebug "{MButton}", "WindowMover()", true
}

!Mbutton::{
    Window.Resize "MButton"
    GUI_Debug.ReturnDebug "{Alt} + {MButton}", "WindowResizer()", true
}



;@_WheelLeft
F13::{
    Komorebic("cycle-move next", &Result)
    GUI_Debug.ReturnDebug "{WheelLeft} := {F13}", Result, true
}

;@_WheelRight
F14::{
    Komorebic("cycle-move previous", &Result)
    GUI_Debug.ReturnDebug "{WheelRight} := {F14}", Result, true
}


XButton1::{
    SendInput("{Delete}")
    GUI_Debug.ReturnDebug "{XButton1}", "SendInput() => {Delete}", true
}

^XButton1::{
    SendInput("^{Delete}")
    GUI_Debug.ReturnDebug "{Ctrl} + {XButton1}", "SendInput() => ^{Delete}", true
}

+XButton1::{
    SendInput("+{Delete}")
    GUI_Debug.ReturnDebug "{Shift} + {XButton1}", "SendInput() => +{Delete}", true
}



XButton2::{
    SendInput("{Enter}")
    GUI_Debug.ReturnDebug "{XButton2}", "SendInput() => {Enter}", true
}

^XButton2::{
    SendInput("^{Enter}")
    GUI_Debug.ReturnDebug "{Ctrl} + {XButton2}", "SendInput() => ^{Enter}", true
}


+XButton2::{
    SendInput("+{Enter}")
    GUI_Debug.ReturnDebug "{Shift} + {XButton2}", "SendInput() => +{Enter}", true
}

            /*************************************************************************************
                                                    @MXGESTURES
            *************************************************************************************/
/**
 * @NOTES
 * FOR MX MASTER USER :
 * Dunno why, but WheelRight/WheelLeft on MX Master is pretty bad recognized by AHK.,
 * Tried to assign "Launch_App1" and "Launch_App2", doesn't recognize it,
 * But "Launch_Mail" and "Launch_Media" work ?? Wtf logitech ??
 * I don't like it, so I decided to use F13 and F14.
 * If you have some problem with using these, because it open a f*cking office page,
 * go see @README at the top page.
**/

; Move windows across workspaces
;@_MXGestureLeft
+!#Down::{
    Komorebic("cycle-move-to-workspace previous", &Result)
    GUI_Debug.ReturnDebug "{Shift} + {MXGestureLeft} := #+!^{Down}", Result, true
}

;@_MXGestureRight
+!#Up::{
    Komorebic("cycle-move-to-workspace next", &Result)
    GUI_Debug.ReturnDebug "{Shift} + {MXGestureRight} := #+!^{Up}", Result, true
}

;Move windows across monitor
;@_MXGestureLeft
^!#Down::{
    Komorebic("cycle-move-to-monitor previous", &Result)
    GUI_Debug.ReturnDebug "{Ctrl} + {MXGestureLeft} := #+!^{Down}", Result, true
}

;@_MXGestureRight
^!#Up::{
    Komorebic("cycle-move-to-monitor next", &Result)
    GUI_Debug.ReturnDebug "{Ctrl} + {MXGestureRight} := #+!^{Up}", Result, true
}

;Change Workspace
;@_MXGestureLeft
#!Down::{
    Komorebic("focus-monitor 0")
    Sleep(33)
    Komorebic("cycle-workspace previous", &Result)
    GUI_Debug.ReturnDebug "{MXGestureLeft} := #!{Down}", Result, true
}

;@_MXGestureRight
#!Up::{
    Komorebic("focus-monitor 0")
    Sleep(5)
    Komorebic("cycle-workspace next", &Result)
    GUI_Debug.ReturnDebug "{MXGestureRight} := #!{Up}", Result, true
}

;@_MXGesturePress
Appskey::{
    Komorebic("toggle-workspace-layer", &Result)
    GUI_Debug.ReturnDebug "{MXGesturePress} := {AppsKey}", Result, true
}

; eager-focus
; focus the first managed window matching the given exe

/*************************************************************************************************************
**************************************************************************************************************
                                                    @KEYBOARD
**************************************************************************************************************
*************************************************************************************************************/


#(::Application.Window(Application_Class.Notion.winTitle, Application_Class.Notion.path)
#&::Application.Window(Application_Class.Edge.winTitle, Application_Class.Edge.path)
#é::Application.Window(Application_Class.Explorer.winClass, Application_Class.Explorer.path)
#"::Application.Window(Application_Class.Discord.winTitle, Application_Class.Discord.path)
#'::Application.Window(Application_Class.Code.winTitle, Application_Class.Code.path)

;Tab & &::Application.Window(Application_Class.PremierePro.winTitle, Application_Class.PremierePro.path)
;Tab & é::Application.Window(Application_Class.AfterFx.winTitle, Application_Class.AfterFx.path)
;Tab & "::Application.Window(Application_Class.Photoshop.winTitle, Application_Class.Photoshop.path)
;Tab & '::Application.Window(Application_Class.Illustrator.winTitle, Application_Class.Illustrator.path)
;Tab & (::Application.Window(Application_Class.Audition.winTitle, Application_Class.Audition.path)
;Tab & -::Application.Window(Application_Class.MediaEncoder.winTitle, Application_Class.MediaEncoder.path)

;Tab::Tab;Important, if you delete that line, the above hotkeys will over-ride the default "{Tab}" button
;and doing like "{Alt} + {Tab}" will not work anymore.

#space::{
    Language.Switch("fr", "en")
    GUI_Debug.ReturnDebug "{Win} + {Space}", "SwitchLanguage() => Switch between 'fr' and 'en'", true
}

#²::{
    Terminal("Deepr Terminal", "wt.exe", 3, 1200, 600, 300)
    GUI_Debug.ReturnDebug "{Win} + {²}", "Terminal() => Run/Focus Deepr Terminal", true
}

#z::{
    AlwaysOnTop(Sound := true)
    GUI_Debug.ReturnDebug "{Win} + {z}", "AlwaysOnTop()", true
}

#f::{
    Komorebic("toggle-monocle")
    GUI_Debug.ReturnDebug "{Win} + {f}", "Komorebic() => 'toggle-monocle'", true
}

#v::{
    Komorebic("toggle-float")
    GUI_Debug.ReturnDebug "{Win} + {v}", "Komorebic() => 'toggle-float'", true
}

#^r::{
    Komorebic("retile")
    GUI_Debug.ReturnDebug "{Win} + {Ctrl} + {r}", "Komorebic() => 'retile'", true
}


;#b:: {
;resolutions := [[810, 1440], [800, 800], [1400, 1400]]
;
;hwnd := WinActive("A")
;if !hwnd
;return
;
;; Récupère les dimensions actuelles
;WinGetPos(&x, &y, &w, &h, hwnd)
;
;; Trouve l'index de la résolution actuelle ou la plus proche
;idx := 0, minDiff := 1e9
;loop resolutions.Length {
;rw := resolutions[A_Index][1], rh := resolutions[A_Index][2]
;diff := Abs(w - rw) + Abs(h - rh)
;if diff < minDiff
;idx := A_Index, minDiff := diff
;}
;
;; Résolution suivante (boucle circulaire)
;next := Mod(idx, resolutions.Length) + 1
;targetW := resolutions[next][1], targetH := resolutions[next][2]
;
;; Centre la fenêtre
;posX := (A_ScreenWidth - targetW) // 2
;posY := (A_ScreenHeight - targetH) // 2
;
;WinMove(posX, posY, targetW, targetH, hwnd)
;}
;
;#c:: {
;hwnd := WinActive("A")
;if !hwnd
;return
;
;; Récupérer la taille actuelle de la fenêtre
;WinGetPos(&winX, &winY, &winW, &winH, hwnd)
;
;; Taille de l'écran principal
;screenW := A_ScreenWidth
;screenH := A_ScreenHeight
;
;; Calcul des nouvelles positions (centrées)
;posX := (screenW - winW) // 2
;posY := (screenH - winH) // 2
;
;; Appliquer le déplacement sans redimensionnement
;WinMove(posX, posY, , , hwnd)
;}




/*************************************************************************************************************
**************************************************************************************************************
                                                    @KEYPAD
**************************************************************************************************************
*************************************************************************************************************/

/*
[ ][ ][ ][ ]
[ ][ ][ ][ ]
[ ][ ][ ][ ]
[■][■][■][■]
*/

;@_PadKey1
Browser_Home::{
    Application.Window(Application_Class.Explorer.winClass, "Z:\Workspace", false)
    GUI_Debug.ReturnDebug "{PadKey1} => {Browser_Home}", "Application.Window() => 'Z:\Workspace'", true
}

;@_PadKey2
Browser_Favorites::{
    Application.Window(Application_Class.Explorer.winClass, "Z:\Workspace\Productions\Premiere Pro\.Watchfolder", false)
    GUI_Debug.ReturnDebug "{PadKey2} => {Browser_Favorites}", "Application.Window() => 'Z:\Workspace\Productions\Premiere Pro\.Watchfolder'", true
}

;@_PadKey3
Browser_Search::{
    Application.Window(Application_Class.Explorer.winClass, "Z:\Workspace\Productions\Premiere Pro\.Renders", false)
    GUI_Debug.ReturnDebug "{PadKey3} => {Browser_Search}", "Application.Window() => 'Z:\Workspace\Productions\Premiere Pro\.Renders'", true
}

;@_PadKey4
Browser_Refresh::{
    Application.Window(Application_Class.Explorer.winClass, "Z:\Workspace\Productions\Premiere Pro\Sessions", false)
    GUI_Debug.ReturnDebug "{PadKey4} => {Browser_Refresh}", "Application.Window() => 'Z:\Workspace\Productions\Premiere Pro\Sessions'", true
}


/*
[ ][ ][ ][ ]
[ ][ ][ ][ ]
[■][■][■][■]
[ ][ ][ ][ ]
*/

;@_PadKey5
Launch_App1::{
    Application.Window(Application_Class.Explorer.winClass, "Z:\Files", false)
    GUI_Debug.ReturnDebug "{PadKey5} => {Launch_App1}", "Application.Window() => 'Z:\Files'", true
}

;@_PadKey6
Launch_App2::{
    Application.Window(Application_Class.Explorer.winClass, "Z:\Videos", false)
    GUI_Debug.ReturnDebug "{PadKey6} => {Launch_App2}", "Application.Window() => 'Z:\Videos'", true
}

;@_PadKey7
F15::{
    Application.Window(Application_Class.Explorer.winClass, "Z:\Pictures", false)
    GUI_Debug.ReturnDebug "{PadKey7} => {F15}", "Application.Window() => 'Z:\Pictures'", true
}

;@_PadKey8
F16::{
    Application.Window(Application_Class.Explorer.winClass, "Z:\Sounds", false)
    GUI_Debug.ReturnDebug "{PadKey8} => {F16}", "Application.Window() => 'Z:\Sounds'", true
}

/*
[ ][ ][ ][ ]
[■][■][■][■]
[ ][ ][ ][ ]
[ ][ ][ ][ ]
*/

;@_PadKey9
F17::{
    GUI_Debug.ReturnDebug "{PadKey9} => {F17}", "NONE", true
}

;@_PadKey10
F18::{
    GUI_Debug.ReturnDebug "{PadKey10} => {F18}", "NONE", true
}

;@_PadKey11
F19::{
    GUI_Debug.ReturnDebug "{PadKey11} => {F19}", "NONE", true
}

;@_PadKey12
F20::{
    GUI_Debug.ReturnDebug "{PadKey12} => {F20}", "NONE", true
}


/*
[■][■][■][■]
[ ][ ][ ][ ]
[ ][ ][ ][ ]
[ ][ ][ ][ ]
*/

;@_PadKey13
F21::{
    Application.Window(Application_Class.Explorer.winClass, "Z:\Scripts", false)
    GUI_Debug.ReturnDebug "{PadKey13} => {F21}", "Application.Window() => 'Z:\Scripts'", true
}

;@_PadKey14
F22::{
    GUI_Debug.ReturnDebug "{PadKey14} => {F22}", "NONE", true
}

;@_PadKey15
F23::{
    GUI_Debug.ReturnDebug "{PadKey15} => {F23}", "NONE", true
}

;@_PadKey16
F24::{
    IsShow := GUI_Debug.Toggle()
    ; Mise à jour facultative de la GUI de débogage (Debug_Gui)
    if (IsShow) {
    ; Le Toggle a fermé la fenêtre.
        GUI_Debug.ReturnDebug "{PadKey16} => {F24}", "GUI_Debug.Toggle() => Show Debug GUI", true
    } else {
    ; Le Toggle a lancé la fenêtre.
        GUI_Debug.ReturnDebug "{PadKey16} => {F24}", "GUI_Debug.Toggle() => Hide Debug GUI", true
    }
}


            /*************************************************************************************
                                                @KEYPAD_SMALLWHEEL1
            *************************************************************************************/

Media_Prev::{
    Volume.Change("ChangeAppVolume", "msedge.exe", -0.02)
    GUI_Debug.ReturnDebug "{PadSmallWheel1 Left} => {Media_Prev}", "Volume.Change() => Edge -2%", true
}

Media_Play_Pause::{
    
    IsClosed := Volume.SndVol.Toggle(2, 1000, 200, 80, 5)
    Button := "{Media_Play_Pause}"

    ; Mise à jour facultative de la GUI de débogage (Debug_Gui)
    if (IsClosed) {
    ; Le Toggle a fermé la fenêtre.
        GUI_Debug.ReturnDebug "{PadBigWheel2 Pressed} => " Button, "Volume.SndVol.Init() => SndVol Ended", true
    } else {
    ; Le Toggle a lancé la fenêtre.
        GUI_Debug.ReturnDebug "{PadBigWheel2 Pressed} => " Button, "Volume.SndVol.Init() => SndVol Started", true
    }
}

Media_Next::{
    Volume.Change("ChangeAppVolume", "msedge.exe", +0.02)
    GUI_Debug.ReturnDebug "{PadSmallWheel1 Right} => {Media_Next}", "Volume.Change() => Edge +2%", true
}

            /*************************************************************************************
                                                @KEYPAD_SMALLWHEEL2
            *************************************************************************************/

Browser_Back::{
    GUI_Debug.ReturnDebug "{PadSmallWheel2 Left} => {Browser_Back}", "NONE", true
}

Browser_Stop::{
    SendInput("{Browser_Stop}")
    GUI_Debug.ReturnDebug "{PadBigWheel Pressed} => {Browser_Stop}", "SendInput() => {Browser_Stop}", true
}

Browser_Forward::{
    GUI_Debug.ReturnDebug "{PadSmallWheel2 Right} => {Browser_Forward}", "NONE", true
}

            /*************************************************************************************
                                                @KEYPAD_BIGWHEEL
            *************************************************************************************/

Volume_Down::{
    Send("{Volume_Down}")
    GUI_Debug.ReturnDebug "{PadBigWheel Left} => {Volume_Down}", "Volume => Mix Down", true
}

Volume_Mute::{
    Send("{Media_Play_Pause}")
    GUI_Debug.ReturnDebug "{PadSmallWheel1 Pressed} => {Volume_Mute}", "SendInput() => {Media_Play_Pause}", true
}

Volume_Up::{
    Send("{Volume_Up}")
    GUI_Debug.ReturnDebug "{PadBigWheel Right} => {Volume_Up}", "Volume => Mix Up", true
}


;List of most useless key
;1 = used by mouse
;2 = used by macropad
;0 = not used

;   Browser_Back                 |   2
;   Browser_Forward              |   2
;   Browser_Refresh              |   2
;   Browser_Stop                 |   2
;   Browser_Search               |   2
;   Browser_Favorites            |   2
;   Browser_Home                 |   2

;   Volume_Mute                  |   2
;   Volume_Down                  |   2
;   Volume_Up                    |   2

;   Media_Next                   |   2
;   Media_Prev                   |   2
;   Media_Play_Pause             |   2
;   Media_Stop                   |   0

;   Launch_Mail                  |   0
;   Launch_Media                 |   0
;   Launch_App1                  |   0
;   Launch_App2                  |   0

;   Help0    
;   AppsKey                      |   1
;   PrintScreen                  |   0
;   CtrlBreak                    |   0
;   Pause                        |   0

;Very hard to use key (bc it probably doesn't exist on most keyboards.)
;   Sleep