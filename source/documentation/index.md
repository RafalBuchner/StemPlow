# Stem Plow Help



![StemPlow-icon](https://raw.githubusercontent.com/RafalBuchner/StemPlow/master/images/StemPlow-icon.png)

Tool for measuring the thickness of the stem.

You can edit its shortcut, behaviour and appearance by going to
`Extensions > Stem Plow > Settings…`.

## Settings entries

### _against Components_
> NOT IMPLEMENTED (YET)

When checked, Stem Plow will consider components of active glyph.

### _against SideBearings_

When checked, Stem Plow will consider the side bearings of the active glyph measurements.

### _display Named Values from Laser Measure_

If your ufo file contains Named Values defined by [Laser Measure](https://github.com/typesupply/lasermeasure/) Extension, Stem Plow will show them when measuring.

### *always*

> aka `Measure always` mode

It enables `measure always` mode, which allows you to see the ruler all the time (unless you hide it with the trigger key).

### _Trigger behaviour: anchor guide to the outline_

>  aka `anchor` mode

Enables `anchor` mode, which allows the user to "glue" the StemPlow ruler to the outline of the currently edited glyph. To move the ruler, you need to hold the trigger button (defined by `Trigger Character`). Let off the trigger button if you want to anchor it to the path.

### *Trigger Character*

Keyboard key that triggers the StemPlow. It works differently in different modes:

1. `Measure always` and  `anchor` modes are **off**: Shows Stem Plow when holding the trigger key. Otherwise, the ruler is not visible.
2. `Measure always` mode is **on**, and `anchor` mode is **off**: Trigger key toggles the visibility of the ruler.
3. `Measure always` and `anchor` modes are **on**: The ruler is movable when holding the trigger key. Otherwise, the guide sticks to the outline.

### *Text Size and Text Color*:

The visual parameters of the text shown on the measurement lines and named values.

### *Oval Size*

Size value of the dots on the tips of the measurement line.

### *Line Size*

Measurement line's width.

### *Base, Line, Oval Colors*

Those are self-explanatory.



![animation](https://raw.githubusercontent.com/RafalBuchner/StemPlow/master/images/animation.gif)

---

I've learned a lot about Subscribers and Merz while making this version of StemPlow. I wouldn't be able to do it if not for @typesupply's  laser measure extension [`Laser Measure`](https://github.com/typesupply/lasermeasure/) extension. I've based a lot of math on awesome [`Primer on Bézier curves`](https://pomax.github.io/bezierinfo/).
