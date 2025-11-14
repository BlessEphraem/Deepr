#Requires AutoHotkey v2.0

/**
 * @class
 * @description Provides static methods for window management (Move, Resize).
 */
class Window {
    /**
     * Moves the active window by dragging.
     * @param {string} MouseButton The mouse button to monitor for dragging (e.g., "LButton", "RButton").
     */
    static Move(MouseButton)
    {
        try {
            hold := 0
            CoordMode "Mouse"
            ; Get the initial mouse position and window id
            MouseGetPos &KDE_X1, &KDE_Y1, &KDE_id
            ; Get the initial window position and size.
            WinGetPos &KDE_WinX1, &KDE_WinY1, &KDE_WinW, &KDE_WinH, KDE_id
            sleep(1)

            ; Define the window region the mouse is currently in (unused for basic move, but kept for context).
            ; The four regions are Up and Left, Up and Right, Down and Left, Down and Right.
            if (KDE_X1 < KDE_WinX1 + KDE_WinW / 2)
                KDE_WinLeft := 1
            else
                KDE_WinLeft := -1
            if (KDE_Y1 < KDE_WinY1 + KDE_WinH / 2)
                KDE_WinUp := 1
            else
                KDE_WinUp := -1

            if GetKeyState(MouseButton, "P")
                Loop
                {
                    hold++
                    if !GetKeyState(MouseButton, "P") ; Break if button has been released.
                        break
                    WinActivate KDE_id
                    MouseGetPos &KDE_X2, &KDE_Y2 ; Get the current mouse position.
                    KDE_X2 -= KDE_X1 ; Obtain an offset from the initial mouse position.
                    KDE_Y2 -= KDE_Y1
                    KDE_WinX2 := (KDE_WinX1 + KDE_X2) ; Apply this offset to the window X position.
                    KDE_WinY2 := (KDE_WinY1 + KDE_Y2) ; Apply this offset to the window Y position.
                    WinMove KDE_WinX2, KDE_WinY2,,, KDE_id ; Move the window to the new position.
                }


            if hold < 6 {
                SendInput "{" MouseButton "}"
            }

            return

        } catch {
            tooltip "Failed moving window."
            return
        }

    }

    /**
     * Resizes the active window based on the mouse position relative to the center.
     * @param {string} MouseButton The mouse button to monitor for dragging (e.g., "LButton", "RButton").
     */
    static Resize(MouseButton)
    {
        CoordMode "Mouse"
        ; Get the initial mouse position and window id.
        MouseGetPos &KDE_X1, &KDE_Y1, &KDE_id
        ; Abort if the window is maximized.
        if WinGetMinMax(KDE_id)
            return
        ; Get the initial window position and size.
        WinGetPos &KDE_WinX1, &KDE_WinY1, &KDE_WinW, &KDE_WinH, KDE_id
        ; Define the window region the mouse is currently in.
        ; The four regions are Up and Left, Up and Right, Down and Left, Down and Right.
        if (KDE_X1 < KDE_WinX1 + KDE_WinW / 2)
            KDE_WinLeft := 1
        else
            KDE_WinLeft := -1
        if (KDE_Y1 < KDE_WinY1 + KDE_WinH / 2)
            KDE_WinUp := 1
        else
            KDE_WinUp := -1

        Loop
        {
            if !GetKeyState(MouseButton, "P") ; Break if button has been released.
                break
            MouseGetPos &KDE_X2, &KDE_Y2 ; Get the current mouse position.
            ; Get the current window position and size (important for continuous adjustment).
            WinGetPos &KDE_WinX1, &KDE_WinY1, &KDE_WinW, &KDE_WinH, KDE_id
            KDE_X2 -= KDE_X1 ; Obtain an offset from the initial mouse position.
            KDE_Y2 -= KDE_Y1
            ; Then, act according to the defined region to resize.
            WinMove KDE_WinX1 + (KDE_WinLeft+1)/2*KDE_X2  ; X of resized window (moves only if left region)
                  , KDE_WinY1 +    (KDE_WinUp+1)/2*KDE_Y2  ; Y of resized window (moves only if top region)
                  , KDE_WinW  -      KDE_WinLeft  *KDE_X2  ; W of resized window (adds/subtracts based on left/right region)
                  , KDE_WinH  -        KDE_WinUp  *KDE_Y2  ; H of resized window (adds/subtracts based on top/bottom region)
                  , KDE_id
            KDE_X1 := (KDE_X2 + KDE_X1) ; Reset the initial X position for the next iteration.
            KDE_Y1 := (KDE_Y2 + KDE_Y1) ; Reset the initial Y position for the next iteration.
        }
    }


}