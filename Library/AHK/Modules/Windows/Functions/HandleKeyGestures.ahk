#Requires AutoHotkey v2.0

/**
 * @function CleanHotkey
 * @description Removes prefix/suffix modifiers from A_ThisHotkey (e.g., *, $, ~, #, ^, !, +, <, >)
 * to get the base key name (e.g., 'a', 'LButton').
 * @returns {String} The cleaned hotkey string.
 */
CleanHotkey() {
    ; Use a RegEx pattern to remove the common hotkey prefix/suffix symbols in AHK.
    return RegExReplace(A_ThisHotkey, "[*~$#^!+<>]")
}

/**
 * @function MultiAction
 * @description Manages a multi-action hotkey, supporting Single Press, Double Press, and Hold actions.
 * Actions are passed as function objects (or arrays of function objects) which receive
 * a Map object for passing state/data.
 *
 * @param {Array<Function>|Function|0} [Action_SinglePress=0] - Function(s) to execute on a single tap. If 0, defaults to pressing the key itself.
 * @param {Array<Function>|Function|0} [Action_DoublePress=0] - Function(s) to execute on a double tap.
 * @param {Array<Function>|Function|0} [Action_Hold=0]        - Function(s) to execute repeatedly while the key is held past the HoldedTimeout.
 * @param {Array<Function>|Function|0} [Action_Start=0]       - Function(s) to execute immediately upon key press (before any detection).
 * @param {Array<Function>|Function|0} [Action_End=0]         - Function(s) to execute after the main action (Single/Double/Hold) completes.
 * @param {Boolean} [SinglePressNoEnd=false]                  - If true, skips Action_End execution *only* for a Single Press.
 *
 * @returns {String} A comma-separated string of the action types triggered (e.g., "Action_SinglePress, Action_End"). Returns "None" if nothing triggered.
 */
HandleKeyGestures(Action_SinglePress := 0, Action_DoublePress := 0, Action_Hold := 0, Action_Start := 0, Action_End := 0, SinglePressNoEnd := false) {

    StartTime := A_TickCount
    ThisHotkey := CleanHotkey()
    HoldedAction := false
    ActionsTriggered := []      ; Array to store the names of triggered actions for the return string.
    Interval := 33              ; Sleep duration (ms) for internal loops, affects responsiveness.
    Timeout := 230              ; Max duration (ms) between key-up and key-down for Double Press detection.
    HoldedTimeout := 200        ; Min duration (ms) the key must be held to trigger Action_Hold.
    Actions := Map()            ; A Map object to pass state/data between different action functions.

    ; --- Utility Function to Build Return String (AHK v2.0 non-object method) ---
    BuildReturnString(ActionsArray) {
        ReturnString := ""
        Separator := ""
        for action in ActionsArray {
            ReturnString .= Separator action
            Separator := ", "
        }
        ; Return 'None' if empty, otherwise the constructed string.
        return ReturnString := (ReturnString = "" ? "None" : ReturnString)
    }

    ; --- Action Start Execution ---
    if Action_Start != 0 {
        ; Assuming Action_Start is a function object or an array of function objects.
        ; AHK v2.0 allows direct iteration over single functions/objects as if they were arrays of size 1.
        for fn in Action_Start {
            fn.Call(Actions) ; Execute the function, passing the state Map.
        }
        Sleep Interval
        ; Note: The name of the argument is not pushed to ActionsTriggered here in the original code.
    }

    ; --- Default SinglePress Setup ---
    ; If no single press action is provided, default to a function that returns the cleaned hotkey string.
    ; This is a placeholder for a 'do nothing' or 'send key' default action.
    if (Action_SinglePress = 0) {
        ; Use an array containing a lambda function that returns the key name.
        ; The original logic appears to intend this as a placeholder, perhaps for a future Send.
        Action_SinglePress := [(Actions) => CleanHotkey()]
    }

    ; --- Hold Detection Loop ---
    while GetKeyState(ThisHotkey, "P") { ; 'P' checks physical state of the key.
        Elapsed := A_TickCount - StartTime
        if Elapsed > HoldedTimeout {
            ActionsTriggered.Push("Action_Hold")
            HoldedAction := true
            ; Enter the dedicated hold loop once hold is detected
            while GetKeyState(ThisHotkey, "P") {
                if Action_Hold { ; Check if an Action_Hold function(s) was provided.
                    for fn in Action_Hold {
                        fn.Call(Actions)
                    }
                }
                Sleep Interval
            }
        }
        if HoldedAction {
            break ; Exit the initial detection loop if the hold was triggered.
        }
        ; Important: The original code is missing a Sleep/Wait here if the HoldedTimeout is not reached,
        ; which would lead to a near-instant single press if the key is released before the interval.
        ; However, due to the implicit 'break' when the key is released, it proceeds to the next block quickly.
    }

    ; --- Single/Double Press Handling ---
    if !HoldedAction {
        if (Action_DoublePress != 0) {
            ; Wait for the key to be released before looking for the second press.
            KeyWait(ThisHotkey)
            ; Check if the key is *not* currently pressed (it should have been released by now).
            if !GetKeyState(ThisHotkey, "P") {
                ; KeyWait for a second press (D=Down) within the Timeout duration.
                if KeyWait(ThisHotkey, "D T" Timeout / 1000) { ; AHK v2 requires Time in seconds.
                    ; Double Press Detected
                    for fn in Action_DoublePress {
                        fn.Call(Actions)
                    }
                    Sleep Interval
                    ActionsTriggered.Push("Action_DoublePress")
                } else {
                    ; Single Press Detected (Double press timed out)
                    for fn in Action_SinglePress {
                        fn.Call(Actions)
                    }
                    Sleep Interval
                    ActionsTriggered.Push("Action_SinglePress")
                }
            }
            ; If GetKeyState(ThisHotkey, "P") was true here, it means the key was still down
            ; after the initial KeyWait, which shouldn't happen unless KeyWait failed/was interrupted.
        } else {
            ; Simple Single Press if no Double Press action is defined (immediate execution).
            for fn in Action_SinglePress {
                fn.Call(Actions)
                Sleep Interval
            }
            ActionsTriggered.Push("Action_SinglePress")
        }
    }

    ; --- Intermediate Return Check ---
    ReturnString := BuildReturnString(ActionsTriggered)
    if (!HoldedAction and SinglePressNoEnd) {
        return ReturnString ; Exit immediately if it was a Single Press and SinglePressNoEnd is true.
    }

    ; --- Action End Execution ---
    if Action_End != 0 {
        for fn in Action_End {
            fn.Call(Actions)
        }
        Sleep Interval
        ActionsTriggered.Push("Action_End") ; Note: This action is pushed even if SinglePressNoEnd caused an early exit (only relevant if the function continued).
    }

    ; --- Final Return ---
    ReturnString := BuildReturnString(ActionsTriggered)
    return ReturnString
}