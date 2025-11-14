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
/**
 * @Simple_Press -> Right Click
 * @Double_Press -> Open the right click windows menu and press "{l}" to navigate on "Label".
 *                 be carefull using it, don't work on subtitles tracks.
 * @Hold         -> Move playhead to mouse
 * @On_release   -> If it was "Hold", Focus the panel under mouse
 */
RButton::{
    ActionsExecuted := HandleKeyGestures(PressedHotkey, Open_Label, Playhead_ToMouse, Panel_UnderMouse)
    GUI_Debug.ReturnDebug "{RButton}", "HandleKeyGestures() -> " ActionsExecuted, true
}

/**
 * @Simple_Press -> Middle Click
 * @Hold         -> Press the "hand" tool, and hold Right Click button for navigation on timeline
 * @On_release   -> If it was "Hold", turn back the selection tool.
 */
MButton::{
    ActionsExecuted := HandleKeyGestures(PressedHotkey, , Hold, Tool_Hand, Reset_LButton)
    GUI_Debug.ReturnDebug "{MButton}", "HandleKeyGestures() -> " ActionsExecuted, true
}

F13::{
    ActionsExecuted := HandleKeyGestures(ZoomOut, , , Panel_UnderMouse)
    GUI_Debug.ReturnDebug "{WheelLeft} := #{Left})", "HandleKeyGestures() -> " ActionsExecuted, true
}

F14::{
    ActionsExecuted := HandleKeyGestures(ZoomIn, , , Panel_UnderMouse)
    GUI_Debug.ReturnDebug "{WheelRight} := #{Right})", "HandleKeyGestures() -> " ActionsExecuted, true
}

!F13::{
    ActionsExecuted := HandleKeyGestures(KeyframeSelPrev, , , Panel_EffectControls, Panel_UnderMouse)
    GUI_Debug.ReturnDebug "{Alt} + {WheelLeft} := #{Left})", "HandleKeyGestures() -> " ActionsExecuted, true
}

!F14::{
    ActionsExecuted := HandleKeyGestures(KeyframeSelNext, , , Panel_EffectControls, Panel_UnderMouse)
    GUI_Debug.ReturnDebug "{Alt} + {WheelRight} := #{Left})", "HandleKeyGestures() -> " ActionsExecuted, true
}


^b::MsgBox(Project.Activate())


/*************************************************************************************************************
**************************************************************************************************************
                                                    @KEYBOARD
**************************************************************************************************************
*************************************************************************************************************/

^v::{
    Paste()
    GUI_Debug.ReturnDebug "{CTRL} + {v}", "Paste()", true
}

^Backspace::{
    TrueCtrlBackspace()
    GUI_Debug.ReturnDebug "{CTRL} + {Backspace}", "TrueCtrlBackspace()", true
}

^*::{
    TrueFullscreen("vkDCsc02B")
    GUI_Debug.ReturnDebug "{CTRL} + {VKDC}", "TrueFullscreen() -> 'vkDCsc02B', needed only for non-english keyboards", true
}

F4::{
    HandleKeyGestures(Focus_SearchBox, , , Panel_Effect)
    GUI_Debug.ReturnDebug "{F4}", "HandleKeyGestures() -> Focus 'Effects' then 'Search Box'", true
}

^w::{
    CloseWin()
    GUI_Debug.ReturnDebug "{CTRL} + {w}", "CloseWin()", true
}

z::{
    HandleKeyGestures(, , Hold, PressedHotkey, Tool_Normal, true)
    GUI_Debug.ReturnDebug "{z}", "HandleKeyGestures() -> Tool 'Cutter' when hold, default tool on release", true
}
r::{
    HandleKeyGestures(, , Hold, PressedHotkey, Tool_Normal, true)
    GUI_Debug.ReturnDebug "{r}", "HandleKeyGestures() -> Tool 'Select Forward' when hold, default tool on release", true
}
f::{
    HandleKeyGestures(, , Hold, PressedHotkey, Tool_Normal, true)
    GUI_Debug.ReturnDebug "{f}", "HandleKeyGestures() -> Tool 'Slip' when hold, default tool on release", true
}
g::{
    HandleKeyGestures(, , Hold, PressedHotkey, Tool_Normal, true)
    GUI_Debug.ReturnDebug "{g}", "HandleKeyGestures() -> Tool 'Slide' when hold, default tool on release", true
}
b::{
    HandleKeyGestures(, , Hold, PressedHotkey, Tool_Normal, true)
    GUI_Debug.ReturnDebug "{b}", "HandleKeyGestures() -> Tool 'Speed' when hold, default tool on release", true
}

!s::{
    Motion.HotValue("PrUI_", "DarkestHC_", "Scale", ".png")
    GUI_Debug.ReturnDebug "{ALT} + {s}", 'Motion.HotValue() -> Imagesearch for "Scale" property', true
}
!r::{
    Motion.HotValue("PrUI_", "DarkestHC_", "Rotation", ".png")
    GUI_Debug.ReturnDebug "{ALT} + {r}", 'Motion.HotValue() -> Imagesearch for "Rotation" property', true
}

^+r::{
    HandleKeyGestures(Show_Rulers, , , Panel_Player, Panel_Timeline)
    GUI_Debug.ReturnDebug "{CTRL} + {SHIFT} + {R}", 'HandleKeyGestures() -> Show Rulers + Margins', true
}

²::{
    HandleKeyGestures(Player_Fit, , , Panel_EffectControls, Panel_UnderMouse, )
    GUI_Debug.ReturnDebug "{²}", 'HandleKeyGestures() -> Restore Monitor to fit', true
}
!²::{
    ClipClear()
    GUI_Debug.ReturnDebug "{ALT} + {?}", "ClipClear()", true
}



;+PgUp::ClipGain(+2.5)
;+PgDn::ClipGain(-2.5)

NumpadLeft::{
    Mouse.Move.Pixel(-10)
    GUI_Debug.ReturnDebug "{NumpadLeft}", "Mouse.Move() -> 10px left", true
}

NumpadRight::{
    Mouse.Move.Pixel(+10)
    GUI_Debug.ReturnDebug "{NumpadRight}", "Mouse.Move() -> 10px right", true
}

NumpadUp::{
    Mouse.Move.Pixel( , -10)
    GUI_Debug.ReturnDebug "{NumpadUp}", "Mouse.Move() -> 10px down", true
}

NumpadDown::{
    Mouse.Move.Pixel( , +10)
    GUI_Debug.ReturnDebug "{NumpadDown}", "Mouse.Move() -> 10px up", true
}

^space::{
    SendInput KS_Premiere.SelectPanel.Effects
    Sleep(200)
    SendInput KS_Premiere.SearchBox
    GUI_Debug.ReturnDebug "{Ctrl} + {Space}", "Focus 'Effects' then 'Search Box'", true
}

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
    Effects.Search("#MO")
    GUI_Debug.ReturnDebug "{PadKey1} => {Browser_Home}", "Effects.Search() => '#MO'", true
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
    GUI_Debug.ReturnDebug "{PadKey13} => {F21}","Keyframe.Perform() => " Keyframe.Perform("Select", "Prev") , true
}

;@_PadKey14
F22::{
    GUI_Debug.ReturnDebug "{PadKey13} => {F21}","Keyframe.Perform() => " Keyframe.Perform("Select", "Next") , true
}

;@_PadKey15
F23::{
    GUI_Debug.ReturnDebug "{PadKey13} => {F21}","Keyframe.Perform() => " Keyframe.Perform("Move", "Video", "-1") , true
}

;@_PadKey16
F24::{
    GUI_Debug.ReturnDebug "{PadKey13} => {F21}","Keyframe.Perform() => " Keyframe.Perform("Move", "Video", "+1") , true
}

            /*************************************************************************************
                                                @KEYPAD_SMALLWHEEL1
            *************************************************************************************/

Media_Prev::{
    SendInput(KS_Premiere.Clip.VolumeDown)
    GUI_Debug.ReturnDebug "MACROPAD / {Media_Prev}", "SendInput(KS_Premiere.Clip.VolumeDown)", true
}

Media_Play_Pause::{
    Send("{Media_Play_Pause}")
    GUI_Debug.ReturnDebug "{PadSmallWheel1 Left} => {Media_Play_Pause}", "SendInput() => {Media_Play_Pause}", true
}

Media_Next::{
    SendInput(KS_Premiere.Clip.VolumeUp)
    GUI_Debug.ReturnDebug "MACROPAD / {Media_Next}", "SendInput(KS_Premiere.Clip.VolumeUp)", true
}

            /*************************************************************************************
                                                @KEYPAD_SMALLWHEEL2
            *************************************************************************************/
Volume_Down::{
    SendInput(KS_Premiere.Keyframe.Prev)
    GUI_Debug.ReturnDebug "MACROPAD / {Volume_Down}", "SendInput(KS_Premiere.Keyframe.Prev)", true
}
^Volume_Down::{
    SendInput(KS_Premiere.Keyframe.MorePrev)
    GUI_Debug.ReturnDebug "MACROPAD / {CTRL} + {Volume_Down}", "SendInput(KS_Premiere.Keyframe.MorePrev)", true
}
Volume_Up::{
    SendInput(KS_Premiere.Keyframe.Next)
    GUI_Debug.ReturnDebug "MACROPAD / {Volume_Up}", "SendInput(KS_Premiere.Keyframe.Next)", true
}
^Volume_Up::{
    SendInput(KS_Premiere.Keyframe.MoreNext)
    GUI_Debug.ReturnDebug "MACROPAD / {CTRL} + {Volume_Up}", "SendInput(KS_Premiere.Keyframe.MoreNext)", true
}
Volume_Mute::{
    SendInput("{s}")
    GUI_Debug.ReturnDebug "MACROPAD / {Volume_Mute}", "Split Clip", true
}

            /*************************************************************************************
                                                    @BIGWHEEL
            *************************************************************************************/

Browser_Back::{
    HandleKeyGestures(KeyframeSelPrev, , , Panel_EffectControls, Panel_UnderMouse)
    GUI_Debug.ReturnDebug "MACROPAD / {Browser_Back}", "HandleKeyGestures(KeyframeSelPrev, , , Panel_EffectControls, Panel_UnderMouse)", true
}

Browser_Forward::{
    HandleKeyGestures(KeyframeSelNext, , , Panel_EffectControls, Panel_UnderMouse)
    GUI_Debug.ReturnDebug "MACROPAD / {Browser_Forward}", "HandleKeyGestures(KeyframeSelNext, , , Panel_EffectControls, Panel_UnderMouse)", true
}






/***********************************************************************************
                                                  @FUNCTIONS
***********************************************************************************/

    Hold := [(Actions) => Sleep(10)]
    PressedHotkey := [(Actions) => SendInput("{" ThisHotkey := CleanHotkey() "}")]

    Panel_UnderMouse := [(Actions) => (Mouse.FocusActive())]
    Panel_Timeline := [(Actions) => SendInput(KS_Premiere.SelectPanel.Timeline)]
    Panel_EffectControls := [(Actions) => SendInput(KS_Premiere.SelectPanel.EffectControls)]
    Panel_Effect := [(Actions) => SendInput(KS_Premiere.SelectPanel.Effects)]
    Panel_Player := [(Actions) => SendInput(KS_Premiere.SelectPanel.Player)]

    Playhead_ToMouse := [(Actions) => SendInput(KS_Premiere.PlayheadToMouse)]

    ZoomComp := [(Actions) => SendInput(KS_Premiere.Timeline.ZoomComp)]
    ZoomOut := [(Actions) => SendInput(KS_Premiere.Timeline.ZoomOut)]
    ZoomIn := [(Actions) => SendInput(KS_Premiere.Timeline.ZoomIn)]
    ZoomFrame := [(Actions) => SendInput(KS_Premiere.Timeline.ZoomComp)]

    Player_Fit := [(Actions) => (
              SendInput(KS_Premiere.Player.Fit)
              Sleep(12)
              SendInput(KS_Premiere.Player.Fit100)
              Sleep(12)
              SendInput(KS_Premiere.Player.Fit)
          )
    ]
    Player_ZoomIn := [(Actions) => SendInput(KS_Premiere.Player.ZoomIn)]
    Player_ZoomOut := [(Actions) => SendInput(KS_Premiere.Player.ZoomOut)]

    KeyframeSelPrev := [(Actions) => SendInput(KS_Premiere.Keyframe.SelPrev)]
    KeyframeSelNext := [(Actions) => SendInput(KS_Premiere.Keyframe.SelNext)]
    KeyframePrev := [(Actions) => SendInput(KS_Premiere.Keyframe.Prev)]
    KeyframeNext := [(Actions) => SendInput(KS_Premiere.Keyframe.Next)]
    KeyframeMorePrev := [(Actions) => SendInput(KS_Premiere.Keyframe.MorePrev)]
    KeyframeMoreNext := [(Actions) => SendInput(KS_Premiere.Keyframe.MoreNext)]

    Show_Rulers :=
          (Actions) => (
              SendInput(KS_Premiere.Player.ShowMargins)
              Sleep(15)
              SendInput(KS_Premiere.Player.ShowRulers)
              Sleep(15)
              SendInput(KS_Premiere.Player.ShowGuides)
          )

    Open_Label := [ 
          (Actions) => (
              BlockInput("On") 
              SendInput("{RButton}")
              Sleep(65)
              SendInput("{l}")
              BlockInput("Off")
          )
    ]

    Focus_SearchBox := [ 
          (Actions) => (
              Sleep(150)
              SendInput(KS_Premiere.SearchBox)
          )
    ]

    Tool_Hand := [
          (Actions) => (
              SendInput(KS_Premiere.Tool.Hand)
              SendInput("{LButton down}")
          )
    ] 

    Tool_Razor := [(Actions) => (SendInput(KS_Premiere.Tool.Razor))]
    Tool_Normal := [(Actions) => (SendInput(KS_Premiere.Tool.Normal))]
    Tool_Slip := [(Actions) => (SendInput(KS_Premiere.Tool.Slip))]
    Tool_Slide := [(Actions) => (SendInput(KS_Premiere.Tool.Slide))]

    Reset_LButton := [
          (Actions) => (
              SendInput("{LButton up}")
              SendInput(KS_Premiere.Tool.Normal)
          )
    ]

    MarkersPrevious := [(Actions) => (SendInput(KS_Premiere.Markers.Previous))]
    MarkersNext := [(Actions) => (SendInput(KS_Premiere.Markers.Next))]
    MarkersYellow := [(Actions) => (SendInput(KS_Premiere.Markers.Add.Yellow))]





;If Toggle.Capslock() {
;    
;    ^NumpadAdd::{
;        ValueEdit("+5")
;        GUI_Debug.ReturnDebug "{CTRL} + {NumpadAdd}", "ValueEdit('+5')", true
;    }
;    ^NumpadSub::{
;        ValueEdit("-5")
;        GUI_Debug.ReturnDebug "{CTRL} + {NumpadSub}", "ValueEdit('-5')", true
;    }
;    NumpadAdd::{
;        ValueEdit("+10")
;        GUI_Debug.ReturnDebug "{NumpadAdd}", "ValueEdit('+10')", true
;    }
;    NumpadSub::{
;        ValueEdit("-10")
;        GUI_Debug.ReturnDebug "{NumpadSub}", "ValueEdit('-10')", true
;    }
;}


;+q::HandleKeyGestures(KeyframeMorePrev, , KeyframeMorePrev, , )
;+d::HandleKeyGestures(KeyframeMoreNext, , KeyframeMoreNext, , )