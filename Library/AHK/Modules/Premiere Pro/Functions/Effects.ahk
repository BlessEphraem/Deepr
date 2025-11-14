#Requires AutoHotkey v2.0

class Effects {
    static Search(Input) {
        Panel.Focus("Effects")
        Sleep(150)
        SendInput KS_Premiere.SearchBox
        Sleep(150)
        SendText Input
    }
}