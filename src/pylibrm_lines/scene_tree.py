import json
import os
from typing import Optional, Union, List, Dict, Generator, Tuple

from rm_api import Document, API
from rm_api.models import TimestampedValue
from rm_lines_sys import lib

from .scene_info import SceneInfo
from .exceptions import *

class ImageRecordInfo:
    uuid: str
    filename: TimestampedValue[str]
    flags: TimestampedValue[List[int]]

class ImageInfo:
    scene_tree: 'SceneTree'
    images: Dict[str, ImageRecordInfo]

    def __init__(self, scene_tree: 'SceneTree'):
        self.scene_tree = scene_tree
        self.images = {}

    def iter_uuid_filenames(self) -> Generator[Tuple[str, str], None, None]:
        return (
            (uuid, record.filename.value)
            for uuid, record in self.images.items()
        )

    @classmethod
    def from_dict(cls, scene_tree: 'SceneTree', image_info_dict: dict):
        image_info = cls(scene_tree)
        for uuid, record in image_info_dict.items():
            record_info = ImageRecordInfo()
            record_info.uuid = uuid
            record_info.filename = TimestampedValue(record['fileName'])
            record_info.flags = TimestampedValue(record['flags'])
            image_info.images[uuid] = record_info
        return image_info


class SceneTree:
    uuid: bytes
    document: Optional[Document]
    page_uuid: Optional[str]
    _scene_info: Optional[SceneInfo]
    _image_info: Optional[ImageInfo]

    def __init__(self, uuid: bytes = b'', document: Document = None, page_uuid: str = None):
        if not lib:
            # Prevent creating new instances of scene tree if the library is missing
            raise LibMissing()
        self.uuid = uuid
        self.document = document
        self.page_uuid = page_uuid
        self._paragraphs = None
        self._renderer = None
        self._scene_info = None
        self._image_info = None

    @property
    def api(self) -> Optional[API]:
        return self.document.api if self.document else None

    @classmethod
    def from_document(cls, document: Document, page_uuid: str):
        new = cls(document=document, page_uuid=page_uuid)
        page_file_uuid = f'{document.uuid}/{page_uuid}.rm'
        file = new.document.files_available.get(page_file_uuid)
        if file is None:
            raise FileNotFoundError("Could not find the lines file for this page_uuid")
        file_path = new.document.get_file(file.hash)

        new.uuid = lib.buildTree(file_path.encode())

        if not new.uuid:
            raise FailedToBuildTree()

        page = new.document.content.c_pages.get_page_from_uuid(page_uuid)
        setattr(page, 'tree', new)

        return new

    @property
    def renderer(self):
        if not self._renderer:
            from pylibrm_lines.renderer import Renderer
            self._renderer = Renderer(self)
        return self._renderer

    @renderer.setter
    def renderer(self, value):
        from pylibrm_lines.renderer import Renderer
        if not isinstance(value, Renderer):
            raise TypeError("Renderer must be an instance of Renderer class")
        self._renderer = value

    @renderer.deleter
    def renderer(self):
        if self._renderer:
            self._renderer.destroy()
            self._renderer = None

    def to_json_file(self, output_file: Union[os.PathLike, str]):
        success = lib.convertToJsonFile(self.uuid, os.fspath(output_file).encode())
        if not success:
            raise FailedToConvertToJson()

    def to_json_raw(self) -> str:
        raw = lib.convertToJson(self.uuid)
        if raw == b'':
            raise FailedToConvertToJson()
        return raw.decode()

    def to_dict(self) -> dict:
        raw = self.to_json_raw()
        return json.loads(raw)

    @property
    def scene_info(self) -> Optional[SceneInfo]:
        if not self._scene_info:
            try:
                self._scene_info = SceneInfo(self)
            except NoSceneInfo:
                return None
        return self._scene_info

    def get_image_info_raw(self) -> Optional[bytes]:
        raw = lib.getImageInfo(self.uuid)
        if raw == b'':
            return None
        return raw

    def get_image_info_dict(self) -> Optional[dict]:
        raw = self.get_image_info_raw()
        if raw is None:
            return None
        return json.loads(raw.decode())

    def get_image_info(self) -> Optional[ImageInfo]:
        if not self._image_info:
            image_info_dict = self.get_image_info_dict()
            if image_info_dict is None:
                return None
            self._image_info = ImageInfo.from_dict(self, image_info_dict)
        return self._image_info

    @property
    def image_info(self) -> Optional[ImageInfo]:
        return self.get_image_info()


    def destroy(self):
        """Destroying the scene tree will also destroy the renderer if it exists."""
        if not self.uuid:
            raise ValueError("Could not destroy tree, uuid is empty")
        del self.renderer
        lib.destroyTree(self.uuid)
        self.uuid = b''

    def __del__(self):
        """Deleting the scene tree calls the library to destroy the tree."""
        if not self.uuid:
            return
        lib.destroyTree(self.uuid)
