#Requires AutoHotkey v2.0
#singleinstance force

; --- IMPORTS ---
#Include "%A_ScriptDir%\SupportFiles\AHK\RichEdit.ahk"
#Include "%A_ScriptDir%\SupportFiles\AHK\RichEditDlgs.ahk"


; Coordonnées de la souris basées sur l'écran
CoordMode "Mouse", "Screen"
; --------------------------------------------------------------------------------------------------
; CLASSE STATIQUE POUR LE PANNEAU DE NOTES LATÉRAL
; --------------------------------------------------------------------------------------------------

class GUI_SideNote
{
    ; --- CONFIGURATION STATIQUE (Propriétés de la classe) ---
    static notesFile := A_ScriptDir "\notes.rtf"
    static panelWidth := 400
    static panelOpacity := 255
    static showDelay := 200     ; ms (avant de glisser)
    static autoSaveInterval := 1000 ; ms (intervalle de sauvegarde)
    static slideSpeed := 50     ; Plus petit est plus rapide
    static margin := 5          ; Marge en pixels pour la détection du bord de l'écran

    ; --- VARIABLES D'ÉTAT (Propriétés de la classe) ---
    static isPanelShown := false
    static hoverStartTime := 0
    static mouseIsOverPanel := false

    ; --- CONTRÔLES GUI (Propriétés de la classe) ---
    static GuiPanel := ""       ; Le GUI principal
    static richEditControl := "" ; Le contrôle RichEdit pour les notes
    static btnDummy := ""       ; Bouton factice pour déplacer le focus

    ; --- DIMENSIONS DE L'ÉCRAN (Propriétés de la classe) ---
    static primaryScreenWidth := 0
    static primaryScreenHeight := 0
    
    ; ----------------------------------------------------------------------------------------------
    ; MÉTHODE D'INITIALISATION
    ; ----------------------------------------------------------------------------------------------

    static Init()
    {
        ; Récupération des dimensions de l'écran
        this.primaryScreenWidth := SysGet(0)
        this.primaryScreenHeight := SysGet(1)

        ; Création du GUI
        this.GuiPanel := Gui("+AlwaysOnTop -Caption +ToolWindow")
        this.GuiPanel.Color := "aaaaaa" 
        this.GuiPanel.Width := this.panelWidth
        this.GuiPanel.Height := this.primaryScreenHeight - 100
        ; Position initiale (caché à droite de l'écran)
        this.GuiPanel.X := this.primaryScreenWidth
        ; Centrage Vertical
        this.GuiPanel.Y := (this.primaryScreenHeight - this.GuiPanel.Height) // 2 
        
        ; Création du contrôle RichEdit
        this.richEditControl := RichEdit(this.GuiPanel, "w" this.panelWidth " h" this.GuiPanel.Height " vNotesEdit")
        this.richEditControl.WordWrap(true)
        this.richEditControl.ShowScrollBar(0, False) ; Cacher les barres de défilement si inutiles
        this.richEditControl.ShowScrollBar(1, False)

        ; Configuration des couleurs et du bouton factice
        this.GuiPanel.BackColor := this.GuiPanel.Color
        this.btnDummy := this.GuiPanel.Add("Button", "w1 h1 x-10 y-10", "") 
        this.btnDummy.Visible := false 

        ; Chargement du contenu existant
        this.LoadNotes()
        
        ; Configuration de la police
        this.richEditControl.SetDefaultFont({Size: 16, Color: 0x000000, Name: "Atkinson Hyperlegible Regular"}) 
        
        ; Affichage initial du GUI (caché)
        this.GuiPanel.Show("x" this.GuiPanel.X " y" this.GuiPanel.Y)
        
        ; Configuration des événements
        this.GuiPanel.OnEvent("Close", (*) => ExitApp())
        this.GuiPanel.OnClose := this.OnGuiClose.Bind(this)
        
        ; Démarrage des timers
        SetTimer this.AutoSaveNotes.Bind(this), this.autoSaveInterval
        SetTimer this.CheckMouseHover.Bind(this), 100
    }
    
    ; ----------------------------------------------------------------------------------------------
    ; FONCTIONS DE GESTION DES NOTES
    ; ----------------------------------------------------------------------------------------------

    static LoadNotes()
    {
        if FileExist(this.notesFile) {
            content := FileRead(this.notesFile)
            this.richEditControl.SetText(content) 
            ; Positionner le curseur à la fin du texte
            pos := StrLen(content)
            this.richEditControl.SetSel(pos, pos) 
            
            this.btnDummy.Focus() ; Déplacer le focus vers le bouton invisible
        }
    }

    static AutoSaveNotes() 
    {
        ; Récupérer le contenu du RichEdit
        contentToSave := this.richEditControl.GetText()
        file := FileOpen(this.notesFile, "w") 
        
        if !file {
            ; En environnement de production, utiliser une méthode non bloquante (Log ou Toast Notification)
            ; MsgBox("Erreur lors de l'ouverture du fichier pour l'écriture.", "Erreur de Sauvegarde")
            return
        }
        file.Write(contentToSave)
        file.Close()
    }

    static OnGuiClose() 
    {
        ; 1. Sauvegarder le contenu (étape critique)
        this.AutoSaveNotes()
        
        ; 2. Appel à la fonction qui gère le glissement vers la droite (cacher)
        this.SlidePanel(false)
        
        ; Nous ne mettons PAS d'ExitApp() ici, sinon le script complet se ferme.
    }

    ; ----------------------------------------------------------------------------------------------
    ; GESTION DU HOVER ET DU GLISSEMENT
    ; ----------------------------------------------------------------------------------------------

    static CheckMouseHover() 
    {
        MouseGetPos(&mx, &my)

        x := 0, y := 0, w := 0, h := 0
        this.GuiPanel.GetPos(&x, &y, &w, &h)

        panelLeft := x
        panelRight := x + w
        panelTop := y
        panelBottom := y + h

        ; 1. Souris SUR le panneau GUI
        mouseOverWindow := (mx >= panelLeft && mx <= panelRight && my >= panelTop && my <= panelBottom)
        ; 2. Souris SUR le bord droit de l'écran
        mouseOverScreenEdge := (mx >= (this.primaryScreenWidth - this.margin) && mx <= this.primaryScreenWidth)

        mouseOver := mouseOverWindow || mouseOverScreenEdge
        
        ; Vérifier si le panneau GUI est la fenêtre active (focus)
        activeID := WinActive("A") 
        GuiPanelID := this.GuiPanel.Hwnd
        isFocused := (activeID = GuiPanelID)

        if mouseOver || isFocused {
            if !this.mouseIsOverPanel {
                ; Début du survol
                this.mouseIsOverPanel := true
                this.hoverStartTime := A_TickCount
            } else if (A_TickCount - this.hoverStartTime >= this.showDelay && !this.isPanelShown) {
                ; Le délai est écoulé, afficher le panneau
                this.SlidePanel(true)
            }
        } else {
            if (this.mouseIsOverPanel) { 
                ; La souris vient de sortir
                this.mouseIsOverPanel := false
                this.hoverStartTime := 0

                if (this.isPanelShown) { 
                    ; Cacher le panneau si visible
                    this.SlidePanel(false)
                }
            }
        }
    }

    static SlidePanel(show) 
    {
        ; Calculer la position X cible (visible ou cachée)
        ; -15 pour laisser une petite bordure visible, si souhaité
        targetX := show ? (this.primaryScreenWidth - this.panelWidth - 15) : this.primaryScreenWidth

        xPos := 0, yPos := 0, w := 0, h := 0
        this.GuiPanel.GetPos(&xPos, &yPos, &w, &h)
        currentX := xPos

        direction := (targetX < currentX) ? -1 : 1 ; -1 pour glisser à gauche (show), 1 pour glisser à droite (hide)

        ; Boucle d'animation
        while ((direction == 1 && currentX < targetX) || (direction == -1 && currentX > targetX)) {
            currentX += direction * this.slideSpeed

            ; S'assurer de ne pas dépasser la cible
            if ((direction == 1 && currentX > targetX) || (direction == -1 && currentX < targetX))
                currentX := targetX

            this.GuiPanel.Move(currentX, this.GuiPanel.Y)
            Sleep 10 ; Délai pour l'animation
        }

        this.isPanelShown := show
    }
}
