#Requires AutoHotkey v2.0

/**
 * @function ApplyPreset
 * Guides the user to visually drag an effect preset from the Effects panel
 * onto the timeline in Adobe Premiere Pro. It handles panel activation,
 * mouse confinement, and input blocking during the drag operation.
 * NOTE: This function relies on external definitions like KS_Premiere.SelectPanel.Effect, 
 * KS_Premiere.SearchBox, TimedTooltip, and ClassNN_ToCoords.
 * @param {boolean} [ClosePanel=false] If true, sends Ctrl+W after the drag operation to close the Effects panel.
 * @returns {void}
 */
ApplyPreset(ClosePanel := false) {
    
    ; Ensure coordinate modes are set to 'Screen' for reliable positioning across monitors.
    CoordMode "Pixel", "Screen"
    CoordMode "ToolTip", "Screen"
    CoordMode "Mouse", "Screen"
    
    ; Ensure the left mouse button is released before starting the operation.
    SendInput "{LButton Up}"

    ; Store the mouse's starting position to restore it later.
    MouseGetPos &mStart_X, &mStart_Y
    
    ; Send the hotkey/command to select/focus the Effects panel (must be defined externally).
    SendInput KS_Premiere.SelectPanel.Effect
    Sleep 250 ; Give the application time to focus the panel.

    ; Identify the active window handle (expected to be Premiere Pro).
    hwnd := WinExist("A")
    try {
        ; Get the ClassNN of the currently focused control (which should be the Effects panel content).
        effectClassNN := ControlGetClassNN(ControlGetFocus(hwnd))
    }
    catch {
        ; If the focus cannot be retrieved (e.g., panel is missing), show an error tooltip and exit.
        Tooltip("Can't find effect panel.`n" . "Panel was probably closed, try again." . "", 4000)
        Exit
    }

    ; Get the position and dimensions of the focused control (Effects panel content).
    ControlGetPos &x, &y, &w, &h, effectClassNN, hwnd
    
    ; Send the hotkey/command to focus the Search Box within the panel (must be defined externally).
    SendInput KS_Premiere.SearchBox

    Sleep 50
    ; Get the ClassNN of the search box (used to identify the panel, though the effectClassNN is used for dimensions).
    searchClassNN := ControlGetClassNN(ControlGetFocus(hwnd))
    
    ; Convert the control's coordinates (relative to the window) to screen coordinates.
    ; NOTE: This helper function must be defined elsewhere.
    coords := ClassNN_ToCoords(hwnd, x, y, w, h)

    ; Move the mouse cursor to the center of the Effects panel's content area.
    MouseMove (coords.x_screen + w // 2), (coords.y_screen + h // 2)
    
    ; Confine the mouse cursor to the boundaries of the Effects panel during the selection phase.
    ClipCursor({x1: coords.x_screen, y1: coords.y_screen, x2: coords.x_screen + w, y2: coords.y_screen + h})

    ; --- WAIT FOR USER INTERACTION (LButton Click or Esc) ---
    Loop {
        ; Break the loop if the Left Mouse Button is pressed (user has clicked a preset).
        if GetKeyState("LButton")
            break
        ; Exit the function cleanly if the Escape key is pressed (user cancels).
        if GetKeyState("Esc") {
            ClipCursor() ; Release the cursor lock.
            MouseMove mStart_X, mStart_Y ; Restore original mouse position.
            Exit
        }
        Sleep(15)
    }

    ; Release the cursor confinement once the user has started the drag.
    ClipCursor()

    ; Block user input to ensure the subsequent drag/drop movement is precise and uninterrupted.
    BlockInput "On" 
    ; Specifically allow mouse movement commands from AHK, but block user mouse movements.
    BlockInput "MouseMove" 

    ; Simulate holding the left mouse button down (beginning the drag).
    SendInput "{LButton Down}"

    ; Simulate a short movement to ensure the drag operation is properly registered by the OS/Application.
    loop 2 {
        ; Move the mouse 30 pixels right (relative to the current position).
        MouseMove 30, 0, , "R"
        Sleep 33
    }

    ; Optional: Close the panel after the drag/drop if requested.
    if ClosePanel {
        ; Sends Ctrl+W to close the active panel in Premiere Pro.
        SendInput "^{w}"
    }
 
    ; Move the mouse back to its original position.
    MouseMove mStart_X, mStart_Y

    ; Release input blocks in reverse order.
    BlockInput "MouseMoveOff"
    BlockInput "Off"
    exit
}