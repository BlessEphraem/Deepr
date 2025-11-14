#Requires AutoHotkey v2.0

/**
 * Attempts to find the screen coordinates of the text caret (blinking cursor).
 * It polls repeatedly for a specified duration because the caret might not
 * be immediately available.
 *
 * @param {number} [timeoutMs=700]     The total time in milliseconds to keep trying
 * to find the caret.
 * @param {boolean} [showTooltip=true] If true, shows a "NO CARET FOUND" tooltip
 * on failure.
 * @returns {Map | boolean} A Map `{x: number, y: number}` with the caret's
 * screen coordinates if found, or `false` on failure.
 */
FindCaret(timeoutMs := 700, showTooltip := true) {
    ; Ensure that CaretGetPos returns screen-relative (absolute) coordinates
    CoordMode "Caret", "Screen"
    
    attempts := 0
    interval := 33 ; Poll interval in ms (approx. 30 FPS)
    
    ; Calculate the total number of attempts based on the timeout
    maxAttempts := timeoutMs // interval

    ; Start the polling loop
    while (attempts < maxAttempts) {
        ; Try to get the caret's position.
        ; &x and &y are output variables.
        CaretGetPos(&x, &y)
        attempts++
        
        ; If x and y are not empty, the caret was successfully found.
        if (x != "" && y != "") {
            return {x: x, y: y} ; Return the coordinates object
        }
        
        ; Wait for the interval duration before the next attempt
        ; This prevents a tight loop and high CPU usage.
        sleep interval
    }

    ; If the loop finishes, the caret was not found within the timeout
    if showTooltip
        ; Schedule a one-time, 100ms tooltip to show the failure
        ; Tooltip.Bind(...) creates a BoundFunc object for SetTimer.
        SetTimer Tooltip.Bind("NO CARET FOUND"), -100
        
    ; Return false to indicate failure
    return false
}