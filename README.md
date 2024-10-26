# StemPlow

![StemPlow-icon](images/StemPlow-icon.png)

Tool for measuring the thickness of the stem. You can activate it by pressing `f` in the glyph edit window.

You can edit its shortcut, behaviour and appearance by going to
`Extensions > ↔ Stem Plow Settings`.

![animation](images/animation.gif)

> ## Version log:
>
> - version 1.220
>
>   - `measure always` now can be triggered On/Off with trigger key (works when `anchor guide to the outline` is off)
>   - some bug fixes that hopefully will work ([github issue report](https://github.com/RafalBuchner/StemPlow/issues/4#issue-1840248227))
>
> - version 1.212
>
>   - `measure always` an option, which allows you to see the StemPlow all the time
>   - Anchoring System ( in order to turn it on check `anchor guide to the outline` in the settings, while `measure always` is on as well )
>     > when this option is turned on as well as `measure always`, use your shortcut to anchor and unanchor StemPlow to your outlines. The ruler should stick to your shape.
>   - displaying Named Values defined with [`Laser Measure extension`](https://github.com/typesupply/lasermeasure/) by @typesupply
>   - a tiny bit rounder corners for measurement text boxes
>   - floating point in text boxes now depends on GlyphEditor's scale. The more you scale, the more digits after the floating point will appear
>
> - version 1.2
>   - update to Merz
>   - changing it behaviour from "tool" to "preview on hotkey"
>   - adding nice settings window
>   - making it a public version

---

I've learned a lot about Subscribers and Merz while making this version of StemPlow. I wouldn't be able to do it, if not for @typesupply's laser measure extension [`Laser Measure`](https://github.com/typesupply/lasermeasure/) extension. I've based a lot of math on awesome [`Primer on Bézier curves`](https://pomax.github.io/bezierinfo/).
