import ctypes

from pylibrm_lines.pens import ALL_PEN_IDS, get_pen_repr
from src.pylibrm_lines import SceneTree
from pylibrm_lines.renderer import Renderer
from tests.base import BaseTest

class TestConfig(BaseTest):

    def test_001_test_getting_renderer_config(self):
        for renderer in self.renderers:
            config = renderer.config
            self.assertIsNotNone(config)
            self.assertIsInstance(config.version, int)
            # self.assertIsInstance(config.use_whitelist, bool)
            self.assertIsInstance(config.enable_text, bool)
            self.assertIsInstance(config.enable_images, bool)
            self.assertIsInstance(config.enable_glyph_highlights, bool)
            self.assertIsInstance(config.enable_backdrop, bool)
            self.assertEqual(len(config._pen_whitelist), 20)
            self.assertEqual(len(config._pen_blacklist), 20)

    def test_002_test_pens_listing(self):
        for renderer in self.renderers:
            config = renderer.config
            for pen_id in ALL_PEN_IDS:
                self.assertTrue(pen_id in config.allowed_pens, f"Pen {get_pen_repr(pen_id)}({pen_id}) should be in allowed_pens")
            self.assertEqual(len(config._disallowed_pens), 0)
            self.assertEqual(len(config.disallowed_pens), 0)
            config.use_whitelist = True
            self.assertEqual(len(config._allowed_pens), 0)
            self.assertEqual(len(config.allowed_pens), 0)
            for pen_id in ALL_PEN_IDS:
                self.assertTrue(pen_id in config.disallowed_pens, f"Pen {get_pen_repr(pen_id)}({pen_id}) should be in disallowed_pens")

            config.use_whitelist = False

    def test_003_test_pens_blacklist(self):
        for renderer in self.renderers:
            config = renderer.config

            self.assertTrue(ALL_PEN_IDS[0] in config.allowed_pens)
            self.assertTrue(ALL_PEN_IDS[0] not in config.disallowed_pens)
            config.disable_pen(ALL_PEN_IDS[0])
            self.assertTrue(ALL_PEN_IDS[0] not in config.allowed_pens)
            self.assertTrue(ALL_PEN_IDS[0] in config.disallowed_pens)
            config.enable_pen(ALL_PEN_IDS[0])
            self.assertTrue(ALL_PEN_IDS[0] in config.allowed_pens)
            self.assertTrue(ALL_PEN_IDS[0] not in config.disallowed_pens)

    def test_004_test_pens_whitelist(self):
        for renderer in self.renderers:
            config = renderer.config

            config.use_whitelist = True
            self.assertTrue(ALL_PEN_IDS[0] not in config.allowed_pens)
            self.assertTrue(ALL_PEN_IDS[0] in config.disallowed_pens)
            config.enable_pen(ALL_PEN_IDS[0])
            self.assertTrue(ALL_PEN_IDS[0] in config.allowed_pens)
            self.assertTrue(ALL_PEN_IDS[0] not in config.disallowed_pens)
            config.disable_pen(ALL_PEN_IDS[0])
            self.assertTrue(ALL_PEN_IDS[0] not in config.allowed_pens)
            self.assertTrue(ALL_PEN_IDS[0] in config.disallowed_pens)
            config.use_whitelist = False

