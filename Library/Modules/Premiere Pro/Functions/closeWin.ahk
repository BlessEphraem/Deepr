#Requires AutoHotkey v2.0

CloseWin() {
    ClassNN := WinGetClass("A")
    if ClassNN = "Premiere Pro"
        Exit
    Else
        WinClose("A")
}