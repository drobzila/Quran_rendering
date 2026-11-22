from __future__ import annotations
import numpy as np
from manim import *
from .config import FONT_NAME, STYLE_PRESETS

def build_background(style=None):
    style = style or STYLE_PRESETS["green"]
    h, w = config.pixel_height, config.pixel_width
    top = np.array(color_to_rgb(style["top"]), dtype=np.float32) * 255
    bottom = np.array(color_to_rgb(style["bottom"]), dtype=np.float32) * 255
    blend = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None, None]
    rows = top[None, None, :] * (1.0 - blend) + bottom[None, None, :] * blend
    rgb = np.broadcast_to(rows, (h, w, 3)).astype(np.uint8).copy()
    return ImageMobject(rgb).set(height=config.frame_height, width=config.frame_width)

def decorative_motif(style=None, motif_key=None):
    style = style or STYLE_PRESETS["green"]; motif_key = motif_key or "rosette"
    if motif_key == "rosette":
        petals = VGroup(*[Circle(radius=.78).move_to(.78*np.array([np.cos(TAU*i/8),np.sin(TAU*i/8),0])) for i in range(8)])
        motif = VGroup(Circle(radius=.82), petals, Circle(radius=1.62), Circle(radius=1.78))
    elif motif_key == "eight_point_star":
        motif = VGroup(RegularPolygon(n=8).scale(1.75), Square(side_length=2.45).rotate(PI/4), Square(side_length=2.45), Circle(radius=.58))
    elif motif_key == "nested_medallion":
        motif = VGroup(Circle(radius=1.8), Circle(radius=1.55), RegularPolygon(n=12).scale(1.35), RegularPolygon(n=6).scale(.95), RegularPolygon(n=6).scale(.62).rotate(PI/6))
    elif motif_key == "diamond_lattice":
        diamonds = VGroup(*[Square(side_length=.78).rotate(PI/4).move_to([x,y,0]) for x in (-1.05,0,1.05) for y in (-1.05,0,1.05)])
        motif = VGroup(diamonds, Square(side_length=3.25).rotate(PI/4))
    elif motif_key == "flower":
        petals = VGroup(*[Ellipse(width=.72,height=1.35).move_to(.68*np.array([np.cos(TAU*i/8),np.sin(TAU*i/8),0])).rotate(TAU*i/8) for i in range(8)])
        motif = VGroup(petals, Circle(radius=.42), Circle(radius=1.55))
    else:
        arches = VGroup(*[Arc(radius=r,start_angle=0,angle=PI,arc_center=ORIGIN).shift(DOWN*.15) for r in (.75,1.05,1.35,1.65)])
        motif = VGroup(arches, Line(LEFT*1.7,RIGHT*1.7).shift(DOWN*.15))
    motif.set_color(style["accent"]).set_stroke(width=2).set_opacity(.19).set(width=4.15).move_to(ORIGIN)
    motif.add_updater(lambda mob, dt: mob.rotate(TAU*.05*dt))
    return motif

def decorative_divider(width=2.0):
    return Line(LEFT*(width/2), RIGHT*(width/2), stroke_color=GOLD, stroke_width=1.5)

def ayah_number_circle(number: str) -> VGroup:
    circle = Circle(radius=.35, color=GOLD, stroke_width=3)
    label = Text(number, font=FONT_NAME, font_size=28, color=GOLD).move_to(circle.get_center())
    return VGroup(circle, label)

def progress_bar(total_width=None, y=None):
    total_width = total_width or config.frame_width-.4
    y = y if y is not None else -(config.frame_height/2-.5)
    track = Line(LEFT*(total_width/2),RIGHT*(total_width/2),stroke_color=GRAY_E,stroke_width=6)
    return track.move_to([0,y,0])

def corner_ornament(x: float, y: float, flip_x: float, flip_y: float) -> VGroup:
    gold = "#b89a55"
    horizontal = Line(ORIGIN,RIGHT*1.0,color=gold,stroke_width=1.2).move_to([x+flip_x*.5,y,0])
    vertical = Line(ORIGIN,DOWN*1.0,color=gold,stroke_width=1.2).move_to([x,y-flip_y*.5,0])
    diamond = Square(side_length=.2,color=gold,stroke_width=1.1,fill_opacity=0).rotate(PI/4).move_to([x+flip_x*.22,y-flip_y*.22,0])
    dot = Dot([x+flip_x*.58,y-flip_y*.58,0],radius=.025,color=gold)
    return VGroup(horizontal,vertical,diamond,dot).set_opacity(.58)
\n\ndef decorative_frame(style=None):\n    """Subtle ornamental frame and corner flourishes for vertical video."""\n    style = style or STYLE_PRESETS["green"]\n    color = style["gold"]\n    w, h = config.frame_width, config.frame_height\n    margin = 0.28\n    inset = 0.18\n    frame = VGroup()\n    frame.add(Rectangle(width=w-2*margin, height=h-2*margin, stroke_color=color, stroke_width=1.4, fill_opacity=0))\n    frame.add(Rectangle(width=w-2*(margin+inset), height=h-2*(margin+inset), stroke_color=color, stroke_width=0.55, fill_opacity=0).set_opacity(0.65))\n    for x in (-w/2+margin+0.08, w/2-margin-0.08):\n        for y in (-h/2+margin+0.08, h/2-margin-0.08):\n            ornament = Square(side_length=0.23, stroke_color=color, stroke_width=1.4, fill_opacity=0).rotate(PI/4).move_to([x,y,0])\n            dot = Dot([x,y,0], radius=0.035, color=color)\n            frame.add(ornament, dot)\n    return frame.set_opacity(0.75)\n