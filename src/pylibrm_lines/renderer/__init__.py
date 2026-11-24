import json
import os
from _ctypes import Array
from abc import ABC, abstractmethod
from ctypes import c_ubyte, c_uint32
from enum import Enum
from typing import TYPE_CHECKING

import PIL.Image as PILImage
from rm_api.defaults import RM_SCREEN_SIZE, FileTypes
from rm_lines_sys import lib

from pylibrm_lines.exceptions import (
    FailedToConvertToMd,
    FailedToConvertToTxt,
    FailedToMakeRenderer,
    EXCEPTIONS_LIBRM_LINES,
)
from pylibrm_lines.renderer.config import RendererConfig
from pylibrm_lines.scene_items.glyph_range import GlyphRangeItem
from pylibrm_lines.scene_items.image import ImageItem
from pylibrm_lines.scene_items.line import LineItem
from pylibrm_lines.text import Paragraph

from .backdrop_alignments import *
from .pens import *

if TYPE_CHECKING:
    from pymupdf import Page

    from pylibrm_lines.scene_tree import SceneTree


class PageType(Enum):
    Notebook = 0
    Document = 1


class SizeTracker:
    linked_layer: "LayerInfo"
    top: int
    left: int
    bottom: int
    right: int
    frame_width: int
    frame_height: int

    def __init__(
        self,
        linked_layer: "LayerInfo",
        top: int,
        left: int,
        bottom: int,
        right: int,
        frame_width: int,
        frame_height: int,
    ):
        self._linked_layer = linked_layer
        self._top = top
        self._left = left
        self._bottom = bottom
        self._right = right
        self._frame_width = frame_width
        self._frame_height = frame_height

    @classmethod
    def from_dict(cls, linked_layer: "LayerInfo", size_tracker_info: dict):
        return cls(
            linked_layer,
            size_tracker_info["t"],  # top
            size_tracker_info["l"],  # left
            size_tracker_info["b"],  # bottom
            size_tracker_info["r"],  # right
            size_tracker_info["fw"],  # frame_width
            size_tracker_info["fh"],  # frame_height
        )

    @property
    def linked_layer(self) -> "LayerInfo":
        return self._linked_layer

    @property
    def top(self) -> int:
        return self._top

    @property
    def left(self) -> int:
        return self._left

    @property
    def bottom(self) -> int:
        return self._bottom

    @property
    def right(self) -> int:
        return self._right

    @property
    def frame_width(self) -> int:
        return self._frame_width

    @property
    def frame_height(self) -> int:
        return self._frame_height

    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def height(self) -> int:
        return self.bottom - self.top


class LayerItemInfo(ABC):
    def __init__(self, group_id: str, uuid: str, offset_x: float, offset_y: float):
        self._group_id = group_id
        self._uuid = uuid
        self._offset_x = offset_x
        self._offset_y = offset_y

    @classmethod
    @abstractmethod
    def from_dict(cls, item_info: dict):
        return cls(
            item_info["groupId"],
            item_info["itemId"],
            item_info["offsetX"],
            item_info["offsetY"],
        )

    @property
    def group_id(self) -> str:
        return self._group_id

    @property
    def uuid(self) -> str:
        return self._uuid

    @property
    def offset_x(self) -> float:
        return self._offset_x

    @property
    def offset_y(self) -> float:
        return self._offset_y


class LineInfo(LayerItemInfo):

    def __init__(self, group_id: str, uuid: str, offset_x: float, offset_y: float):
        super().__init__(group_id, uuid, offset_x, offset_y)
        self._line = None

    @property
    def line(self) -> LineItem | None:
        return self._line

    @classmethod
    def from_dict(cls, item_info: dict):
        item = super().from_dict(item_info)
        item._line = LineItem.from_dict(item_info["line"])
        return item


class ImageInfo(LayerItemInfo):

    def __init__(self, group_id: str, uuid: str, offset_x: float, offset_y: float):
        super().__init__(group_id, uuid, offset_x, offset_y)
        self._image = None

    @property
    def image(self) -> ImageItem | None:
        return self._image

    @classmethod
    def from_dict(cls, item_info: dict):
        item = super().from_dict(item_info)
        item._image = ImageItem.from_dict(item_info["image"])
        return item


class GlyphRangeInfo(LayerItemInfo):

    def __init__(self, group_id: str, uuid: str, offset_x: float, offset_y: float):
        super().__init__(group_id, uuid, offset_x, offset_y)
        self._glyph_range = None

    @property
    def glyph_range(self) -> GlyphRangeItem | None:
        return self._glyph_range

    @classmethod
    def from_dict(cls, item_info: dict):
        item = super().from_dict(item_info)
        item._glyph_range = GlyphRangeItem.from_dict(item_info["glyphRange"])
        return item


class LayerInfo:
    renderer: "Renderer"
    uuid: str
    label: str
    visible: bool

    def __init__(
        self, renderer: "Renderer", uuid: str, label: str, visible: bool = True
    ):
        self.renderer = renderer
        self._uuid = uuid
        self._label = label
        self._visible = visible
        self._size_tracker = None
        self._data: dict | None = None
        self._lines = None
        self._images = None
        self._glyph_ranges = None

        self.update_size_tracker()
        self.update_data()

    @classmethod
    def from_dict(cls, renderer: "Renderer", layer_info: dict):
        return cls(
            renderer, layer_info["groupId"], layer_info["label"], layer_info["visible"]
        )

    def update_size_tracker(self):
        self._size_tracker = SizeTracker.from_dict(
            self, self.renderer.get_size_tracker_dict(self.uuid)
        )

    @property
    def uuid(self) -> str:
        return self._uuid

    @property
    def label(self) -> str:
        return self._label

    @property
    def visible(self) -> bool:
        return self._visible

    @property
    def size_tracker(self) -> SizeTracker | None:
        if self._size_tracker is None:
            self.update_size_tracker()
        return self._size_tracker

    @property
    def lines(self) -> list[LineInfo]:
        if self._lines is None:
            self.update_lines()
        return self._lines

    def update_lines(self):
        if not self._data:
            return self.update_data()
        self._lines = [
            LineInfo.from_dict(line_info) for line_info in self._data.get("lines", [])
        ]

    @property
    def images(self):
        if self._images is None:
            self.update_images()
        return self._images

    def update_images(self):
        if not self._data:
            return self.update_data()
        self._images = [
            ImageInfo.from_dict(image_info)
            for image_info in self._data.get("images", [])
        ]

    @property
    def glyph_ranges(self):
        if self._glyph_ranges is None:
            self.update_glyph_ranges()
        return self._glyph_ranges

    def update_glyph_ranges(self):
        if not self._data:
            return self.update_data()
        self._glyph_ranges = [
            GlyphRangeInfo.from_dict(glyph_range_info)
            for glyph_range_info in self._data.get("glyphRanges", [])
        ]

    def update_data(self):
        self._data = self.renderer.get_layer_full_dict(self.uuid)

        # Update basic layer info
        self._label = self._data.get("label", self.label)
        self._uuid = self._data.get("groupId", self.uuid)
        self._visible = self._data.get("visible", self.visible)

        # Update item info
        self.update_lines()
        self.update_images()
        self.update_glyph_ranges()


class Renderer:
    uuid: bytes
    _paragraphs: list[Paragraph] | None
    _layers: list[LayerInfo] | None
    scene_tree = "SceneTree"

    def __init__(
        self,
        scene_tree: "SceneTree",
        page_type: PageType | None = None,
        landscape: bool | None = None,
    ):
        self.scene_tree = scene_tree
        self._paragraphs = None
        self._layers = None
        self._config = None
        self._backdrop_ptr = None
        self._template = "Blank"
        self._layers_index = {}
        if not landscape:
            if scene_tree.document:
                landscape = scene_tree.document.content.is_landscape
            else:
                raise ValueError(
                    "Missing value for landscape and cannot infer from document"
                )
        if not page_type:
            if scene_tree.document:
                page_type = (
                    PageType.Notebook
                    if scene_tree.document.content.file_type == FileTypes.Notebook.value
                    else PageType.Document
                )
            else:
                raise ValueError(
                    "Missing value for page_type and cannot infer from document type"
                )

        self.uuid = lib.makeRenderer(self.scene_tree.uuid, page_type.value, landscape)

        if not self.uuid or self.uuid == b"-1":
            # RARE, this shouldn't happen,
            # unless there is a bug in how the renderer is loaded,
            # or the scene tree is corrupt
            # You shouldn't need to catch this exception, but if you do, please report it!
            raise FailedToMakeRenderer()
        elif self.uuid[0] == 45:
            err_code = int(self.uuid)
            raise EXCEPTIONS_LIBRM_LINES.get(err_code, FailedToMakeRenderer)()

        page = self.scene_tree.document.content.c_pages.get_page_from_uuid(
            self.scene_tree.page_uuid
        )
        page.renderer = self

        self.landscape = landscape
        self.page_type = page_type
        self.scene_tree.renderer = self
        if scene_tree.document:
            self.template = scene_tree.document.content.c_pages.get_page_from_uuid(
                scene_tree.page_uuid
            ).template.value

            if scene_tree.image_info:
                for uuid, filename in scene_tree.image_info.iter_uuid_filenames():
                    file_uuid = (
                        f"{scene_tree.document.uuid}/{scene_tree.page_uuid}/{filename}"
                    )
                    file = scene_tree.document.file_uuid_map.get(file_uuid)
                    if file:
                        lib.addImage(
                            self.uuid,
                            uuid.encode(),
                            scene_tree.document.get_file(file.hash).encode(),
                        )

        self._update_paragraphs()
        self._update_layers()

    def set_backdrop_raw(
        self,
        backdrop_ptr: Array[c_ubyte],
        size: int,
        width: int,
        height: int,
        stride: int,
    ):
        """
        Set a backdrop from a raw pointer. The pointer should point to a buffer in RGBA format, with 4 bytes per pixel.

        :param backdrop_ptr:
        :param size:
        :param width:
        :param height:
        :param stride:
        :return:
        """
        self._backdrop_ptr = backdrop_ptr
        lib.setBackdrop(self.uuid, self._backdrop_ptr, size, width, height, stride)

    def set_backdrop_buffer(
        self,
        buffer: bytes | bytearray,
        width: int,
        height: int,
        stride: int | None = None,
    ):
        """
        Set a backdrop from bytes buffer. The buffer should be in RGBA format, with 4 bytes per pixel.

        :param buffer:
        :param width:
        :param height:
        :param stride:
        :return:
        """
        self._backdrop_ptr = (c_ubyte * len(buffer)).from_buffer_copy(buffer)
        self.set_backdrop_raw(
            self._backdrop_ptr, len(buffer), width, height, stride or width * 4
        )

    def set_backdrop_image(self, image: PILImage.Image):
        """
        Set a backdrop from a PIL Image. The image will be converted to RGBA format.

        :param image:
        :return:
        """
        image = image.convert("RGBA")

        buffer = image.tobytes()
        stride = image.width * len(image.getbands())
        self.set_backdrop_buffer(buffer, image.width, image.height, stride)

    def set_backdrop_pymupdf(self, pdf_page: "Page", dpi: int | None = 227):
        """
        Set a backdrop from a PyMuPDF page. The page will be rendered to an RGBA image.

        :param dpi: The DPI to render the page at. Default is 227, which is the default for reMarkable.
        :param pdf_page: The PyMuPDF page to use as a backdrop.
        :return:
        """
        image = pdf_page.get_pixmap(alpha=True, dpi=dpi)
        self.set_backdrop_buffer(image.samples, image.width, image.height, image.stride)

    @property
    def config(self) -> RendererConfig:
        if self._config is None:
            config_ptr = lib.getConfig(self.uuid)
            self._config = RendererConfig(self, config_ptr)
        return self._config

    @property
    def paper_size(self) -> tuple[int, int]:
        if self.scene_tree.scene_info and self.scene_tree.scene_info.paper_size:
            paper_size = self.scene_tree.scene_info.paper_size
        else:
            paper_size = RM_SCREEN_SIZE
        if self.landscape:
            return paper_size[1], paper_size[0]
        return paper_size

    @property
    def template(self) -> str:
        return self._template

    @template.setter
    def template(self, value: str):
        lib.setTemplate(self.uuid, value.encode())
        self._template = value

    def get_paragraphs_raw(self) -> bytes | None:
        raw = lib.getParagraphs(self.uuid)
        if raw == b"":
            return None
        return raw

    def get_paragraphs_dict(self) -> list[dict] | None:
        raw = self.get_paragraphs_raw()
        if raw is None:
            return None
        return json.loads(raw.decode())

    def get_paragraphs(self) -> list[Paragraph] | None:
        paragraphs = self.get_paragraphs_dict()
        if not paragraphs:
            return None
        return [Paragraph.from_dict(self, paragraph) for paragraph in paragraphs]

    def get_layers_raw(self) -> bytes | None:
        raw = lib.getLayers(self.uuid)
        if raw == b"":
            return None
        return raw

    def get_layers_dict(self) -> list[dict] | None:
        raw = self.get_layers_raw()
        if raw is None:
            return None
        return json.loads(raw.decode())

    def get_layers(self) -> list[LayerInfo] | None:
        layers = self.get_layers_dict()
        if not layers:
            return None
        return [LayerInfo.from_dict(self, layer) for layer in layers]

    def get_layer_by_uuid(self, layer_uuid: str) -> LayerInfo | None:
        if not self._layers_index:
            self._update_layers()
        return self._layers_index.get(layer_uuid, None)

    def get_size_tracker_raw(self, layer_uuid: str) -> bytes | None:
        raw = lib.getSizeTracker(self.uuid, layer_uuid.encode())
        if raw == b"":
            return None
        return raw

    def get_size_tracker_dict(self, layer_uuid: str) -> dict | None:
        raw = self.get_size_tracker_raw(layer_uuid)
        if raw is None:
            return None
        return json.loads(raw.decode())

    def get_layer_full_raw(self, layer_uuid: str) -> bytes | None:
        raw = lib.getLayerFull(self.uuid, layer_uuid.encode())
        if raw == b"":
            return None
        return raw

    def get_layer_full_dict(self, layer_uuid: str) -> dict | None:
        raw = self.get_layer_full_raw(layer_uuid)
        if raw is None:
            return None
        return json.loads(raw.decode())

    def get_size_tracker(self, layer_uuid: str) -> SizeTracker | None:
        layer = self.get_layer_by_uuid(layer_uuid)
        if not layer:
            return None
        return layer.size_tracker

    def _update_paragraphs(self):
        self._paragraphs = self.get_paragraphs()

    def _update_layers(self):
        self._layers = self.get_layers()
        self._layers_index = (
            {layer.uuid: layer for layer in self._layers} if self._layers else {}
        )

    @property
    def paragraphs(self) -> list[Paragraph] | None:
        if self._paragraphs is None:
            self._update_paragraphs()
        return self._paragraphs

    @property
    def layers(self) -> list[LayerInfo] | None:
        if self._layers is None:
            self._update_layers()
        return self._layers

    def to_md_file(self, output_file: os.PathLike | str):
        success = lib.textToMdFile(self.uuid, os.fspath(output_file).encode())
        if not success:
            raise FailedToConvertToMd()

    def to_md_raw(self) -> str:
        raw = lib.textToMd(self.uuid)
        if raw == b"":
            raise FailedToConvertToMd()
        return raw.decode()

    def to_txt_file(self, output_file: os.PathLike | str):
        success = lib.textToTxtFile(self.uuid, os.fspath(output_file).encode())
        if not success:
            raise FailedToConvertToTxt()

    def to_txt_raw(self) -> str:
        raw = lib.textToTxt(self.uuid)
        if raw == b"":
            raise FailedToConvertToTxt()
        return raw.decode()

    def get_frame_raw(
        self,
        x: int,
        y: int,
        frame_width: int,
        frame_height: int,
        width: int,
        height: int,
        antialias: bool = False,
    ) -> bytes:
        buffer_size = width * height
        buffer = (c_uint32 * buffer_size)()

        lib.getFrame(
            self.uuid,
            buffer,
            buffer_size * 4,
            x,
            y,
            frame_width,
            frame_height,
            width,
            height,
            antialias,
        )
        return bytes(buffer)

    def to_image_raw(self, antialias: bool = False) -> tuple[bytes, tuple[int, int]]:
        return (
            self.get_frame_raw(0, 0, *self.paper_size, *self.paper_size, antialias),
            self.paper_size,
        )

    def to_image(self, antialias: bool = False) -> PILImage.Image:
        raw_frame, size = self.to_image_raw(antialias)
        return PILImage.frombytes("RGBA", size, raw_frame, "raw", "RGBA")

    def to_image_file(
        self,
        output_file: os.PathLike | str,
        antialias: bool = False,
        image_format: str = "PNG",
    ):
        image = self.to_image(antialias)
        image.save(os.fspath(output_file), image_format)

    def destroy(self):
        if not self.uuid:
            return
        lib.destroyRenderer(self.uuid)
        self.uuid = b""

    def __del__(self):
        self.destroy()
