#Requires AutoHotkey v2.0

/**
 * @class Panel
 * Provides static methods for managing focus and retrieving window/control information 
 * for specific panels within Adobe Premiere Pro.
 * NOTE: Relies on external hotkey definitions in KS_Premiere.SelectPanel.
 */
class Panel {
    /**
     * @static
     * Focuses a specified panel in Premiere Pro by sending its corresponding hotkey.
     * Optionally performs a 'Reset' sequence to ensure the key is registered.
     * @param {string} Name - The name of the panel to focus ("Effects", "EffectControls", "Player", "Timeline", "Bin").
     * @param {boolean} [Reset=true] - If true, performs a double-tap on the 'Effects' hotkey first to ensure focus is released/reset.
     * @returns {void}
     */
    static Focus(Name, Reset := true) {
        if Reset {
            ; Send 'Effects' hotkey twice with a short delay to reset the active panel focus.
            SendInput KS_Premiere.SelectPanel.EffectControls
            Sleep(12)
            SendInput KS_Premiere.SelectPanel.EffectControls
            Sleep(5)
        }
        ; If the target is 'Effects', the reset sequence already focused it, so return.
        if Name = "EffectControls"
            return
        ; Send the specific hotkey for the requested panel.
        else if Name = "Effects"
            SendInput KS_Premiere.SelectPanel.Effects
        else if Name = "Player"
            SendInput KS_Premiere.SelectPanel.Player
        else if Name = "Timeline"
            SendInput KS_Premiere.SelectPanel.Timeline
        else if Name = "Bin"
            SendInput KS_Premiere.SelectPanel.Bin
        return
    }
    
    /**
     * @static
     * Focuses a panel and attempts to retrieve the ClassNN, screen coordinates, and dimensions of its content control.
     * Currently only fully implemented for "EffectControls".
     * @param {string} Name - The name of the panel (e.g., "EffectControls").
     * @param {number} [attempts=3] - Number of times to retry retrieving the control information.
     * @returns {Object|string} An object with {ClassNN, x, y, w, h} (screen coordinates/dimensions) on success, or an empty string on failure.
     */
    static ClassNN(Name, attempts := 3) {
        classNN := ""
        this.Focus(Name) ; Focus the target panel.
        Sleep(33)
        
        while (attempts > 1 or classNN = "") {
            attempts--
            try {
                ; Get the handle of the currently focused control within the active window ("A").
                hCtrl := ControlGetFocus("A")
                if !hCtrl
                    throw Error("No control focused")
                
                ; Retrieve the ClassNN (Class Name and Instance Number) for the focused control.
                classNN := ControlGetClassNN(hCtrl)
                if !classNN
                    throw Error("ClassNN not found")
                
                ; Get the position and size of the control, relative to the window.
                ControlGetPos &cx, &cy, &cw, &ch, classNN, "A"
                
                ; Get the position of the entire Premiere Pro window.
                WinGetPos &wx, &wy,,, "A"
                
                ; Calculate the control's absolute screen coordinates.
                globalX := (wx + cx)
                ; Add an offset (+55) to the Y coordinate, typically to skip the window's title bar/tabs 
                ; and ensure the coordinate starts within the panel's content area.
                globalY := (wy + cy) + 55 
                ; Comment: 'dunno why, but +50 seems to be needed for image search to work...'
                
                ; Return the control information.
                return {
                    ClassNN: classNN,
                    x: globalX,
                    y: globalY,
                    w: cw,
                    h: ch
                   }
                    
                } catch {
                    Sleep(25)
                    continue ; Retry the loop on failure.
                }
            }
            MsgBox "ClassNN not found for " Panel
            return ""
        ; Other panels would require their own specific ClassNN retrieval logic here.
    }
}