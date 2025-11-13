#Requires AutoHotkey v2.0

/**
 * Restricts or frees the mouse cursor's movement.
 * If 'rect' is provided, the cursor is confined to that screen rectangle.
 * If 'rect' is omitted, all cursor restrictions are removed.
 *
 * @param {Map | unset} [rect] An optional object (Map) with screen coordinates:
 * { x1: number, y1: number, x2: number, y2: number }.
 * 'x1' and 'y1' define the top-left corner.
 * 'x2' and 'y2' define the bottom-right corner.
 * If this parameter is not set, the cursor will be unclipped.
 * @returns {number} A non-zero value if successful, or zero if it fails.
 */
ClipCursor(rect := unset) {
    ; Check if the optional 'rect' parameter was provided
    if IsSet(rect) {
        ; A Windows RECT structure has 4 32-bit integers (left, top, right, bottom)
        ; 4 * 4 bytes = 16 bytes
        buf := Buffer(16)
        
        ; Populate the buffer with the rectangle's coordinates
        NumPut("int", rect.x1, buf, 0)  ; RECT.left
        NumPut("int", rect.y1, buf, 4)  ; RECT.top
        NumPut("int", rect.x2, buf, 8)  ; RECT.right
        NumPut("int", rect.y2, buf, 12) ; RECT.bottom
        
        ; Call the API to clip the cursor, passing a pointer to our RECT buffer
        return DllCall("ClipCursor", "ptr", buf)
    } else {
        ; The 'rect' parameter was not provided
        ; Passing a NULL pointer (0) to ClipCursor unclips the cursor.
        return DllCall("ClipCursor", "ptr", 0)
    }
}