import json
import os
from enum import Enum
from typing import List, Optional, TYPE_CHECKING, Union

from rm_api.defaults import DocumentTypes, FileTypes
from rm_lines_sys import lib

from .exceptions import FailedToConvertToMd, FailedToConvertToTxt
from .text import Paragraph

if TYPE_CHECKING:
    from .scene_tree import SceneTree


class PageType(Enum):
    Notebook = 0
    Document = 1


class Renderer:
    uuid: bytes
    _paragraphs: Optional[List[Paragraph]]
    scene_tree = 'SceneTree'

    def __init__(self, scene_tree: 'SceneTree', page_type: PageType = None, landscape: bool = None):
        self.scene_tree = scene_tree
        self._paragraphs = None
        if not landscape:
            if scene_tree.document:
                landscape = scene_tree.document.content.is_landscape
            else:
                raise ValueError("Missing value for landscape and cannot infer from document")
        if not page_type:
            if scene_tree.document:
                page_type = PageType.Notebook if scene_tree.document.content.file_type == FileTypes.Notebook.value else PageType.Document
            else:
                raise ValueError("Missing value for page_type and cannot infer from document type")
        self.uuid = lib.makeRenderer(self.scene_tree.uuid, page_type.value, landscape)

        self._update_paragraphs()

    def get_paragraphs_raw(self) -> Optional[bytes]:
        raw = lib.getParagraphs(self.uuid)
        if raw == b'':
            return None
        return raw

    def get_paragraphs_dict(self) -> Optional[List[dict]]:
        raw = self.get_paragraphs_raw()
        if raw is None:
            return None
        return json.loads(raw.decode())

    def get_paragraphs(self) -> Optional[List[Paragraph]]:
        paragraphs = self.get_paragraphs_dict()
        if not paragraphs:
            return None
        return [Paragraph.from_dict(self, paragraph) for paragraph in paragraphs]

    def _update_paragraphs(self):
        self._paragraphs = self.get_paragraphs()

    @property
    def paragraphs(self) -> Optional[List[Paragraph]]:
        if self._paragraphs is None:
            self._update_paragraphs()
        return self._paragraphs

    def to_md_file(self, output_file: Union[os.PathLike, str]):
        success = lib.textToMdFile(self.uuid, os.fspath(output_file).encode())
        if not success:
            raise FailedToConvertToMd()

    def to_md_raw(self) -> str:
        raw = lib.textToMd(self.uuid)
        if raw == b'':
            raise FailedToConvertToMd()
        return raw.decode()

    def to_txt_file(self, output_file: Union[os.PathLike, str]):
        success = lib.textToTxtFile(self.uuid, os.fspath(output_file).encode())
        if not success:
            raise FailedToConvertToTxt()

    def to_txt_raw(self) -> str:
        raw = lib.textToTxt(self.uuid)
        if raw == b'':
            raise FailedToConvertToTxt()
        return raw.decode()