#Requires AutoHotkey v2.0

; --- Tooltip Watchdog ---
global TooltipActive := false
global TooltipStart := 0
global TooltipTimeout := 5000


; Fonction de surveillance
WatchTooltip() {
    global TooltipActive, TooltipStart, TooltipTimeout
    tooltipWin := WinExist("ahk_class tooltips_class32") ; Vérifie s'il y a un tooltip
    ; Si un tooltip est visible
    if tooltipWin {
        if !TooltipActive {
            TooltipActive := true
            TooltipStart := A_TickCount
        } else if (A_TickCount - TooltipStart >= TooltipTimeout) {
            ; Supprime le tooltip en le cachant
            tooltip
            TooltipActive := false
        }
    } else {
        TooltipActive := false
    }
}