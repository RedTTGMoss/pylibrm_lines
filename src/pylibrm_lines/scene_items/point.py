class PointItem:
    def __init__(self, x: float, y: float, speed: int, direction: int, width: int, pressure: int):
        self.x = x
        self.y = y
        self.speed = speed
        self.direction = direction
        self.width = width
        self.pressure = pressure
        self._calc = {}

    # noinspection PyTypeChecker
    @classmethod
    def from_dict(cls, data: dict):
        item = cls(
            x=data.get('x'),
            y=data.get('y'),
            speed=data.get('speed'),
            direction=data.get('direction'),
            width=data.get('width'),
            pressure=data.get('pressure')
        )
        for key, value in data.items():
            if key.startswith('_calc_'):
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
                "No calculation data available. Ensure 'stroker_data_in_json' is enabled and the layer data is refreshed.")
        return self._calc
