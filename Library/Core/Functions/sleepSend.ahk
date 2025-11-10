#Requires AutoHotkey v2.0

SleepSend(input, delay) {
    Sleep 100
    SendInput input
    Sleep delay
    return
}