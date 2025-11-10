#Requires AutoHotkey v2.0

TrueCtrlBackspace() {
    SendInput "^+{Left}"
    sleep 50
    SendInput "{Backspace}"

}