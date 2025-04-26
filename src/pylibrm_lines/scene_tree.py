import json
import os
import tempfile
from pathlib import Path
from typing import Optional, Union

from rm_api import Document, API
from rm_lines_sys import lib

class LibMissing(Exception):
    def __init__(self):
        super().__init__("LIB rm_lines was not loaded properly")

class FailedToBuildTree(Exception):
    def __init__(self):
        super().__init__("An major issue occurred reading the LINES file and building the scene tree")


class SceneTree:
    uuid: bytes
    document: Optional[Document]
    page_uuid: Optional[str]

    def __init__(self, uuid: bytes = b'', document: Document = None, page_uuid: str = None):
        if not lib:
            # Prevent creating new instances of scene tree if the library is missing
            raise LibMissing()
        self.uuid = uuid
        self.document = document
        self.page_uuid = page_uuid

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
        file_path = os.path.join(new.api.sync_file_path, file.hash)

        new.uuid = lib.buildTree(file_path.encode())

        if not new.uuid:
            raise FailedToBuildTree()

        return new

    def to_json_file(self, output_file: Union[os.PathLike, str]):
        lib.convertToJson(self.uuid, os.fspath(output_file).encode())

    def to_json_raw(self) -> str:
        temp_file = tempfile.mktemp()
        self.to_json_file(temp_file)
        with open(temp_file, 'r') as f:
            raw = f.read()
        os.remove(temp_file)
        return raw

    def to_dict(self) -> dict:
        temp_file = tempfile.mktemp()
        self.to_json_file(temp_file)
        with open(temp_file, 'r') as f:
            result = json.load(f)
        os.remove(temp_file)
        return result