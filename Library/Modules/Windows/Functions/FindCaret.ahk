#Requires AutoHotkey v2.0

FindCaret(timeoutMs := 700, showTooltip := true) {
    CoordMode "Caret", "Screen"
    attempts := 0
    interval := 33
    maxAttempts := timeoutMs // interval

    while (attempts < maxAttempts) {
        CaretGetPos(&x, &y)
        attempts++
        if (x != "" && y != "") {
            return {x: x, y: y}
        }
        sleep interval
    }

    if showTooltip
        SetTimer Tooltip.Bind("NO CARET FOUND"), -100
    return false
}