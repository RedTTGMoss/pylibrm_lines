import os
from typing import Optional

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