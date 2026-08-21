import logging
import os
import unittest
from typing import List

from PIL import Image
from pygameextra import Rect
from rm_api.models import LocalDocument
from pathlib import Path

from pylibrm_lines import set_debug_logger, set_error_logger, set_logger, set_debug_mode
from src.pylibrm_lines import SceneTree
from pylibrm_lines.renderer import Renderer
from src.pylibrm_lines.scene_info import SceneInfo

SOURCE_DIR = Path(__file__).parent.parent
RESULTS_DIRECTORY = SOURCE_DIR / 'results'
TESTS_DIRECTORY = SOURCE_DIR / 'tests' / 'files'
JSON_DIRECTORY = RESULTS_DIRECTORY / 'json'
PNG_DIRECTORY = RESULTS_DIRECTORY / 'png'
ZOOM_DIRECTORY = RESULTS_DIRECTORY / 'zoom'
SVG_DIRECTORY = RESULTS_DIRECTORY / 'svg'
PDF_DIRECTORY = RESULTS_DIRECTORY / 'pdf'
MD_DIRECTORY = RESULTS_DIRECTORY / 'md'
TXT_DIRECTORY = RESULTS_DIRECTORY / 'txt'

# Make the necessary directories
os.makedirs(RESULTS_DIRECTORY, exist_ok=True)
os.makedirs(JSON_DIRECTORY, exist_ok=True)
os.makedirs(PNG_DIRECTORY, exist_ok=True)
os.makedirs(ZOOM_DIRECTORY, exist_ok=True)
os.makedirs(SVG_DIRECTORY, exist_ok=True)
os.makedirs(PDF_DIRECTORY, exist_ok=True)
os.makedirs(MD_DIRECTORY, exist_ok=True)
os.makedirs(TXT_DIRECTORY, exist_ok=True)


class BaseTest(unittest.TestCase):
    documents: List[LocalDocument]
    trees: List[SceneTree] = []
    renderers: List[Renderer] = []

    @classmethod
    def setUpClass(cls):
        if cls is BaseTest:
            raise unittest.SkipTest('')  # Skip BaseTest tests, it's a base class
        super(BaseTest, cls).setUpClass()
        logger = logging.getLogger(cls.__name__)

        set_debug_logger(lambda msg: logger.debug(msg))
        set_error_logger(lambda msg: logger.error(msg))
        set_logger(lambda msg: logger.info(msg))
        set_debug_mode(True)

        # LOAD DOCUMENTS USING NEW DOCUMENT LOADING METHOD
        cls.documents = []
        result_dirs = [os.path.join(RESULTS_DIRECTORY, d) for d in os.listdir(RESULTS_DIRECTORY) if
                       os.path.isdir(os.path.join(RESULTS_DIRECTORY, d))]

        for file in os.listdir(TESTS_DIRECTORY):
            cls.documents.append(LocalDocument.load_rmdoc(os.path.join(TESTS_DIRECTORY, file)))
            for result_dir in result_dirs:
                os.makedirs(os.path.join(result_dir, cls.documents[-1].metadata.visible_name), exist_ok=True)


    def get_filename(self, renderer: Renderer):
        return f"{renderer.scene_tree.document.metadata.visible_name}/{renderer.scene_tree.page_uuid}"
