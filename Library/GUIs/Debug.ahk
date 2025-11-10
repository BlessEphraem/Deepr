#Requires AutoHotkey v2.0
#SingleInstance Force

; Array: [Line1 (Hotkey/Trigger), Line2 (Function/Result), Ping (Force GUI update)]
global ReturnDebug := ['', '', false] 


; Original from Taran Van Hemert, big thanks for his AHK 1.0 (https://github.com/TaranVH/2nd-keyboard/blob/master/Taran's_Windows_Mods/KEYSTROKE_VIZ.ahk)
; Adapted for AHK v2.0.
class GUI_Debug
{

    static CurrentState := ['', '', false] ; [Line1, Line2, Ping]

    /**
     * @static
     * Public interface for hotkeys to set the new state.
     * @param Line1 The hotkey/trigger text.
     * @param Line2 The function/result text.
     * @param Ping If true, forces a GUI shift.
     */
    static ReturnDebug(A_Line1, A_Line2, A_Ping := false) {
        ; Met à jour la propriété statique interne
        GUI_Debug.CurrentState := [A_Line1, A_Line2, A_Ping]
    }

    ;
    ; --- STATIC PROPERTIES FOR CONFIGURATION AND CONTROLS ---
    static G_MAIN := unset ; The main GUI (will be initialized in .Init())
    static IsVisible := true
    static ShowInAltTabOnVisible := false

    ; --- GLOBAL HISTORY PROPERTIES (New addition) ---
    ; Used to store the current values and the last-updated values for change detection.
    ; Stocke la dernière valeur lue de ReturnDebug pour la comparaison.
    static HISTORY_STATE_OLD := ['', '', false] 

    ;
    ; Move all configuration constants from the start of the script here
    ; Make them static

    ; --- MONITOR AND LOCATION CONFIGURATION ---
    static MONITOR_INDEX := 2
    static LOCATION := 3

    ;
    ; --- COLORS ---
    static GUI_BG_COLOR := '121212'
    static GUI_TEXT_COLOR_DEFAULT := 'ffffff'
    static HISTORY_COLOR_2 := 'ff0000'
    static HISTORY_COLOR_1 := 'ffe600'
    static HISTORY_COLOR_0 := '00ff62'

   ;
    ; --- DIMENSIONS AND POSITIONING ---
    static MAIN_TEXT_SIZE := 24
    static MAIN_TEXT_WEIGHT := 400
    static DETAIL_TEXT_SIZE := 16
    
    static DETAIL_TEXT_WEIGHT := 200

    static MAIN_TEXT_CONTROL_HEIGHT := GUI_Debug.MAIN_TEXT_SIZE * 2
    static DETAIL_TEXT_CONTROL_HEIGHT := GUI_Debug.DETAIL_TEXT_SIZE * 2
    static DETAIL_TEXT_OFFSET_Y := GUI_Debug.MAIN_TEXT_CONTROL_HEIGHT + 5
    static GUI_LINE_SINGLE_HEIGHT := GUI_Debug.MAIN_TEXT_CONTROL_HEIGHT + GUI_Debug.DETAIL_TEXT_CONTROL_HEIGHT + 10

    static GUI_WIDTH := 1200
    static SCREEN_MARGIN_EDGE := 16
    static GUI_VERTICAL_GAP := 10

    static APPLICATION_NAME := 'KEYSTROKE_VIZ'


    ; Calculate the necessary height for a single history line
    static GUI_HEIGHT := (GUI_Debug.GUI_LINE_SINGLE_HEIGHT * 3) + (GUI_Debug.GUI_VERTICAL_GAP * 2)

    ;
    ; --- TRANSPARENCY ---
    static HISTORY_ALPHA_0 := 225
    static HISTORY_ALPHA_1 := 225
    static HISTORY_ALPHA_2 := 160

    ;
    ; --- CONSOLIDATED FONT PROPERTIES ---
    static MAIN_TEXT_FONT_FAMILY := 'Satoshi Light'
    static MAIN_FONT_PROPS := 'S' GUI_Debug.MAIN_TEXT_SIZE ' W' GUI_Debug.MAIN_TEXT_WEIGHT ' Q5 norm'

    static DETAIL_TEXT_FONT_FAMILY := 'Satoshi Light'
    static DETAIL_FONT_PROPS := 'S' GUI_Debug.DETAIL_TEXT_SIZE ' W' GUI_Debug.DETAIL_TEXT_WEIGHT ' Q5 norm'


    /**
     * @static
     * Initializes and shows the debug GUI.
     */
    static Init() {
        ;
        ; --- MONITOR SELECTION AND COORDINATE CALCULATION (UNCHANGED) ---
        try {
            MonitorGet(GUI_Debug.MONITOR_INDEX + 1, &MonitorLeft, &MonitorTop, &MonitorRight, &MonitorBottom)
        } catch {
            MonitorGet(0, &MonitorLeft, &MonitorTop, &MonitorRight, &MonitorBottom)
        }
    
        if (MonitorRight == '') {
            MaxMonitorIndex :=
            0
            while MonitorGet(MaxMonitorIndex + 1, &temp1)
            MaxMonitorIndex++
            
            UseMonitorIndex := MaxMonitorIndex - 1
            MonitorGet(UseMonitorIndex + 1, &MonitorLeft, &MonitorTop, &MonitorRight, &MonitorBottom)
        }
        else {
            UseMonitorIndex := GUI_Debug.MONITOR_INDEX
        }

        ; SCREEN_WIDTH := MonitorRight - MonitorLeft
        ; SCREEN_HEIGHT := MonitorBottom - MonitorTop
    
        if (GUI_Debug.LOCATION = 1 or GUI_Debug.LOCATION = 3)
            GUI_X := MonitorLeft + GUI_Debug.SCREEN_MARGIN_EDGE
        else
            GUI_X := MonitorRight - GUI_Debug.GUI_WIDTH - GUI_Debug.SCREEN_MARGIN_EDGE
    
        if (GUI_Debug.LOCATION = 1 or GUI_Debug.LOCATION = 2)
            GUI_Y := MonitorTop + GUI_Debug.SCREEN_MARGIN_EDGE
        
        else
            GUI_Y := MonitorBottom - GUI_Debug.GUI_HEIGHT - GUI_Debug.SCREEN_MARGIN_EDGE
    
        ;
        ; --- SINGLE GUI CREATION (UNCHANGED) ---
        static GUI_OPTIONS := '+Owner +AlwaysOnTop -Resize -SysMenu -MinimizeBox -MaximizeBox -Disabled -Caption -Border'

        GUI_Debug.G_MAIN := Gui()
        GUI_Debug.G_MAIN.Opt(GUI_OPTIONS)
        GUI_Debug.G_MAIN.MarginX := 0
        GUI_Debug.G_MAIN.MarginY := 0
        GUI_Debug.G_MAIN.BackColor := GUI_Debug.GUI_BG_COLOR
        GUI_Debug.G_MAIN.Title := GUI_Debug.APPLICATION_NAME
    
        ;
        ; Calculate Y-Coordinates within the single GUI
        LINE2_START_Y := 0
        LINE1_START_Y := LINE2_START_Y + GUI_Debug.GUI_LINE_SINGLE_HEIGHT + GUI_Debug.GUI_VERTICAL_GAP
        LINE0_START_Y := LINE1_START_Y + GUI_Debug.GUI_LINE_SINGLE_HEIGHT + GUI_Debug.GUI_VERTICAL_GAP
    
        ;
        ; --- HISTORY2 (Oldest line - Red/Alpha 2) ---
        GUI_Debug.G_MAIN.SetFont('C' GUI_Debug.HISTORY_COLOR_2 ' ' GUI_Debug.MAIN_FONT_PROPS, GUI_Debug.MAIN_TEXT_FONT_FAMILY)
        GUI_Debug.G_MAIN.AddText('vLine2_Text x0 y' LINE2_START_Y ' w' GUI_Debug.GUI_WIDTH ' h' GUI_Debug.MAIN_TEXT_CONTROL_HEIGHT, ' ') ; Initial empty text
        
        GUI_Debug.G_MAIN.SetFont('C' GUI_Debug.GUI_TEXT_COLOR_DEFAULT ' ' GUI_Debug.DETAIL_FONT_PROPS, GUI_Debug.DETAIL_TEXT_FONT_FAMILY)
        GUI_Debug.G_MAIN.AddText('vLine2_Name x0 y' (LINE2_START_Y + GUI_Debug.DETAIL_TEXT_OFFSET_Y) ' w' GUI_Debug.GUI_WIDTH ' h' GUI_Debug.DETAIL_TEXT_CONTROL_HEIGHT, ' ')
    
    
        ;
        ; --- HISTORY1 (Recent line - Yellow/Alpha 1) ---
        GUI_Debug.G_MAIN.SetFont('C' GUI_Debug.HISTORY_COLOR_1 ' ' GUI_Debug.MAIN_FONT_PROPS, GUI_Debug.MAIN_TEXT_FONT_FAMILY)
        GUI_Debug.G_MAIN.AddText('vLine1_Text x0 y' LINE1_START_Y ' w' GUI_Debug.GUI_WIDTH ' h' GUI_Debug.MAIN_TEXT_CONTROL_HEIGHT, ' ')
        
        GUI_Debug.G_MAIN.SetFont('C' GUI_Debug.GUI_TEXT_COLOR_DEFAULT ' ' GUI_Debug.DETAIL_FONT_PROPS, GUI_Debug.DETAIL_TEXT_FONT_FAMILY)
        GUI_Debug.G_MAIN.AddText('vLine1_Name x0 y' (LINE1_START_Y + GUI_Debug.DETAIL_TEXT_OFFSET_Y) ' w' GUI_Debug.GUI_WIDTH ' h' GUI_Debug.DETAIL_TEXT_CONTROL_HEIGHT, ' ')
    
    
        ;
        ; --- HISTORY0 (Current line - Green/Alpha 0) ---
        GUI_Debug.G_MAIN.SetFont('C' GUI_Debug.HISTORY_COLOR_0 ' ' GUI_Debug.MAIN_FONT_PROPS, GUI_Debug.MAIN_TEXT_FONT_FAMILY)
        GUI_Debug.G_MAIN.AddText('vLine0_Text x0 y' LINE0_START_Y ' w' GUI_Debug.GUI_WIDTH ' h' GUI_Debug.MAIN_TEXT_CONTROL_HEIGHT, ' ')
        
        GUI_Debug.G_MAIN.SetFont('C' GUI_Debug.GUI_TEXT_COLOR_DEFAULT ' ' GUI_Debug.DETAIL_FONT_PROPS, GUI_Debug.DETAIL_TEXT_FONT_FAMILY)
        GUI_Debug.G_MAIN.AddText('vLine0_Name x0 y' (LINE0_START_Y + GUI_Debug.DETAIL_TEXT_OFFSET_Y) ' w' GUI_Debug.GUI_WIDTH ' h' GUI_Debug.DETAIL_TEXT_CONTROL_HEIGHT, ' ')
    
        GUI_Debug.G_MAIN.Show('x' GUI_X ' y' GUI_Y ' w' GUI_Debug.GUI_WIDTH ' h' GUI_Debug.GUI_HEIGHT ' NoActivate' (GUI_Debug.IsVisible ? '' : ' Hide'))

        ; Apply transparency (TransColor for the whole GUI)
        WinSetTransColor(GUI_Debug.GUI_BG_COLOR, GUI_Debug.APPLICATION_NAME)
    }


    /**
     * @static
     * Toggles the visibility of the debug GUI. (UNCHANGED)
     * - Hides the window completely (WinHide).
     * - Manages Alt+Tab visibility using +ToolWindow/+AppWindow based on ShowInAltTabOnVisible.
     * @return {boolean} True if the GUI is now visible, False if hidden.
     */
    static Toggle() {
        ; Checks if the GUI has been initialized
        if (!IsObject(GUI_Debug.G_MAIN)) {
            return
        }

        ; 1. Inverser l'état de visibilité
        GUI_Debug.IsVisible := !GUI_Debug.IsVisible

        if (GUI_Debug.IsVisible) {
            ; --- RENDRE VISIBLE ---

            ; Si ShowInAltTabOnVisible est true, on remet +AppWindow pour qu'elle apparaisse dans Alt+Tab
            if (GUI_Debug.ShowInAltTabOnVisible) {
                GUI_Debug.G_MAIN.Opt('-ToolWindow')
            } else {
                ; Sinon, elle reste +ToolWindow (déjà appliqué dans Init)
                ; On s'assure qu'elle est en mode +ToolWindow
                GUI_Debug.G_MAIN.Opt('+ToolWindow')
            }

            ; Afficher la fenêtre
            WinShow(GUI_Debug.APPLICATION_NAME)
            WinSetTransColor(GUI_Debug.GUI_BG_COLOR, 'ahk_id ' GUI_Debug.G_MAIN.Hwnd)
            return True

        } else {
            ; --- RENDRE INVISIBLE ---

            ; On applique +ToolWindow (caché d'Alt+Tab) si ce n'est pas déjà le cas.
            WinSetTransColor('', 'ahk_id ' GUI_Debug.G_MAIN.Hwnd)
            GUI_Debug.G_MAIN.Opt('+ToolWindow')

            ; Cacher la fenêtre complètement
            WinHide(GUI_Debug.APPLICATION_NAME)
            return False
        }
    }


    /**
     * @static
     * Updates the content of the visualization window. (UNCHANGED - used by hotkeys directly)
     * @param TEXT_LINE2 Content of the second line (The function name/result).
     * @param TEXT_LINE1 Content of the first line (The hotkey/trigger).
     * @param A_ForceShift (Optional) If true, forces an extra shift up.
     */
    static UpdateGui(TEXT_LINE2, TEXT_LINE1, A_ForceShift := false) {
        ; Checks if the GUI has been initialized
        if (!IsObject(GUI_Debug.G_MAIN)) {
            return
        }

        ; --- LOGIQUE DE DÉCALAGE DEMANDÉE PAR LE PING ---
        if (A_ForceShift) {
            ; Shift: HISTORY2 takes the content of HISTORY1 (shift up)
            GUI_Debug.G_MAIN['Line2_Text'].Value := GUI_Debug.G_MAIN['Line1_Text'].Value
            GUI_Debug.G_MAIN['Line2_Name'].Value := GUI_Debug.G_MAIN['Line1_Name'].Value
            
            ; Shift: HISTORY1 takes the content of CURRENT (shift to middle)
            GUI_Debug.G_MAIN['Line1_Text'].Value := GUI_Debug.G_MAIN['Line0_Text'].Value
            GUI_Debug.G_MAIN['Line1_Name'].Value := GUI_Debug.G_MAIN['Line0_Name'].Value
        } else {
            ; 1. HISTORY2 takes the content of HISTORY1 (shift up)
            GUI_Debug.G_MAIN['Line2_Text'].Value := GUI_Debug.G_MAIN['Line1_Text'].Value
            GUI_Debug.G_MAIN['Line2_Name'].Value := GUI_Debug.G_MAIN['Line1_Name'].Value
            
            ; 2. HISTORY1 takes the content of CURRENT (shift to middle)
            GUI_Debug.G_MAIN['Line1_Text'].Value := GUI_Debug.G_MAIN['Line0_Text'].Value
            GUI_Debug.G_MAIN['Line1_Name'].Value := GUI_Debug.G_MAIN['Line0_Name'].Value
        }
        
        ; 3. Update the CURRENT line with new data.
        GUI_Debug.G_MAIN['Line0_Text'].Value := TEXT_LINE2
        GUI_Debug.G_MAIN['Line0_Name'].Value := TEXT_LINE1
    }


    /**
     * @desc
     * **NEW NAME/LOCATION:** Function called by SetTimer to check for changes 
     * in the global 'ReturnDebug' variable and update the GUI if a change is detected.
     */
    static Update() {

        ; Deconstruct the current state
        Current_Line1 := this.CurrentState[1]
        Current_Line2 := this.CurrentState[2]
        Ping_Triggered := this.CurrentState[3]
        
        ; Deconstruct the old state from the static property
        Old_Line1 := GUI_Debug.HISTORY_STATE_OLD[1]
        Old_Line2 := GUI_Debug.HISTORY_STATE_OLD[2]

        ; Check if a PING was triggered OR if the values are different from the last updated values
        ; Note: We only check Line1/Line2 for changes, Ping_Triggered forces a shift regardless of value change.
        if (Ping_Triggered || Current_Line1 != Old_Line1 || Current_Line2 != Old_Line2) {

            ; --- LOGIC DE DÉCALAGE ET DE MISE À JOUR ---

            ; PING / UPDATE NORMAL: HISTORY2 prend le contenu de HISTORY1
            GUI_Debug.G_MAIN['Line2_Text'].Value := GUI_Debug.G_MAIN['Line1_Text'].Value
            GUI_Debug.G_MAIN['Line2_Name'].Value := GUI_Debug.G_MAIN['Line1_Name'].Value

            ; PING / UPDATE NORMAL: HISTORY1 prend le contenu de CURRENT
            GUI_Debug.G_MAIN['Line1_Text'].Value := GUI_Debug.G_MAIN['Line0_Text'].Value
            GUI_Debug.G_MAIN['Line1_Name'].Value := GUI_Debug.G_MAIN['Line0_Name'].Value

            ; 3. Mise à jour de la ligne CURRENT avec les nouvelles données
            GUI_Debug.G_MAIN['Line0_Text'].Value := Current_Line2 ; Function/Result
            GUI_Debug.G_MAIN['Line0_Name'].Value := Current_Line1 ; Hotkey/Trigger

            ; --- MISE À JOUR DE L'HISTORIQUE ET RESET DU PING ---

            ; Mettre à jour l'historique statique
            GUI_Debug.HISTORY_STATE_OLD := [Current_Line1, Current_Line2, false] ; Ping is always reset here

            ; **IMPORTANT** : Réinitialiser la variable globale ReturnDebug (surtout le flag PING)
            ; pour éviter un décalage continu lors du prochain cycle SetTimer
            GUI_Debug.CurrentState := [Current_Line1, Current_Line2, false]
        }
    }
}