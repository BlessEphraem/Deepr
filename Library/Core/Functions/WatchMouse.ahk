#Requires AutoHotkey v2.0

WatchMouse()
{
    MouseGetPos , , &WindowUnderMouse, &ControlUnderMouse

    try ProcessNameHWND := WinGetProcessName("A") 
    ClassHWND := " ahk_class " WinGetClass(WindowUnderMouse)
    ControlHWND := " Control: " ControlUnderMouse

    Text := ProcessNameHWND "|" ClassHWND "|" ControlHWND  ; Regrouper les données dans une seule variable séparée par "|"

    WatchMouse_Tooltip(Text, "Off")
}

WatchMouse_Tooltip(Text, OnOff) {
    if (OnOff = "Off") {
        ToolTip  ; Efface la ToolTip si "Off"
        return
    }
    
    lines := StrSplit(Text, "|")  ; Décomposer la variable en une liste
    formattedText := ""
    
    for index, line in lines {
        formattedText .= line
        if (index < lines.Length) {
            formattedText .= " `n "  ; Ajouter un saut de ligne sauf pour le dernier élément
        }
    }
    
    ToolTip formattedText  ; Afficher la ToolTip avec le texte formaté
}


