
from pylibrm_lines.scene_items.point import PointItem


class LineItem:
    def __init__(
        self,
        tool: int,
        color: int,
        thickness_scale: float,
        stating_length: float,
        item_id: str,
        move_id: str | None,
        argb_color: tuple[int, int, int] | None,
        points: list[PointItem],
    ):
        self.tool = tool
        self.color = color
        self.thickness_scale = thickness_scale
        self.stating_length = stating_length
        self.item_id = item_id
        self.move_id = move_id
        self.points = points

        self._calc = {}

    # noinspection PyTypeChecker
    @classmethod
    def from_dict(cls, data: dict):
        item = cls(
            tool=data.get("tool"),
            color=data.get("color"),
            thickness_scale=data.get("thicknessScale"),
            stating_length=data.get("statingLength"),
            item_id=data.get("itemId"),
            move_id=data.get("moveId", None),
            argb_color=tuple(data["argbColor"]) if data["argbColor"] else None,
            points=[PointItem.from_dict(p) for p in data.get("points", [])],
        )
        for key, value in data.items():
            if key.startswith("_calc_"):
                item._calc[key[6:]] = value

        return item

    @property
    def calc(self):
        """
        A list of additional values from the stroker,
        To get these values, the config option `stroker_data_in_json` must be enabled.
        Refresh the layer data to get the latest values.
        """
        if not self._calc:
            raise ValueError(
                "No calculation data available. Ensure 'stroker_data_in_json' is enabled and the layer data is refreshed."
            )
        return self._calc
