#Requires AutoHotkey v2.0

WaitForUserConfirm(keys*) {
    ; keys* est un array des touches à surveiller
    while true {
        for key in keys {
            if GetKeyState(key, "P") {
                SendInput "{" key " Up}"
                SendInput "{LButton Up}"
                Tooltip
                sleep 10
                return key ; Retourne la touche utilisée
            }
        }
        Tooltip "PRESS " JoinArray(keys) " `nWHEN DONE"
        Sleep 10
    }
}