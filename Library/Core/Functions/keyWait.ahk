#Requires AutoHotkey v2.0

MyKeyWait(WhichKey) {
    loop {
        if GetKeyState(WhichKey, "P")
            break
        else if GetKeyState("Esc", "P")
            Exit
        else
            continue
    }
}