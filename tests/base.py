import logging
import os
import unittest
from pathlib import Path
from typing import ClassVar

from rm_api.models import LocalDocument

from pylibrm_lines.lib import set_permissive_mode, get_permissive_mode
from .conftest import TEST_FILE
from pylibrm_lines import (
    set_debug_logger,
    set_debug_mode,
    set_error_logger,
    set_logger,
    get_debug_mode,
)
from pylibrm_lines.renderer import Renderer
from pylibrm_lines import SceneTree, SceneInfo

SOURCE_DIR = Path(__file__).parent.parent
RESULTS_DIRECTORY = SOURCE_DIR / "results"
BASE_DIRECTORY = SOURCE_DIR / "tests"
OTHER_DIRECTORY = SOURCE_DIR / "tests" / "other"
TESTS_DIRECTORY = SOURCE_DIR / "tests" / "files"
JSON_DIRECTORY = RESULTS_DIRECTORY / "json"
PARAGRAPHS_DIRECTORY = RESULTS_DIRECTORY / "paragraphs"
LAYER_FULL_DIRECTORY = RESULTS_DIRECTORY / "layer_full"
PNG_DIRECTORY = RESULTS_DIRECTORY / "png"
PNG_SIZED_DIRECTORY = RESULTS_DIRECTORY / "png_sized"
PIL_BACKDROP_DIRECTORY = RESULTS_DIRECTORY / "pil_backdrop"
PDF_BACKDROP_DIRECTORY = RESULTS_DIRECTORY / "pdf_backdrop"
ZOOM_DIRECTORY = RESULTS_DIRECTORY / "zoom"
SVG_DIRECTORY = RESULTS_DIRECTORY / "svg"
PDF_DIRECTORY = RESULTS_DIRECTORY / "pdf"
MD_DIRECTORY = RESULTS_DIRECTORY / "md"
TXT_DIRECTORY = RESULTS_DIRECTORY / "txt"

# Make the necessary directories
os.makedirs(RESULTS_DIRECTORY, exist_ok=True)
os.makedirs(JSON_DIRECTORY, exist_ok=True)
os.makedirs(PARAGRAPHS_DIRECTORY, exist_ok=True)
os.makedirs(PNG_DIRECTORY, exist_ok=True)
os.makedirs(PNG_SIZED_DIRECTORY, exist_ok=True)
os.makedirs(LAYER_FULL_DIRECTORY, exist_ok=True)
os.makedirs(PIL_BACKDROP_DIRECTORY, exist_ok=True)
os.makedirs(PDF_BACKDROP_DIRECTORY, exist_ok=True)
os.makedirs(ZOOM_DIRECTORY, exist_ok=True)
os.makedirs(SVG_DIRECTORY, exist_ok=True)
os.makedirs(PDF_DIRECTORY, exist_ok=True)
os.makedirs(MD_DIRECTORY, exist_ok=True)
os.makedirs(TXT_DIRECTORY, exist_ok=True)


class BaseTest(unittest.TestCase):
    documents: ClassVar[list[LocalDocument]]
    trees: ClassVar[list[SceneTree]] = []
    renderers: ClassVar[list[Renderer]] = []

    @classmethod
    def setUpClass(cls):
        if cls is BaseTest:
            raise unittest.SkipTest("")  # Skip BaseTest tests, it's a base class
        super().setUpClass()
        logger = logging.getLogger(cls.__name__)

        set_debug_logger(lambda msg: logger.debug(msg))
        set_error_logger(lambda msg: logger.error(msg))
        set_logger(lambda msg: logger.info(msg))
        set_debug_mode(True)
        set_permissive_mode(True)

        assert get_debug_mode() is True
        assert get_permissive_mode() is True

        # LOAD DOCUMENTS USING NEW DOCUMENT LOADING METHOD
        cls.documents = []
        result_dirs = [
            os.path.join(RESULTS_DIRECTORY, d)
            for d in os.listdir(RESULTS_DIRECTORY)
            if os.path.isdir(os.path.join(RESULTS_DIRECTORY, d))
        ]

        files = [TEST_FILE] if TEST_FILE else os.listdir(TESTS_DIRECTORY)

        for file in files:
            cls.documents.append(
                LocalDocument.load_rmdoc(os.path.join(TESTS_DIRECTORY, file))
            )
            for result_dir in result_dirs:
                os.makedirs(
                    os.path.join(result_dir, cls.documents[-1].metadata.visible_name),
                    exist_ok=True,
                )

    def get_filename(self, renderer: Renderer):
        return f"{renderer.scene_tree.document.metadata.visible_name}/{renderer.scene_tree.page_uuid}"
