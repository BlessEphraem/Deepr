#Requires AutoHotkey v2.0

WatchError() {
    ; Vérifie s'il y a une MsgBox avec le titre "Erreur"
    if WinExist(Err) {
        ; Débloque tout
        try BlockInput("Off")
        try BlockInput("MouseMoveOff")
        try BlockInput("SendOff")

        ; (Optionnel) Affiche un message discret pour confirmer
        ToolTip "💡 Sécurité : BlockInput désactivé automatiquement.", 100, 100
        SetTimer(() => ToolTip(), -2000) ; cache le tooltip après 2s
    }
}