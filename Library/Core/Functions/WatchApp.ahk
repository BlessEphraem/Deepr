#Requires AutoHotkey v2.0

WatchApp(g_AppsToPin) {

    ; On boucle sur chaque élément (chaque critère)
    ; contenu dans notre tableau g_AppsToPin.
    for winCriterion in g_AppsToPin
    {
        ; 1. Vérifier si une fenêtre correspondante existe.
        ; WinExist() renvoie l'ID unique (HWND) de la première
        ; fenêtre trouvée, ou 0 si aucune fenêtre ne correspond.
        hwnd := WinExist(winCriterion)

        ; 2. Si la fenêtre existe (hwnd n'est pas 0)...
        if (hwnd)
        {
            ; 3. On vérifie son "style étendu" (ExStyle).
            ; Le style "Always on Top" (WS_EX_TOPMOST)
            ; correspond à la valeur hexadécimale 0x8.
            currentStyle := WinGetExStyle("ahk_id " hwnd)

            ; 4. On vérifie si le style 0x8 n'est PAS déjà appliqué.
            ; L'opérateur "&" (ET binaire) vérifie si le "bit"
            ; 0x8 est "allumé" dans currentStyle.
            ; On met un "!" (NON) devant pour agir
            ; seulement si ce n'est PAS le cas.
            if !(currentStyle & 0x8)
            {
                ; 5. La fenêtre existe mais n'est pas "On Top".
                ; On la met donc en "Always on Top" !
                WinSetAlwaysOnTop(1, "ahk_id " hwnd)
            }
        }
        ; Si (hwnd) est 0 (faux), la fenêtre n'existe pas,
        ; donc on ne fait rien et on passe à l'élément suivant.
    }
}

#Requires AutoHotkey v2.0

/**
 * WatchChildApp - Cherche une fenêtre enfant par titre et vérifie son critère AHK parent.
 *
 * @param {String} ahkCriteria - Le critère AHK à vérifier pour la fenêtre enfant trouvée
 * (ex: "ahk_exe Premiere Pro.exe").
 * @param {Array} childTitles - Un tableau de titres de fenêtre à rechercher (ex: ["Track Fx Editor - ", "Keyboard Shortcuts"]).
 */
WatchChildApp(ahkCriteria, childTitles) {
    ; Afficher pour le debug.

    ; On boucle sur chaque titre de fenêtre enfant à rechercher.
    for childTitle in childTitles
    {
        ; 1. Chercher la fenêtre enfant par son titre exact (match partiel si le titre se termine par ' - ').
        ; La fonction WinExist utilise le mode AHK_TITLE_MATCH_MODE par défaut (2 - contient).
        ; On utilise le titre seul ici, car AHK va chercher la fenêtre qui match CE titre en premier.
        ; On ajoute 'ahk_class' pour ne pas affecter la recherche par titre, mais pour le debug
        ; on pourrait utiliser 'ahk_id' plus tard pour cibler précisément.
        local hwnd := WinExist(childTitle)

        ; Afficher l'état de la recherche pour le debug.
        if (hwnd) {

            ; 2. Si la fenêtre enfant existe (hwnd n'est pas 0)...
            ; On vérifie maintenant si elle correspond au critère AHK fourni (ahkCriteria).
            ; Ceci vérifie si le processus parent/propriétaire est le bon.
            ; On concatène le ahk_id pour s'assurer que WinExist utilise CETTE fenêtre spécifique pour la vérification.
            if (WinExist("ahk_id " hwnd " " ahkCriteria))
            {

                ; 3. On vérifie son "style étendu" (ExStyle).
                ; Le style "Always on Top" (WS_EX_TOPMOST) correspond à la valeur hexadécimale 0x8.
                local currentStyle := WinGetExStyle("ahk_id " hwnd)

                ; 4. On vérifie si le style 0x8 n'est PAS déjà appliqué.
                ; L'opérateur "&" (ET binaire) vérifie si le "bit" 0x8 est "allumé" dans currentStyle.
                if !(currentStyle & 0x8)
                {
                    ; 5. La fenêtre enfant existe, match le critère, et n'est pas "On Top".
                    ; On la met donc en "Always on Top" !
                    WinSetAlwaysOnTop(1, "ahk_id " hwnd)
                    ; On sort de la boucle dès qu'une fenêtre enfant correspondante est trouvée et traitée.
                    return
                } else {
                    ; La fenêtre est déjà "On Top", on peut s'arrêter aussi.
                    return
                }
            } else {
                ; Fenêtre trouvée, mais le critère AHK ne correspond pas (pas le bon parent).
                ToolTip("WatchChildApp: Fenêtre trouvée (" childTitle . ") mais le critère AHK ne correspond pas. Ignoré.", 10, A_ScreenHeight - 60, 2000)
            }
        }
    }
    ; Si aucune fenêtre enfant n'est trouvée après la boucle, on affiche un message.
}
