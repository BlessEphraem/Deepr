#Requires AutoHotkey v2.0

; === Crée la GUI une seule fois, dès le lancement ===
global SuspendGUI := Gui("+AlwaysOnTop -Caption +ToolWindow +E0x20") ; +E0x20 = ignore les clics
SuspendGUI.BackColor := "0x000000"
SuspendGUI.SetFont("s14 bold cffffff", "Sandra")
SuspendGUI.Add("Text", "vSuspendedText BackgroundTrans", "SCRIPT SUSPENDED")

; === Calcul position GUI ===
global GuiWidth := 230
global GuiHeight := 40
; Détecte les moniteurs
monitors := MonitorGetCount()
monIndex := (monitors >= 2) ? 2 : 1

MonitorGet(monIndex, &monLeft, &monTop, &monRight, &monBottom)
GuiX := monRight - GuiWidth - 20
GuiY := monTop + 20

WinSetTransColor("0x000000", SuspendGUI.Hwnd)