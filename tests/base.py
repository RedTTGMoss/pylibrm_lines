import os
import unittest
from abc import ABC
from typing import List

from rm_api import API
from pathlib import Path
from src.pylibrm_lines import SceneTree

RESULTS_DIRECTORY = Path('results')
JSON_DIRECTORY = RESULTS_DIRECTORY / 'json'
PNG_DIRECTORY = RESULTS_DIRECTORY / 'png'
SVG_DIRECTORY = RESULTS_DIRECTORY / 'svg'
PDF_DIRECTORY = RESULTS_DIRECTORY / 'pdf'
MD_DIRECTORY = RESULTS_DIRECTORY / 'md'

# Make the necessary directories
os.makedirs(RESULTS_DIRECTORY, exist_ok=True)
os.makedirs(JSON_DIRECTORY, exist_ok=True)
os.makedirs(PNG_DIRECTORY, exist_ok=True)
os.makedirs(SVG_DIRECTORY, exist_ok=True)
os.makedirs(PDF_DIRECTORY, exist_ok=True)
os.makedirs(MD_DIRECTORY, exist_ok=True)

class BaseTest(unittest.TestCase):
    api: API
    trees: List[SceneTree]

    @classmethod
    def setUpClass(cls):
        if cls is BaseTest:
            raise unittest.SkipTest("Skip BaseTest tests, it's a base class")
        super(BaseTest, cls).setUpClass()

        uri = os.environ.get("CLOUD_URI")
        if not os.environ.get("TOKEN"):
            raise ValueError("Please set the `TOKEN` environment variable.")
        cls.api = API(uri=uri, discovery_uri=uri)
        cls.api.get_documents()
        cls.trees = []

    def test_100_tree_to_json_file(self):
        for tree in self.trees:
            filename = tree.page_uuid + '.json'
            print(JSON_DIRECTORY / filename)
            tree.to_json_file(JSON_DIRECTORY / filename)

    def test_101_tree_to_md_file(self):
        raise unittest.SkipTest("Not implemented")