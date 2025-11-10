#Requires AutoHotkey v2.0

Class Attributes {

    static Sel(WhichAttributes) {

        CoordMode("pixel", "Window")
        CoordMode("mouse", "Window")
        CoordMode("caret", "Window")

        BlockInput("MouseMove")
        MouseGetPos &xpos, &ypos

        SendInput(KS_Premiere.SelectPanel.Timeline)
        ;for reseting selection

        SendInput(KS_Premiere.SelectPanel.EffectSettings)
        SendInput("{tab}")
        sleep(33)
        SendInput("{Tab " WhichAttributes "}")

        CaretGetPos(&A_Caretx, &A_CaretY)

        sleep 200

        if (A_CaretX = "") {
            checking := 0
            Loop
                {
                    checking++
                    Sleep 33
                    Tooltip "Counter = (" checking " * 33)`nCaret = " A_CaretX
                    if CaretGetPos(&A_CaretX, &A_CaretY) {
                        tooltip "CARET FOUND AT X" A_CaretX " AND " A_CaretY
                        break
                    }
                    if checking > 40 {
                        checking := 0
                        tooltip "FAIL, CARET NOT FOUND"
                        tooltip
                        sleep 20
                        BlockInput("MouseMoveOff")
                        Exit
                    }
                }
        }
        sleep 33
        tooltip
        
        MouseMove A_CaretX, A_CaretY, 0
        sleep 1
        SendInput "{Escape}"
        sleep 1 
        SendInput "{LButton Down}"
        BlockInput("MouseMoveOff")

        Keywait "Enter", "D"
        MouseMove xpos, ypos, 0

        sleep 500
        return
    }

    static Motion := {
        PosX: 1,
        PosY: 2,
        Scale: 3,
        Rot: 5
    }
}