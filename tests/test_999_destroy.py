from pylibrm_lines.pens import ALL_PEN_IDS, get_pen_repr
from src.pylibrm_lines import SceneTree
from pylibrm_lines.renderer import Renderer
from tests.base import BaseTest

class DESTROY(BaseTest):
    def test_990_destroy_renderers(self):
        for renderer in self.renderers:
            renderer.destroy()

    def test_991_destroy_trees(self):
        for tree in self.trees:
            tree.destroy()