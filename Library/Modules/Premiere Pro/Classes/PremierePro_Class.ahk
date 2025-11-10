; Custom Class made for hotkeys in Premiere Pro.
; All hotkeys that you use in Premiere Pro, must be assigned there.

class KS_Premiere {

    static Excalibur := "^{Space}"
    
    static SelectPanel := {
        EffectControls: "{F2}",
        Properties: "{F3}",
        Bin: "{F1}",
        Effects: "{F4}",
        Player: '{F7}',
        Timeline: "{F8}",
        NextPanel: "^+{$}",
        PrevPanel: "^+{^}"
    }

    static Keyframe := {
        Prev: "{Numpad4}", 
        Next: "{Numpad6}",
            ;Need to be something else than an arrow key, dunno why, but when you are in "transform" mode
            ;and if you presse "left", it will move the layer 1 pixel left. It will not go back one frame.
            MorePrev: "+{NumpadLeft}",
            MoreNext:"+{NumpadRight}",

        Perform: {
            Video: "{Numpad8}",
            Audio: "{Numpad5}",
        },
            
        SelPrev: "{Numpad7}",
        SelNext: "{Numpad9}",

        Move:{
            Video: {
                Back: { 1:"!{Numpad7}", 10:"!+{Numpad7}" },
                Forw: { 1:"!{Numpad9}", 10:"!+{Numpad9}" },
            },
            Audio: {
                Back: { 1:"!{Numpad1}", 10:"!+{Numpad1}" },
                Forw: { 1:"!{Numpad3}", 10:"!+{Numpad3}" },
            },
        },

        MoveAudioForward: "^+{Right}",
        MoveAudioBackward: "^+{Left}",

    }

    static Clip := {
        Prev: "{Down}",
        Next:"{Up}",
        VolumeDown: "{PgDn}",
        VolumeUP: "{PgUp}",
        Rename: '{Backspace}',
    }

    static Bin := {
        Rename: "{Backspace}"
    }

    static Player := {
        Fit: "{²}",
        Fit100: "^+!{²}",
        Transform: "^{t}",
        ShowGuides: "+{r}",
        ShowRulers: "^{r}",
        ShowMargins: "^+{r}",
        ShowOverlay: "^+{o}"
    }

    static Tool := {
        Razor: "{z}",
        Normal: "{v}",
        Hand: "{h}",
        Text: "{t}",
        Slip: "{f}",
        Slide: "{g}"
    }

    static Timeline := { 
        ZoomComp: "^+{)}",       
        ZoomOut: '{)}',
        ZoomIn: "{=}",
        ZoomFrame: "^+{=}",  
        Cut: "{s}",       
        Selection_Follow_Playhead: '{*}',
    }

    class Markers {
        static Add := {
            Yellow: '^{,}',
            Red: "{,}",
        }
        static Next := "{:}"
        static Previous := "{;}"
    }

    class AltMenu {
        class Edit {
            static Prefix := "!{e}"
            static Label := this.Prefix "{l}"
        }
    }

    class ShowProperties {
        static All := "{o}"
        static Edited := "{u}"
    }

    static CompSettings := "^{k}"
    static MaximizePanel := "^+{*}"

    static Play := "{space}"

    static Save := "^{s}"
    static SaveAs := "^+{s}"
    static SaveAsCopy := "^!{s}"

    static AfterComposition := "^!+{m}"

    static Unselect := "^+{D}"
        
    static SearchBox := "^{f}"
    static DeselectAll := "^+{D}"

    static SendToAE := "^!+{m}"
    static GlobalFXMute := "{NumpadAdd}"
    static EffectSettings_SavePreset:= "^!+{P}"
    static Nesting := "{Enter}"
    static RippleDelete := "+{Delete}"
    static AddEdit := "{S}"
    static Enable := "{e}"
    static PlayheadToMouse := "{<}"
    static AudioGain := "{y}"
    
    static Volume := {
        Up: "^{PgUp}",
        Down: "^{PgDn}"
    }

    static Attributes := {
        Add: "^{!}",
        Sub: "!{!}"
        ; "ALT" + "!"
    }

    static Plugins := {
        Excal: "^{Space}"
    }

}
