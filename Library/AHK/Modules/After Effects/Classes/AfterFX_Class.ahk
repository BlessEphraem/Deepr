#Requires AutoHotkey v2.0

class KS_AfterFX {
    static CompSettings := "^{k}"
    static Nest := "^+{c}"

    static Timeline := {        
        UnZoom: '{)}',
        Zoom: '{=}',
        ZoomInFrame: '^+{=}',
        ToggleZoom: '^!{à}',

    }

    static Keyframe := {
        Prev: '^{Left}',
        Next: '^{Right}',
        MorePrev: '^+{Left}',
        MoreNext: '^+{Right}',
        SelNext: '!{Right}',
        SelPrev: '!{Left}'
    }

    static Player := {
        UnZoom: "^{)}",
        Zoom: "^{=}",
        Fit: "^{à}"
    }
}