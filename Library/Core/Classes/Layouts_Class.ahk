#Requires AutoHotkey v2.0

Class Layouts {
   
    static Windows(*) {
        if this.GetActive() = "Windows"
            return true
        else
            return false
    }

    static Capslock(layout) {
        if this.GetActive() = layout && Toggle.CapsLock()
            return true
        else
            return false
    }
   
    static GetActive(*) {
        ; Test chaque programme, si actif → retourne winTitle ou winClass
        if WinActive(Application_Class.Arc.winTitle)
            return Application_Class.Arc.winTitle
        else if WinActive(Application_Class.PremierePro.winTitle)
            return Application_Class.PremierePro.winTitle
        else if WinActive(Application_Class.AfterFX.winTitle)
            return Application_Class.AfterFX.winTitle
        else if WinActive(Application_Class.Audition.winTitle)
            return Application_Class.Audition.winTitle
        else if WinActive(Application_Class.Illustrator.winClass)
            return Application_Class.Illustrator.winClass
        else if WinActive(Application_Class.Blender.winTitle)
            return Application_Class.Blender.winTitle
        else if WinActive(Application_Class.Explorer.winTitle)
            return Application_Class.Explorer.winTitle
        else
            return "Windows"
    }
}

Class Toggle {
    static CapsLock(*) {
        ; Test chaque programme, si actif → retourne winTitle ou winClass
        if GetKeyState("CapsLock", "T")
            return true
        else
            return false
    }
}