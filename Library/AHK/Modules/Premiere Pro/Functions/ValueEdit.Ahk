#Requires AutoHotkey v2.0
#SingleInstance Force

; ---------------------------------------------------------
; Fonction principale : ValueEdit(Offset)
; Exemple d'utilisation :
;   ^a::ValueEdit("+10")
;   ^b::ValueEdit("+0,5")

; ---------------------------------------------------------
ValueEdit(offset) {
    ; Sauvegarde du presse-papiers actuel
    ClipSaved := ClipboardAll()

    ; Copie la sélection
    A_Clipboard := ""
    Send "^c"
    ClipWait(0.5)
    Sel := Trim(A_Clipboard)

    if (Sel = "") {
        MsgBox "❌ Aucune sélection trouvée.", "Erreur"
        A_Clipboard := ClipSaved
        return
    }

    ; Vérification du format
    ; Accepte des nombres comme : 100,0 | 100.0 | -25,5 | +12.5
    ; Mais pas : 100% ou 100,0%
    if !RegExMatch(Sel, "^[+-]?\d+(?:[.,]\d+)?$") {
        MsgBox "❌ La sélection n’est pas une valeur valide.`nExemples valides : 100,0 | 100.5 | -25,5", "Erreur"
        A_Clipboard := ClipSaved
        return
    }

    ; Détection du séparateur utilisé dans la sélection
    sepSel := InStr(Sel, ",") ? "," : "."

    ; Conversion du texte sélectionné en nombre standard (avec .)
    val := StrReplace(Sel, ",", ".")
    val := val + 0.0  ; force la conversion numérique

    ; Normalisation de l’offset
    offsetNorm := StrReplace(offset, ",", ".")
    if !RegExMatch(offsetNorm, "^[+-]?\d+(?:\.\d+)?$") {
        MsgBox "❌ Offset invalide : " offset, "Erreur"
        A_Clipboard := ClipSaved
        return
    }
    offsetNum := offsetNorm + 0.0

    ; Calcul de la nouvelle valeur
    newVal := val + offsetNum

    ; Conversion inverse selon le séparateur d’origine
    newText := sepSel = "," ? StrReplace(Format("{:.10g}", newVal), ".", ",") : Format("{:.10g}", newVal)

    ; Copie et remplace la sélection
    A_Clipboard := newText
    Send "^v"
    Sleep 12
    Send "^a"

    ; Restaure le presse-papiers initial
    Sleep 100
    A_Clipboard := ClipSaved
}
