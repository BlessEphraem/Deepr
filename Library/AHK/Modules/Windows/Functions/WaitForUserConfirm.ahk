#Requires AutoHotkey v2.0

/**
 * Pauses script execution and waits for the user to press one of several specified keys.
 * Displays a tooltip with instructions.
 *
 * This function is "variadic," meaning you can pass multiple key names as arguments.
 * Example: WaitForUserConfirm("Enter", "LButton", "Escape")
 *
 * @param {Array<string>} keys* An array of key names to watch for (e.g., "Enter", "LButton").
 * @returns {string} The string name of the key that the user pressed.
 *
 * @remarks
 * This function includes safety features:
 * 1. It sends a "Key Up" event for the pressed key to prevent it from getting stuck.
 * 2. It sends a "LButton Up" event to ensure any accidental mouse drags are released.
 */
WaitForUserConfirm(keys*) {
    ; 'keys*' is a variadic parameter, meaning 'keys' is now an Array
    ; of all arguments passed to the function.
    
    ; This is a polling loop. It will run indefinitely until 'return' is called.
    while true {
        ; Iterate over every key name passed into the function
        for key in keys {
            ; Check the "P" (physical) state of the key.
            ; This is more reliable than the logical state.
            if GetKeyState(key, "P") {
                ; --- SAFETY FEATURES ---
                
                ; 1. Send a "Key Up" for the key that was pressed.
                ; This prevents the key from getting "stuck" down or
                ; being passed to the active window.
                SendInput "{" key " Up}"
                
                ; 2. Send a "Left Button Up". This is a crucial safety net
                ; to release any mouse drag that might be active.
                SendInput "{LButton Up}"
                
                ; Clear the instructional tooltip
                Tooltip
                
                sleep 10 ; Short pause for stability
                
                ; Exit the function and return the name of the key that was pressed
                return key
            }
        }
        
        ; --- IDLE STATE ---
        
        ; While waiting, display a tooltip with instructions.
        ; We join the 'keys' array with ", " to create a readable list.
        ; `n is a newline character.
        Tooltip "PRESS " keys.Join(", ") " `nWHEN DONE"
        
        ; Sleep for 10ms to prevent the loop from using 100% CPU.
        ; This is the poll interval.
        Sleep 10
    }
}