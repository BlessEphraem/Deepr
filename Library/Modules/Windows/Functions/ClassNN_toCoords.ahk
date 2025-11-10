#Requires AutoHotkey v2.0

ClassNN_ToCoords(hwnd, x, y, w, h) {
    ; Convertir coords en écran
    pt := Buffer(8)
    NumPut("int", x, pt, 0), NumPut("int", y, pt, 4)
    DllCall("ClientToScreen", "ptr", hwnd, "ptr", pt)
        ;The ClientToScreen function converts the client-area coordinates of a specified point to screen coordinates.

    x_screen := NumGet(pt, 0, "int")
    y_screen := NumGet(pt, 4, "int")
    x_center := x_screen + w // 2
    y_center := y_screen + h // 2
    return { 
        x_screen: x_screen,
        y_screen: y_screen,
        x_center: x_center,
        y_center: y_center,
            }
}