/**
 * @class Mouse
 * Provides static methods for interacting with the mouse position and the
 * corresponding window and control under the cursor.
 */

class Mouse {
    /**
     * Retrieves the coordinates of the mouse cursor, and the ID and control name
     * of the window under the cursor.
     *
     * **AHK 2.0 Usage:**
     * `pos := Mouse.Get()`
     * `MsgBox "Window ID: " pos.Id ", Control: " pos.Control`
     *
     * @returns {{Id: Integer, Control: String}} An object containing:
     * - `Id`: The unique ID of the window under the cursor.
     * - `Control`: The class name of the control under the cursor.
     */
    static Get() {
        MouseGetPos ,, &Id, &Control
        return { Id: Id, Control: Control }
    }

    /**
     * Attempts to set the keyboard focus to the control currently under the mouse cursor.
     * If the control cannot be found or focused (e.g., if it's not a focusable control),
     * a transient tooltip message is displayed.
     *
     * **AHK 2.0 Usage:**
     * `Mouse.FocusActive()` ; Call this to focus the control under the mouse.
     *
     * @returns {void}
     */
    static FocusActive() {
        try ControlFocus(this.Get().Control, this.Get().Id)
        catch {
            ; TimedTooltip is a placeholder for a user-defined function that displays a temporary message.
            ; A SetTimer with a negative period (-100ms) executes once after 100ms.
            SetTimer((*) => TimedTooltip("Can't find control.", 2000), -100)
        }
        return
    }

    class Move {

        static Pixel(Xdirection := 0, YDirection := 0 ) {
            MouseGetPos &firstX, &firstY
            MouseMove firstX + (Xdirection), firstY + (YDirection)
            return
        }

        static Monitor(maxScreens := 0) {
            MonitorCount := MonitorGetCount()

            ; Validation du paramètre
            if (maxScreens > 0 && maxScreens > MonitorCount) {
                Tooltip "ERROR : Invalid screen value set. The code will execute for each monitor instead."
                Sleep 2000
                Tooltip ""
                maxScreens := 0  ; Revenir au comportement par défaut
            }
        
            ; Si un nombre de moniteurs spécifique est demandé
            max := (maxScreens > 0) ? maxScreens : MonitorCount
        
            CoordMode("Mouse", "Screen")
            MouseGetPos(&MouseX, &MouseY)
        
            ; Trouver sur quel écran on est
            current := 0
            Loop MonitorCount {
                MonitorGet(A_Index, &MonitorLeft, &MonitorTop, &MonitorRight, &MonitorBottom)
                if ((MouseX >= MonitorLeft) && (MouseX < MonitorRight) && (MouseY >= MonitorTop) && (MouseY < MonitorBottom)) {
                    current := A_Index
                    currentRX := (MouseX - MonitorLeft) / (MonitorRight - MonitorLeft)
                    currentRY := (MouseY - MonitorTop) / (MonitorBottom - MonitorTop)
                    break
                }
            }
        
            ; Calcul de l'écran suivant
            next := current + 1
            if (next > max)
                next := 1
        
            ; Aller au centre du moniteur suivant
            MonitorGet(next, &MonitorLeft, &MonitorTop, &MonitorRight, &MonitorBottom)
            newX := (MonitorLeft + MonitorRight) / 2
            newY := (MonitorTop + MonitorBottom) / 2

            ; Déplacement souris
            DllCall("SetCursorPos", "int", newX, "int", newY)
            Sleep 10
        }
    }
}