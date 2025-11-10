#Requires AutoHotkey v2.0

ClipCursor(rect := unset) {
    if IsSet(rect) {
        buf := Buffer(16)
        NumPut("int", rect.x1, buf, 0)
        NumPut("int", rect.y1, buf, 4)
        NumPut("int", rect.x2, buf, 8)
        NumPut("int", rect.y2, buf, 12)
        return DllCall("ClipCursor", "ptr", buf)
    } else {
        return DllCall("ClipCursor", "ptr", 0)
    }
}