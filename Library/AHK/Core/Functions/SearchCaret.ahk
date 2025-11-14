#Requires AutoHotkey v2.0

SearchCaret(control := "A", Duration := 3000) {
    local maxTime := A_TickCount + Duration
    
    ; Tenter de trouver le focus sur 'Edit1' (la barre d'adresse) pendant la durée spécifiée.
    while (A_TickCount < maxTime) {
        if (ControlGetFocus("A") == control) {
            return true ; Focus trouvé
        }
        Sleep 50 ; Petite pause pour ne pas surcharger le processeur
    }
    
    return false ; Focus non trouvé dans le délai imparti
}