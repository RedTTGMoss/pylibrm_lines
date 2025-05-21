import os
import unittest
from abc import ABC
from typing import List

from rm_api import API
from pathlib import Path

from rm_api.auth import FailedToRefreshToken

from src.pylibrm_lines import SceneTree
from src.pylibrm_lines.renderer import Renderer
from src.pylibrm_lines.scene_info import SceneInfo
from src.pylibrm_lines.text import ParagraphStyle

RESULTS_DIRECTORY = Path('results')
JSON_DIRECTORY = RESULTS_DIRECTORY / 'json'
PNG_DIRECTORY = RESULTS_DIRECTORY / 'png'
SVG_DIRECTORY = RESULTS_DIRECTORY / 'svg'
PDF_DIRECTORY = RESULTS_DIRECTORY / 'pdf'
MD_DIRECTORY = RESULTS_DIRECTORY / 'md'
TXT_DIRECTORY = RESULTS_DIRECTORY / 'txt'

# Make the necessary directories
os.makedirs(RESULTS_DIRECTORY, exist_ok=True)
os.makedirs(JSON_DIRECTORY, exist_ok=True)
os.makedirs(PNG_DIRECTORY, exist_ok=True)
os.makedirs(SVG_DIRECTORY, exist_ok=True)
os.makedirs(PDF_DIRECTORY, exist_ok=True)
os.makedirs(MD_DIRECTORY, exist_ok=True)
os.makedirs(TXT_DIRECTORY, exist_ok=True)


class BaseTest(unittest.TestCase):
    api: API
    trees: List[SceneTree]
    renderers: List[Renderer]

    @classmethod
    def setUpClass(cls):
        if cls is BaseTest:
            raise unittest.SkipTest("Skip BaseTest tests, it's a base class")
        super(BaseTest, cls).setUpClass()

        uri = os.environ.get("CLOUD_URI")
        if not os.environ.get("TOKEN"):
            raise ValueError("Please set the `TOKEN` environment variable.")
        try:
            cls.api = API(uri=uri, discovery_uri=uri, require_token=False)
        except FailedToRefreshToken:
            raise ValueError("Failed to refresh token. Please check your token.")
        cls.api.get_documents()
        cls.trees = []
        cls.renderers = []

    def test_100_tree_to_json_file(self):
        for tree in self.trees:
            filename = tree.page_uuid + '.json'
            tree.to_json_file(JSON_DIRECTORY / filename)

    def test_101_tree_get_scene_info(self):
        for tree in self.trees:
            assert tree.scene_info is None or isinstance(tree.scene_info, SceneInfo)

    def test_102_renderer_to_md_file(self):
        for renderer in self.renderers:
            if not renderer.paragraphs:
                continue
            filename = renderer.scene_tree.page_uuid + '.md'
            renderer.to_md_file(os.path.join(MD_DIRECTORY / filename))

    def test_103_renderer_to_txt_file(self):
        for renderer in self.renderers:
            if not renderer.paragraphs:
                continue
            filename = renderer.scene_tree.page_uuid + '.txt'
            renderer.to_txt_file(os.path.join(TXT_DIRECTORY / filename))

    def test_104_renderer_to_png_file(self):
        for renderer in self.renderers:
            filename = renderer.scene_tree.page_uuid + '.png'
            renderer.to_image_file(os.path.join(PNG_DIRECTORY / filename))
