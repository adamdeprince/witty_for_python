# Painting & Geometry

> WPainter (the 2D drawing surface), the geometry value types it consumes, the pen/brush/font/gradient palette, and the paint device backends (SVG, PNG-on-canvas, PDF, measure-only).

**Classes in this section:**

- [`LengthUnit`](#LengthUnit)
- [`WLength`](#WLength)
- [`AnimationEffect`](#AnimationEffect)
- [`TimingFunction`](#TimingFunction)
- [`WAnimation`](#WAnimation)
- [`WPointF`](#WPointF)
- [`WRectF`](#WRectF)
- [`WLineF`](#WLineF)
- [`WTransform`](#WTransform)
- [`FontFamily`](#FontFamily)
- [`FontStyle`](#FontStyle)
- [`FontVariant`](#FontVariant)
- [`FontWeight`](#FontWeight)
- [`FontSize`](#FontSize)
- [`WFont`](#WFont)
- [`GradientStyle`](#GradientStyle)
- [`WGradient`](#WGradient)
- [`WShadow`](#WShadow)
- [`BorderStyle`](#BorderStyle)
- [`BorderWidth`](#BorderWidth)
- [`WBorder`](#WBorder)
- [`PenStyle`](#PenStyle)
- [`PenCapStyle`](#PenCapStyle)
- [`PenJoinStyle`](#PenJoinStyle)
- [`WPen`](#WPen)
- [`BrushStyle`](#BrushStyle)
- [`WBrush`](#WBrush)
- [`WPainterPath`](#WPainterPath)
- [`PainterImage`](#PainterImage)
- [`WPainter`](#WPainter)
- [`WPaintedWidget`](#WPaintedWidget)
- [`RenderMethod`](#RenderMethod)
- [`WAbstractArea`](#WAbstractArea)
- [`WCircleArea`](#WCircleArea)
- [`WRectArea`](#WRectArea)
- [`WPolygonArea`](#WPolygonArea)
- [`PaintDeviceFeatureFlag`](#PaintDeviceFeatureFlag)
- [`WPaintDevice`](#WPaintDevice)
- [`WVectorImage`](#WVectorImage)
- [`WSvgImage`](#WSvgImage)
- [`WCanvasPaintDevice`](#WCanvasPaintDevice)
- [`WMeasurePaintDevice`](#WMeasurePaintDevice)
- [`WPdfImage`](#WPdfImage)

---

### LengthUnit {#LengthUnit}

*Inherits:* `enum.Enum`

### WLength {#WLength}

A CSS length — a numeric value paired with a LengthUnit, or the
special `'auto'` placeholder. Used everywhere Wt accepts a width,
height, margin, or column dimension. Most APIs that take a length
also accept a bare float (interpreted as pixels); reach for
WLength when you need a non-pixel unit.

    panel.set_width(wt.WLength(50, wt.LengthUnit.Percentage))
    margin = wt.WLength('1.5em')           # parsed CSS

**Constructors**

- `__init__(self) -> None`
  Default-construct as 'auto' (no explicit length).

- `__init__(self, value: float, unit: LengthUnit = LengthUnit.Pixel) -> None`
  Construct from a numeric value and a unit (defaults to
  pixels).

- `__init__(self, css_text: str) -> None`
  Parse a CSS length string — e.g. 'auto', '50%', '12px', '1em'.

**Properties**

- `is_auto: bool` *(read-only)*
  True if this is the `'auto'` (default-constructed) length.

- `value: float` *(read-only)*
  The numeric component — pair with `unit` to interpret.

- `unit: LengthUnit` *(read-only)*
  The LengthUnit that scales `value`.

**Methods**

- `to_css_text(self) -> str`
  Render as a CSS string Wt's renderer can use.

- `to_pixels(self, font_size: float = 16.0) -> float`
  Convert to pixels assuming the given root font size (for em/ex/percentage resolution).

**Dunder methods**

- `__repr__(self) -> str`

### AnimationEffect {#AnimationEffect}

*Inherits:* `enum.IntEnum`

### TimingFunction {#TimingFunction}

*Inherits:* `enum.Enum`

### WAnimation {#WAnimation}

Describes a show / hide transition. Pass to WWidget.animate_show
and animate_hide (or use as the second arg to a setHidden overload
for animated visibility changes). An empty WAnimation means 'no
transition'; otherwise pick an AnimationEffect, optionally a
TimingFunction, and a duration in milliseconds.

    panel.animate_show(wt.WAnimation(
        wt.AnimationEffect.SlideInFromBottom,
        wt.TimingFunction.EaseOut, 300))

Effects can be OR'd together (`SlideInFromLeft | Fade`) to
combine motion with a fade.

**Constructors**

- `__init__(self) -> None`
  Default — an empty animation (no transition).

- `__init__(self, effects: int, timing: TimingFunction = TimingFunction.Linear, duration_ms: int = 250) -> None`
  Construct from an effect (or `e1 | e2` to combine a slide with Fade). Timing and duration default to Linear / 250ms.

**Properties**

- `duration: int` *(read/write)*
  Length of the animation in milliseconds.

- `timing_function: TimingFunction` *(read/write)*
  The TimingFunction (easing curve) the animation uses.

- `empty: bool` *(read-only)*
  True for the default (no-effect) animation.

### WPointF {#WPointF}

A point in 2-D space with floating-point coordinates. Used by
WPainter for paths and polygons; mutable so you can mutate x/y
in place.

**Constructors**

- `__init__(self) -> None`
  Construct the origin (0, 0).

- `__init__(self, x: float, y: float) -> None`
  Construct the point (x, y).

**Properties**

- `x: float` *(read/write)*
  Horizontal coordinate.

- `y: float` *(read/write)*
  Vertical coordinate.

**Dunder methods**

- `__repr__(self) -> str`

### WRectF {#WRectF}

Axis-aligned rectangle with floating-point coordinates. Used as
a parameter to WPainter draw / clip methods and as the result
type of bounding-box queries.

**Constructors**

- `__init__(self) -> None`
  Construct a degenerate rectangle at the origin with zero size.

- `__init__(self, x: float, y: float, width: float, height: float) -> None`
  Construct a rectangle whose top-left corner is at (x, y) and with the given size.

**Properties**

- `x: float` *(read/write)*
  Top-left X coordinate.

- `y: float` *(read/write)*
  Top-left Y coordinate.

- `width: float` *(read/write)*
  Rectangle width.

- `height: float` *(read/write)*
  Rectangle height.

- `is_null: bool` *(read-only)*
  True when the rectangle is the default-constructed null value (distinct from a present-but-empty rect).

- `is_empty: bool` *(read-only)*
  True when width or height is zero (or negative).

- `left: float` *(read-only)*
  Left edge (same as `x`).

- `top: float` *(read-only)*
  Top edge (same as `y`).

**Dunder methods**

- `__repr__(self) -> str`

### WLineF {#WLineF}

A line segment between two points. Used in bulk-line draws (`WPainter.draw_lines`).

**Constructors**

- `__init__(self) -> None`
  Construct a zero-length line at the origin.

- `__init__(self, x1: float, y1: float, x2: float, y2: float) -> None`
  Construct a line from (x1, y1) to (x2, y2).

**Properties**

- `x1: float` *(read-only)*
  X coordinate of the start point.

- `y1: float` *(read-only)*
  Y coordinate of the start point.

- `x2: float` *(read-only)*
  X coordinate of the end point.

- `y2: float` *(read-only)*
  Y coordinate of the end point.

- `p1: WPointF` *(read-only)*
  Start point as a WPointF.

- `p2: WPointF` *(read-only)*
  End point as a WPointF.

### WTransform {#WTransform}

Affine 2-D transform as a 2x3 matrix (m11, m12, m21, m22, dx,
dy). Applied to coordinates by WPainter operations after
`set_world_transform`. Use `WPainter.translate / rotate / scale`
for the common cases — construct a WTransform directly only
when you need a combined or pre-computed matrix.

**Constructors**

- `__init__(self) -> None`
  Identity transform.

**Properties**

- `is_identity: bool` *(read-only)*
  True when this transform leaves coordinates unchanged.

- `m11: float` *(read-only)*
  Row 1, column 1 of the matrix (X scale).

- `m12: float` *(read-only)*
  Row 1, column 2 of the matrix (Y shear into X).

- `m21: float` *(read-only)*
  Row 2, column 1 of the matrix (X shear into Y).

- `m22: float` *(read-only)*
  Row 2, column 2 of the matrix (Y scale).

- `dx: float` *(read-only)*
  X translation component.

- `dy: float` *(read-only)*
  Y translation component.

- `determinant: float` *(read-only)*
  Matrix determinant — non-zero iff the transform is invertible.

**Methods**

- `reset(self) -> None`
  Restore the identity transform.

- `adjoint(self) -> WTransform`
  Return the adjoint (transposed cofactor) matrix. Useful when computing inverses manually.

- `map_point(self, x: float, y: float) -> tuple`
  Apply the transform to (x, y) and return (tx, ty).

### FontFamily {#FontFamily}

*Inherits:* `enum.Enum`

Generic font-family categories. Maps to the CSS generic family of the same name. Combine with `WFont.set_family`'s specific argument to nominate concrete font names.

### FontStyle {#FontStyle}

*Inherits:* `enum.Enum`

CSS `font-style` value — upright, italic, or oblique.

### FontVariant {#FontVariant}

*Inherits:* `enum.Enum`

CSS `font-variant` value. SmallCaps renders lowercase as smaller uppercase glyphs.

### FontWeight {#FontWeight}

*Inherits:* `enum.Enum`

CSS `font-weight` value. Pick a preset; Value means an explicit numeric weight is supplied to `WFont.set_weight`.

### FontSize {#FontSize}

*Inherits:* `enum.Enum`

CSS `font-size` keyword sizes. Use FixedSize together with `WFont.set_size(WLength)` for an explicit numeric size.

### WFont {#WFont}

Font specification used by WPainter.draw_text and by widget decoration APIs. Holds family, style, variant, weight, and size — what CSS would call the `font` shorthand.

**Constructors**

- `__init__(self) -> None`
  Construct a default-family font at the browser's default size.

- `__init__(self, family: FontFamily) -> None`
  Construct with the given generic family.

**Methods**

- `set_family(self, family: FontFamily, specific_families: str = '') -> None`
  Generic family + optional comma-separated specific font names (e.g. setFamily(Monospace, "'Courier New'")).

- `set_style(self, style: FontStyle) -> None`
  Set the FontStyle (normal / italic / oblique).

- `set_variant(self, variant: FontVariant) -> None`
  Set the FontVariant (normal or small caps).

- `set_weight(self, weight: FontWeight, value: int = 400) -> None`
  When weight=Value, the second argument is the CSS numeric weight (100, 200, …, 900).

- `set_size(self, size: WLength) -> None`
  Size as a WLength — accepts a number (treated as pixels), a WLength('1.2em'), or a parsed CSS string.

- `size_length(self, medium_size: float = 16.0) -> WLength`
  Resolve the current size to a concrete WLength. Keyword sizes (Small, Large, …) are computed relative to `medium_size` pixels.

### GradientStyle {#GradientStyle}

*Inherits:* `enum.Enum`

Geometric form of a WGradient — straight axis (Linear) or concentric (Radial).

### WGradient {#WGradient}

Multi-stop colour gradient used as a pen stroke or brush fill.
Configure geometry first (`set_linear_gradient` or
`set_radial_gradient`), then add colour stops in order from 0.0
(start) to 1.0 (end).

    g = wt.WGradient()
    g.set_linear_gradient(0, 0, 100, 0)
    g.add_color_stop(0.0, wt.WColor('red'))
    g.add_color_stop(1.0, wt.WColor('yellow'))
    painter.set_brush(wt.WBrush(g))

**Constructors**

- `__init__(self) -> None`
  Construct an empty (no-geometry, no-stops) gradient.

**Properties**

- `style: GradientStyle` *(read-only)*
  Linear or Radial — set by the last set_* call.

- `is_empty: bool` *(read-only)*
  True when no colour stops have been added yet.

**Methods**

- `set_linear_gradient(self, x0: float, y0: float, x1: float, y1: float) -> None`
  Configure a linear gradient from (x0,y0) to (x1,y1).

- `set_radial_gradient(self, cx: float, cy: float, r: float, fx: float, fy: float) -> None`
  Configure a radial gradient: bounding circle centred at (cx,cy) with radius r, focal point at (fx,fy).

- `add_color_stop(self, position: float, color: WColor) -> None`
  Add a color stop at `position` (0.0 = start, 1.0 = end).

- `clear_color_stops(self) -> None`
  Remove every previously-added colour stop.

### WShadow {#WShadow}

Drop-shadow descriptor — offset, blur radius, and colour. Pass to `WPainter.set_shadow` to apply to subsequent draws; pass the default-constructed WShadow() to clear.

**Constructors**

- `__init__(self) -> None`
  Construct the no-shadow value.

- `__init__(self, dx: float, dy: float, color: WColor, blur: float) -> None`
  Construct a shadow offset by (dx, dy) in the painter's current coordinates, tinted `color`, with `blur` blur radius.

**Properties**

- `offset_x: float` *(read-only)*
  Horizontal shadow offset.

- `offset_y: float` *(read-only)*
  Vertical shadow offset.

- `color: WColor` *(read-only)*
  Shadow tint colour.

- `blur: float` *(read-only)*
  Blur radius.

- `none: bool` *(read-only)*
  True for the default (no-shadow) value.

**Methods**

- `set_offsets(self, dx: float, dy: float) -> None`
  Set the shadow's offset.

- `set_color(self, color: WColor) -> None`
  Set the shadow's tint colour.

- `set_blur(self, blur: float) -> None`
  Set the Gaussian blur radius.

### BorderStyle {#BorderStyle}

*Inherits:* `enum.Enum`

CSS `border-style` value. Mirrors the standard set of CSS borders — Solid for the common case, Dotted/Dashed for discontinuous strokes, Groove/Ridge/Inset/Outset for 3-D effects.

### BorderWidth {#BorderWidth}

*Inherits:* `enum.Enum`

CSS `border-width` keyword. Use Explicit together with the WLength-taking WBorder constructor for a numeric width.

### WBorder {#WBorder}

Value type describing a CSS border — style, width, and colour. Passed to widget decoration APIs (WCssDecorationStyle etc.).

**Constructors**

- `__init__(self) -> None`
  Construct the default (no border) value.

- `__init__(self, style: BorderStyle, width: BorderWidth, color: WColor) -> None`
  Construct from a style, a keyword width (Thin/Medium/Thick), and a colour.

- `__init__(self, style: BorderStyle, width: WLength, color: WColor) -> None`
  Explicit-width variant — `width` is a WLength rather than the Thin/Medium/Thick preset.

**Properties**

- `style: BorderStyle` *(read-only)*
  Current BorderStyle.

- `color: WColor` *(read-only)*
  Current border colour.

- `explicit_width: WLength` *(read-only)*
  Explicit width as a WLength (meaningful only when the border was constructed with the WLength-taking ctor).

**Methods**

- `set_style(self, style: BorderStyle) -> None`
  Change the border style.

- `set_color(self, color: WColor) -> None`
  Change the border colour.

### PenStyle {#PenStyle}

*Inherits:* `enum.Enum`

Stroke dash pattern. NoPen suppresses the stroke entirely (use for fill-only draws).

### PenCapStyle {#PenCapStyle}

*Inherits:* `enum.Enum`

Shape applied at the ends of stroked open paths — flush (FlatCap), squared off past the endpoint (SquareCap), or a semicircle (RoundCap).

### PenJoinStyle {#PenJoinStyle}

*Inherits:* `enum.Enum`

Shape applied where two stroked segments meet — sharp point (MiterJoin), flattened (BevelJoin), or rounded (RoundJoin).

### WPen {#WPen}

Stroke specification — colour or gradient, dash style, line cap, join style, and width. Assigned to a WPainter via `set_pen`; affects every subsequent stroke or outline.

**Constructors**

- `__init__(self) -> None`
  Construct a default black 1-px solid pen.

- `__init__(self, style: PenStyle) -> None`
  Construct a pen with the given dash style (and default colour and width).

- `__init__(self, color: WColor) -> None`
  Construct a solid pen of the given colour.

**Properties**

- `color: WColor` *(read-only)*
  Current stroke colour.

- `style: PenStyle` *(read-only)*
  Current dash pattern.

- `cap_style: PenCapStyle` *(read-only)*
  Current line-end cap style.

- `join_style: PenJoinStyle` *(read-only)*
  Current segment join style.

- `width: WLength` *(read-only)*
  Current stroke width as a WLength.

**Methods**

- `set_style(self, style: PenStyle) -> None`
  Set the dash pattern.

- `set_cap_style(self, style: PenCapStyle) -> None`
  Set the line-end cap style.

- `set_join_style(self, style: PenJoinStyle) -> None`
  Set the join style for connected segments.

- `set_width(self, width: WLength) -> None`
  Set stroke width (a WLength — number for pixels, or a WLength with explicit units).

- `set_color(self, color: WColor) -> None`
  Set the stroke colour.

- `set_gradient(self, gradient: WGradient) -> None`
  Use a gradient for the stroke instead of a solid color.

### BrushStyle {#BrushStyle}

*Inherits:* `enum.Enum`

Fill pattern for a WBrush. NoBrush leaves the interior unfilled; SolidPattern fills with a single colour; Gradient uses the brush's attached WGradient.

### WBrush {#WBrush}

Fill specification — a solid colour or a gradient. Assigned to a WPainter via `set_brush`; affects every subsequent filled shape (rectangle, ellipse, path, etc.).

**Constructors**

- `__init__(self) -> None`
  Construct the no-fill (NoBrush) value.

- `__init__(self, style: BrushStyle) -> None`
  Construct with the given style and default colour.

- `__init__(self, color: WColor) -> None`
  Construct a solid-colour brush.

- `__init__(self, gradient: WGradient) -> None`
  Construct a gradient-filled brush. style is set to Gradient.

**Properties**

- `color: WColor` *(read-only)*
  Current fill colour.

- `style: BrushStyle` *(read-only)*
  Current fill style.

**Methods**

- `set_style(self, style: BrushStyle) -> None`
  Switch fill style.

- `set_color(self, color: WColor) -> None`
  Set the solid fill colour (also switches to SolidPattern).

- `set_gradient(self, gradient: WGradient) -> None`
  Use a gradient for the fill. Sets style to Gradient.

### WPainterPath {#WPainterPath}

A geometric path built from straight lines, Bézier curves, and
arcs — the parametric input to `WPainter.draw_path` and
`WPainter.set_clip_path`. Build incrementally: move the pen,
draw segments, optionally close back to the start.

    path = wt.WPainterPath()
    path.move_to(10, 10)
    path.line_to(50, 10)
    path.cubic_to(80, 10, 80, 80, 50, 80)
    path.close_sub_path()
    painter.draw_path(path)

**Constructors**

- `__init__(self) -> None`
  Construct an empty path.

- `__init__(self, start: WPointF) -> None`
  Begin the path at the given start point.

**Properties**

- `is_empty: bool` *(read-only)*
  True when no segments have been added yet.

- `current_position: WPointF` *(read-only)*
  End point of the most recently added segment — the implicit starting point of the next `line_to` / `cubic_to` / `arc_to`.

**Methods**

- `close_sub_path(self) -> None`
  Close the current sub-path with a line back to its start.

- `move_to(self, x: float, y: float) -> None`
  Begin a new sub-path at (x, y) without drawing a connecting segment.

- `line_to(self, x: float, y: float) -> None`
  Append a straight line from the current position to (x, y).

- `cubic_to(self, c1x: float, c1y: float, c2x: float, c2y: float, end_x: float, end_y: float) -> None`
  Cubic Bézier from current position to (end_x, end_y) via control points (c1x, c1y) and (c2x, c2y).

- `arc_to(self, cx: float, cy: float, radius: float, start_angle: float, sweep_length: float) -> None`
  Arc of `radius` centred at (cx, cy); angles in degrees, 0° = 3 o'clock, sweeping counter-clockwise.

- `add_rect(self, x: float, y: float, width: float, height: float) -> None`
  Add an axis-aligned rectangle as a closed sub-path.

- `add_ellipse(self, x: float, y: float, width: float, height: float) -> None`
  Add an ellipse inscribed in the bounding rect as a closed sub-path.

### PainterImage {#PainterImage}

Value type describing an image that a WPainter can draw. Holds
the URL the browser will fetch and the intrinsic pixel size
needed for layout. Pass an instance to `WPainter.draw_image`;
also re-exported on the WPainter class as `WPainter.Image` for
the natural nested-class form.

**Constructors**

- `__init__(self, url: str, width: int, height: int) -> None`
  Reference an external image at `url` with explicit pixel dimensions.

- `__init__(self, url: str, file: str) -> None`
  Reference an image whose pixel dimensions Wt should read from local file `file` (the URL is what the browser uses; the file is where Wt looks for size metadata).

**Properties**

- `uri: str` *(read-only)*
  The URL the browser will load to render this image.

- `width: int` *(read-only)*
  Intrinsic image width in pixels.

- `height: int` *(read-only)*
  Intrinsic image height in pixels.

### WPainter {#WPainter}

2-D drawing context. Receives geometric draw commands and turns
them into output on a paint device — an HTML canvas, an SVG
document, a PDF page, etc. Modelled on the same verb surface as
Cairo or HTML5 Canvas: configure pen / brush / font, then call
draw_* methods.

    pdf = wt.WPdfImage(wt.WLength(595), wt.WLength(842))
    painter = wt.WPainter(pdf)
    painter.set_pen(wt.WPen(wt.WColor('black')))
    painter.draw_line(0, 0, 100, 100)
    painter.draw_text(10, 10, 200, 30, wt.AlignmentFlag.Left,
                      'Report')
    app.add_resource(pdf, '/report.pdf')

Inside a WPaintedWidget's paint callback the painter is handed
to you already bound to the right device — don't construct one.
The painter does NOT own its device; keep the device alive for
the painter's lifetime. Drop the painter (or let it go out of
scope) to flush any pending output to the device.

**Constructors**

- `__init__(self, device: WPaintDevice) -> None`
  Construct a painter bound to a paint device. The device is not owned; the painter borrows it for its lifetime.

- `__init__(self, device: WResource) -> None`
  Construct from a WResource that also implements WPaintDevice (WPdfImage / WSvgImage). Equivalent to passing the WPaintDevice view of the same object.

**Properties**

- `pen: WPen` *(read-only)*
  The current pen — what strokes use.

- `brush: WBrush` *(read-only)*
  The current brush — what fills use.

- `is_active: bool` *(read-only)*
  True if the painter is currently bound to a device and can accept draw calls.

**Methods**

- `save(self) -> None`
  Push the current state (pen, brush, font, transform, clipping) onto an internal stack. Pair with restore().

- `restore(self) -> None`
  Pop the most recently saved state, undoing any pen / brush / font / transform / clipping changes made since the matching save().

- `set_pen(self, pen: WPen) -> None`
  Set the stroke style for subsequent line / outline draws.

- `set_brush(self, brush: WBrush) -> None`
  Set the fill style for subsequent filled-shape draws.

- `set_font(self, font: WFont) -> None`
  Set the font used by draw_text.

- `set_shadow(self, shadow: WShadow) -> None`
  Apply a drop-shadow effect to subsequent draw operations. Pass `wt.WShadow()` to clear.

- `set_world_transform(self, transform: WTransform, combine: bool = False) -> None`
  Replace the painter's current transform with `transform`. Pass combine=True to multiply onto the existing transform instead of replacing it.

- `translate(self, dx: float, dy: float) -> None`
  Shift the origin of subsequent draws by (dx, dy).

- `rotate(self, angle: float) -> None`
  Rotate by `angle` degrees about the origin of the local coordinate system.

- `scale(self, sx: float, sy: float) -> None`
  Scale subsequent draws by sx in X and sy in Y. Pass sx=sy=-1 to flip about the origin.

- `set_clipping(self, enabled: bool) -> None`
  Enable or disable the active clip path. Use set_clip_path first to define the clip region.

- `set_clip_path(self, path: WPainterPath) -> None`
  Restrict subsequent draws to the area inside `path` (a WPainterPath). Does not enable clipping by itself — call set_clipping(True) too.

- `draw_line(self, x1: float, y1: float, x2: float, y2: float) -> None`
  Stroke a straight line from (x1, y1) to (x2, y2) using the current pen.

- `draw_rect(self, x: float, y: float, width: float, height: float) -> None`
  Stroke and fill an axis-aligned rectangle with the current pen and brush.

- `draw_ellipse(self, x: float, y: float, width: float, height: float) -> None`
  Ellipse inscribed in the given bounding rect.

- `draw_arc(self, x: float, y: float, width: float, height: float, start_angle: int, span_angle: int) -> None`
  Arc inscribed in the bounding rect, swept from start to start+span (in 1/16-degree units, Wt convention).

- `draw_pie(self, x: float, y: float, width: float, height: float, start_angle: int, span_angle: int) -> None`
  Pie slice — arc closed back to the centre. Angles in 1/16-degree units like draw_arc.

- `draw_chord(self, x: float, y: float, width: float, height: float, start_angle: int, span_angle: int) -> None`
  Chord — arc closed by a straight line between its endpoints (not the centre). Angles in 1/16-degree units.

- `draw_point(self, x: float, y: float) -> None`
  Draw a single point at (x, y) with the current pen.

- `draw_path(self, path: WPainterPath) -> None`
  Stroke and fill a WPainterPath using the current pen and brush.

- `draw_lines(self, lines: Sequence[WLineF]) -> None`
  Stroke each WLineF in `lines` with the current pen — one round-trip into the device, cheaper than many draw_line calls.

- `draw_text(self, x: float, y: float, width: float, height: float, alignment: int, text: str) -> None`
  Draw text into the rect. `alignment` is an OR of AlignmentFlag values (e.g. Center | Middle).

- `draw_image(self, point: WPointF, image: PainterImage) -> None`
  Draw the image at its intrinsic size with top-left at point.

- `draw_image(self, point: WPointF, image: PainterImage, source_rect: WRectF) -> None`
  Draw a sub-region of the image at its intrinsic size. source_rect is in the image's pixel coordinates.

- `draw_image(self, dest_rect: WRectF, image: PainterImage) -> None`
  Stretch / shrink the image to fill dest_rect.

- `draw_image(self, dest_rect: WRectF, image: PainterImage, source_rect: WRectF) -> None`
  Stretch a sub-region of the image into dest_rect.

### WPaintedWidget {#WPaintedWidget}

*Inherits:* `WInteractWidget`

A widget whose contents are produced by Python code running
against a WPainter. Pass a callable at construction; it will be
invoked each time the widget needs to repaint, with a freshly-
bound WPainter as its only argument.

    def paint(p):
        p.set_pen(wt.WPen(wt.WColor('navy')))
        p.draw_line(0, 0, 200, 100)
        p.draw_ellipse(20, 20, 60, 60)
    container.add_widget(wt.WPaintedWidget(paint))

Call `update()` to request a repaint after model changes. The
WPainter handed to the callback is a non-owning view of a
stack-allocated object — don't stash it beyond the callback's
return. The paint callback may run on a worker thread; the
binding acquires the GIL before calling into Python.

**Constructors**

- `__init__(self) -> None`
  Construct an empty painted widget with no paint callback. Set one later via `set_paint_callback` before calling `update()`.

- `__init__(self, paint: Callable) -> None`
  Construct with the paint callback. The callable takes a single WPainter argument — use its draw_* methods to render.

**Properties**

- `preferred_method: RenderMethod` *(read-only)*
  The currently selected render backend (RenderMethod enum).

**Methods**

- `set_paint_callback(self, paint: Callable) -> None`
  Replace the paint callback. The new callback will be used from the next paintEvent onward; call update() to force a redraw immediately.

- `update(self) -> None`
  Schedule a repaint. Wt batches paint events — the actual paintEvent fires after the current event loop tick.

- `set_preferred_method(self, method: RenderMethod) -> None`
  Render backend: InlineSvgVml, HtmlCanvas, or PngImage. HtmlCanvas is the default on modern browsers.

- `add_area(self, area: _T_Area) -> _T_Area`
  Attach an image-map area (WRectArea / WCircleArea / WPolygonArea) that becomes a clickable region on top of the painted output.

- `insert_area(self, index: int, area: _T_Area) -> _T_Area`
  Insert an image-map area at position `index`. Earlier areas in the list receive clicks first when regions overlap.

### RenderMethod {#RenderMethod}

*Inherits:* `enum.Enum`

Backend a WPaintedWidget uses to render. HtmlCanvas is the default; InlineSvgVml emits inline SVG (legacy IE: VML); PngImage rasterises server-side and serves a PNG.

### WAbstractArea {#WAbstractArea}

*Inherits:* `WObject`

Base class for clickable regions in an image map. Concrete
subclasses define the region's shape: WRectArea, WCircleArea,
WPolygonArea. Attach one to a WPaintedWidget or WImage via
`add_area` to make part of the rendered output respond to clicks.

**Properties**

- `hole: bool` *(read/write)*
  When True, this area is treated as a hole (transparent to clicks) cut out of the surrounding map.

- `transformable: bool` *(read/write)*
  When True, the area's coordinates are interpreted in the painter's local coordinate system and follow any transforms applied to the widget. When False, coordinates stay fixed in widget pixels.

**Methods**

- `set_link(self, link: WLink) -> None`
  Navigate to `link` when the area is clicked (WLink — URL, internal path, or WResource).

- `set_alternate_text(self, text: str) -> None`
  Text used by screen readers and shown when the underlying image fails to load.

- `set_tool_tip(self, text: str) -> None`
  Hover-tooltip text shown while the cursor is over this area.

- `set_style_class(self, style_class: str) -> None`
  CSS class for the underlying `<area>` element.

### WCircleArea {#WCircleArea}

*Inherits:* `WAbstractArea`

Circular clickable region for an image map. Coordinates are in the widget's pixel space (or local coordinates if `transformable` is True).

**Constructors**

- `__init__(self) -> None`
  Construct an empty circle area — set centre and radius afterwards.

- `__init__(self, x: int, y: int, radius: int) -> None`
  Construct a circle centred at (x, y) with the given radius.

**Properties**

- `center_x: int` *(read-only)*
  X coordinate of the circle's centre.

- `center_y: int` *(read-only)*
  Y coordinate of the circle's centre.

- `radius: int` *(read/write)*
  Circle radius in pixels (or local coordinate units).

**Methods**

- `set_center(self, x: int, y: int) -> None`
  Move the circle's centre to (x, y).

### WRectArea {#WRectArea}

*Inherits:* `WAbstractArea`

Rectangular clickable region for an image map.

**Constructors**

- `__init__(self) -> None`
  Construct a degenerate (zero-size) rectangle. Set bounds afterwards by reconstructing.

- `__init__(self, x: int, y: int, width: int, height: int) -> None`
  Construct an axis-aligned rectangle with top-left at (x, y).

- `__init__(self, rect: WRectF) -> None`
  Construct from an existing WRectF.

### WPolygonArea {#WPolygonArea}

*Inherits:* `WAbstractArea`

Polygon-shaped clickable region. Build by passing a list of vertices, or extend a polygon incrementally via `add_point`.

**Constructors**

- `__init__(self) -> None`
  Construct an empty polygon area — add vertices afterwards.

- `__init__(self, points: Sequence[WPointF]) -> None`
  Construct from a sequence of WPointF vertices.

**Methods**

- `add_point(self, x: float, y: float) -> None`
  Append a vertex at (x, y) to the polygon.

- `set_points(self, points: Sequence[WPointF]) -> None`
  Replace the polygon's vertices with `points`.

### PaintDeviceFeatureFlag {#PaintDeviceFeatureFlag}

*Inherits:* `enum.IntEnum`

Capability bits a paint device can advertise. Combined with OR into a bitmask. HasFontMetrics means the device can measure text without rendering it; CanWordWrap means it knows how to break long strings on word boundaries.

### WPaintDevice {#WPaintDevice}

Abstract base for everything a WPainter can draw into — an
HTML canvas, an SVG document, a PDF page, an off-screen
measurement device. Cannot be constructed directly; pick a
concrete subclass.

    pdf = wt.WPdfImage(wt.WLength(595), wt.WLength(842))
    painter = wt.WPainter(pdf)
    painter.draw_text(...)
    app.add_resource(pdf, '/page.pdf')

WResource-based devices (WSvgImage, WPdfImage) are typically
served to the browser by mounting on a URL; off-screen devices
(WMeasurePaintDevice, WCanvasPaintDevice) are used for sizing
or capture.

**Properties**

- `width: WLength` *(read-only)*
  Device width as a WLength.

- `height: WLength` *(read-only)*
  Device height as a WLength.

### WVectorImage {#WVectorImage}

*Inherits:* `WPaintDevice`

Base class for vector-graphics paint devices (WSvgImage today; a future VML implementation). Exposes no methods of its own — exists so callers can `isinstance(dev, wt.WVectorImage)` to test for the vector family.

### WSvgImage {#WSvgImage}

*Inherits:* `WResource`

SVG paint device backed by a WResource. Paint into it with a
WPainter, then mount the device on a URL via
`WApplication.add_resource` to serve the resulting SVG document
to clients (typically as the source of a WImage or a
`<link rel=icon>`).

    svg = wt.WSvgImage(wt.WLength(200), wt.WLength(100))
    p = wt.WPainter(svg)
    p.draw_ellipse(20, 20, 60, 60)
    del p  # flush
    app.add_resource(svg, '/badge.svg')
    container.add_widget(wt.WImage(wt.WLink('/badge.svg'), 'badge'))

Because WSvgImage is a WResource the same instance can be
served to many clients.

**Constructors**

- `__init__(self, width: WLength, height: WLength) -> None`
  Create an SVG paint surface of the given size. Construct a WPainter against it, paint, then mount the WSvgImage on a URL — clients fetch the SVG text.

### WCanvasPaintDevice {#WCanvasPaintDevice}

*Inherits:* `WPaintDevice`

HTML5-canvas paint device. The same backend a WPaintedWidget uses when its render method is HtmlCanvas. Construct one directly only for off-screen / capture scenarios; for normal drawing into the page, use WPaintedWidget.

**Constructors**

- `__init__(self, width: WLength, height: WLength) -> None`
  Create a canvas paint surface of the given size.

### WMeasurePaintDevice {#WMeasurePaintDevice}

*Inherits:* `WPaintDevice`

Pass-through paint device that records the bounding rect of
every draw operation without actually rendering. Useful for
sizing an output canvas before allocating the real device.

    measure = wt.WMeasurePaintDevice(reference_device)
    p = wt.WPainter(measure)
    render(p)               # whatever paint code
    rect = measure.bounding_rect

**Constructors**

- `__init__(self, delegate: WPaintDevice) -> None`
  Construct over an underlying device — `delegate` is consulted for font metrics but no rendering reaches it.

**Properties**

- `bounding_rect: WRectF` *(read-only)*
  Union of every WRectF that's been painted into the measure device so far.

### WPdfImage {#WPdfImage}

*Inherits:* `WResource`

PDF paint device backed by a WResource. Paint into it with a
WPainter, then mount it on a URL so clients can download or
view the resulting PDF.

    pdf = wt.WPdfImage(wt.WLength(595), wt.WLength(842))  # A4
    p = wt.WPainter(pdf)
    p.draw_text(36, 36, 523, 30, wt.AlignmentFlag.Left, 'Report')
    p.draw_rect(36, 80, 523, 200)
    del p  # flush
    app.add_resource(pdf, '/report.pdf')

Rendered by libharu. Only the 14 PDF base fonts are available
by default — call `add_font_collection` first if you need a
specific TrueType/Type1 font.

**Constructors**

- `__init__(self, width: WLength, height: WLength) -> None`
  Create a PDF paint surface with the given page dimensions (typically in WLength.Point units — A4 portrait is roughly 595×842 pt).

**Methods**

- `add_font_collection(self, directory: str, recursive: bool = True) -> None`
  Search `directory` for TrueType / Type1 fonts and make them available to drawText. Pair with WFont.set_family(..., specific='Some Font') to reference one. Without registered fonts the PDF uses libharu's built-in 14 base fonts only.
