import os
import unittest
from rm_api import API

from src.pylibrm_lines import SceneTree
from tests.base import BaseTest


class TestTreeFromDocument(BaseTest):

    def test_001_tree_from_document(self):
        for document in self.api.documents.values():
            document.ensure_download()
            for page in document.content.c_pages.pages:
                self.trees.append(SceneTree.from_document(document, page.id))