WatchModifierKeys() {

    modifierKeys := [
        "LAlt",
        "LCtrl",
        "LShift",
        "LWin",
        "RAlt",
        "RCtrl",
        "RShift",
        "RWin"
    ]

    for key in modifierKeys {
        ; État logique = ce que le système croit
        logicalDown := GetKeyState(key)
        ; État physique = ce que ton clavier envoie réellement
        physicalDown := GetKeyState(key, "P")

        ; Si le système pense que la touche est enfoncée,
        ; mais que physiquement elle est relâchée :
        if (logicalDown && !physicalDown) {
            Send "{" key " up}"
            ToolTip key " libérée (correction Alt bloqué)"
            SetTimer () => ToolTip(""), -1000  ; Cache le tooltip après 1s
        }
    }
}

