from typing import List

from rm_api.models import TimestampedValue


class ImageItem:
    def __init__(self, image_ref: TimestampedValue[str], bounds_timestamp: str, vertices: List[float],
                 indices: List[int]):
        self.image_ref = image_ref
        self.bounds_timestamp = bounds_timestamp
        self.vertices = vertices
        self.indices = indices

    @classmethod
    def from_dict(cls, data: dict):
        image_ref = TimestampedValue[str](data['imageRef'])
        bounds_timestamp = data['boundsTimestamp']
        vertices = data['vertices']
        indices = data['indices']
        return cls(image_ref, bounds_timestamp, vertices, indices)
