import os
import unittest
from abc import ABC
from typing import List

from rm_api import API

from src.pylibrm_lines import SceneTree

class BaseTest(unittest.TestCase):
    api: API
    trees: List[SceneTree]

    @classmethod
    def setUpClass(cls):
        if cls is BaseTest:
            raise unittest.SkipTest("Skip BaseTest tests, it's a base class")
        super(BaseTest, cls).setUpClass()

    def setUp(self):
        uri = os.environ.get("CLOUD_URI")
        if not os.environ.get("TOKEN"):
            raise ValueError("Please set the `TOKEN` environment variable.")
        self.api = API(uri=uri, discovery_uri=uri)
        self.api.get_documents()
        self.trees = []

