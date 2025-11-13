#Requires AutoHotkey v2.0

/**
 * Converts client-area coordinates to absolute screen coordinates and calculates the center.
 * This is useful for getting the absolute screen position of a control or region
 * within a window, given its client-relative position and size.
 *
 * @param {number} hwnd The handle (HWND) to the parent window.
 * @param {number} x    The client x-coordinate (relative to the window's top-left content area).
 * @param {number} y    The client y-coordinate (relative to the window's top-left content area).
 * @param {number} w    The width of the region.
 * @param {number} h    The height of the region.
 * @returns {Map} An object (Map) with absolute screen coordinates:
 * { x_screen: number, y_screen: number, x_center: number, y_center: number }
 */
ClassNN_ToCoords(hwnd, x, y, w, h) {
    ; Allocate an 8-byte buffer for a Windows POINT structure
    ; A POINT structure contains two 32-bit integers (LONG): x and y. (2 * 4 bytes = 8 bytes)
    pt := Buffer(8)
    
    ; Populate the buffer with the input client coordinates
    NumPut("int", x, pt, 0) ; Put x at offset 0
    NumPut("int", y, pt, 4) ; Put y at offset 4

    ; Call the Windows API function to convert client coordinates to screen coordinates.
    ; This function modifies the 'pt' buffer in-place.
    DllCall("ClientToScreen", "ptr", hwnd, "ptr", pt)
    
    ; Retrieve the converted screen coordinates from the buffer
    x_screen := NumGet(pt, 0, "int")
    y_screen := NumGet(pt, 4, "int")
    
    ; Calculate the center of the region using screen coordinates
    ; The '//' operator performs integer division.
    x_center := x_screen + w // 2
    y_center := y_screen + h // 2
    
    ; Return a Map (AHK's object) containing all the calculated values
    return {
        x_screen: x_screen,
        y_screen: y_screen,
        x_center: x_center,
        y_center: y_center
    }
}