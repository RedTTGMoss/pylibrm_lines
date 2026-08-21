"""
A list of all the pen IDs based on the lines format.
Note that some of these pens have two versions,
ones which represent the old pen or v1 and ones which represent the new pen on newer firmware or v2.

NOTE: This file should be kept up to date if new pens are to be added to the format ;)
"""

PEN_BALLPOINT = -1
PEN_BALLPOINT_V1 = 2
PEN_BALLPOINT_V2 = 15
PEN_CALLIGRAPHY = 21
PEN_ERASER = 6
PEN_ERASER_AREA = 8
PEN_FINELINER = -2
PEN_FINELINER_V1 = 4
PEN_FINELINER_V2 = 17
PEN_HIGHLIGHTER = -3
PEN_HIGHLIGHTER_V1 = 5
PEN_HIGHLIGHTER_V2 = 18
PEN_MARKER = -4
PEN_MARKER_V1 = 3
PEN_MARKER_V2 = 16
PEN_MECHANICAL_PENCIL = -5
PEN_MECHANICAL_PENCIL_V1 = 7
PEN_MECHANICAL_PENCIL_V2 = 13
PEN_PAINTBRUSH = -6
PEN_PAINTBRUSH_V1 = 0
PEN_PAINTBRUSH_V2 = 12
PEN_PENCIL = -7
PEN_PENCIL_V1 = 1
PEN_PENCIL_V2 = 14
PEN_SHADER = 23

PEN_COMBINED_VERSIONS = {
    PEN_BALLPOINT: (PEN_BALLPOINT_V1, PEN_BALLPOINT_V2),
    PEN_FINELINER: (PEN_FINELINER_V1, PEN_FINELINER_V2),
    PEN_HIGHLIGHTER: (PEN_HIGHLIGHTER_V1, PEN_HIGHLIGHTER_V2),
    PEN_MARKER: (PEN_MARKER_V1, PEN_MARKER_V2),
    PEN_MECHANICAL_PENCIL: (PEN_MECHANICAL_PENCIL_V1, PEN_MECHANICAL_PENCIL_V2),
    PEN_PAINTBRUSH: (PEN_PAINTBRUSH_V1, PEN_PAINTBRUSH_V2),
    PEN_PENCIL: (PEN_PENCIL_V1, PEN_PENCIL_V2),
}

PEN_REPRESENTATIONS = {
        PEN_BALLPOINT: "Ballpoint Pen",
        PEN_BALLPOINT_V1: "Ballpoint Pen v1",
        PEN_BALLPOINT_V2: "Ballpoint Pen v2",
        PEN_CALLIGRAPHY: "Calligraphy Pen",
        PEN_ERASER: "Eraser",
        PEN_ERASER_AREA: "Eraser Area",
        PEN_FINELINER: "Fineliner",
        PEN_FINELINER_V1: "Fineliner v1",
        PEN_FINELINER_V2: "Fineliner v2",
        PEN_HIGHLIGHTER: "Highlighter",
        PEN_HIGHLIGHTER_V1: "Highlighter v1",
        PEN_HIGHLIGHTER_V2: "Highlighter v2",
        PEN_MARKER: "Marker",
        PEN_MARKER_V1: "Marker v1",
        PEN_MARKER_V2: "Marker v2",
        PEN_MECHANICAL_PENCIL: "Mechanical Pencil",
        PEN_MECHANICAL_PENCIL_V1: "Mechanical Pencil v1",
        PEN_MECHANICAL_PENCIL_V2: "Mechanical Pencil v2",
        PEN_PAINTBRUSH: "Paint Brush",
        PEN_PAINTBRUSH_V1: "Paint Brush v1",
        PEN_PAINTBRUSH_V2: "Paint Brush v2",
        PEN_PENCIL: "Pencil",
        PEN_PENCIL_V1: "Pencil v1",
        PEN_PENCIL_V2: "Pencil v2",
        PEN_SHADER: "Shader"
    }

ALL_PEN_IDS = [pen for pen in PEN_REPRESENTATIONS.keys() if pen not in PEN_COMBINED_VERSIONS.keys()]

def get_pen_repr(pen_id: int) -> str:
    return PEN_REPRESENTATIONS.get(pen_id, "Unknown Pen")

def is_valid_pen(pen_id: int) -> bool:
    return pen_id in PEN_REPRESENTATIONS
