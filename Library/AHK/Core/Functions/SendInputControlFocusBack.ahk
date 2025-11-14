#Requires AutoHotkey v2.0

SendInputControlFocusBack(Hotkeys, WhichPanel) {
    Controls := ControlGetFocus("A")
    SendInput WhichPanel
    sleep 10
    ; Vérifie si Hotkeys est un array
    if Type(Hotkeys) = "Array" {
        for Each, Key in Hotkeys {
            SendInput Key
            Sleep 50
        }
    } else {
        ; Si ce n'est pas un array, l'utiliser comme une seule chaîne
        SendInput Hotkeys
        Sleep 50
    }

    ControlFocus Controls
}