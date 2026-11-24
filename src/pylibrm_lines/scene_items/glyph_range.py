class GlyphRangeItem:
    def __init__(
        self,
        start: int | None,
        length: int | None,
        color: int,
        argb_color: tuple[int, int, int] | None,
        text: str,
        rects: list[tuple[float, float, float, float]],
    ):
        self.start = start
        self.length = length
        self.color = color
        self.argb_color = argb_color
        self.text = text
        self.rects = rects

    # noinspection PyTypeChecker
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            start=data.get("start"),
            length=data.get("length"),
            color=data.get("color"),
            argb_color=tuple(data["argbColor"]) if data["argbColor"] else None,
            text=data.get("text", ""),
            rects=[
                (rect["x"], rect["y"], rect["w"], rect["h"])
                for rect in data.get("rects", [])
            ],
        )
