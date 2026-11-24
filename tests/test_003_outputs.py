import json

from PIL import Image
from pygameextra import Rect

from tests.base import *


class TestOutputs(BaseTest):

    def test_100_tree_to_json_file(self):
        for tree in self.trees:
            filename = tree.page_uuid + ".json"
            tree.to_json_file(JSON_DIRECTORY / filename)

    def test_101_tree_get_scene_info(self):
        for tree in self.trees:
            assert (
                tree.scene_info is None
                or tree.scene_info.__class__.__name__ == SceneInfo.__name__
            )

    def test_102_renderer_to_md_file(self):
        for renderer in self.renderers:
            if not renderer.paragraphs:
                continue
            filename = self.get_filename(renderer) + ".md"
            renderer.to_md_file(os.path.join(MD_DIRECTORY / filename))

    def test_103_renderer_to_txt_file(self):
        for renderer in self.renderers:
            if not renderer.paragraphs:
                continue
            filename = self.get_filename(renderer) + ".txt"
            renderer.to_txt_file(os.path.join(TXT_DIRECTORY / filename))

    def test_104_renderer_to_png_file(self):
        for renderer in self.renderers:
            filename = self.get_filename(renderer) + ".png"
            renderer.to_image_file(os.path.join(PNG_SIZED_DIRECTORY / filename))

    def test_105_renderer_get_layers(self):
        for renderer in self.renderers:
            layers = renderer.layers
            for layer in layers:
                from_uuid = renderer.get_layer_by_uuid(layer.uuid)
                self.assertEqual(
                    layer, from_uuid, f"Layer {layer.uuid} not found in renderer layers"
                )

    def test_106_renderer_get_layers_full(self):
        for renderer in self.renderers:
            layers = renderer.layers
            renderer.config.follow_rules_in_json = True
            renderer.config.stroker_data_in_json = True
            layer_data = []
            for layer in layers:
                layer.update_data()
                layer_data.append(layer._data)

            filename = self.get_filename(renderer) + f"_{layer.uuid}.json"
            with open(os.path.join(LAYER_FULL_DIRECTORY / filename), "w") as f:
                json.dump(layer_data, f, indent=4)

    def test_107_renderer_get_size_tracker(self):
        for renderer in self.renderers:
            for layer in renderer.layers:
                size_tracker = layer.size_tracker
                self.assertIsNotNone(
                    size_tracker, f"Size tracker for layer {layer.uuid} is None"
                )

    def test_108_render_scaled(self):
        for renderer in self.renderers:
            initial_rect = Rect(0, 0, *renderer.paper_size)
            rect = initial_rect.scale_by(2, 2)  # Zoomed out, aka 0.5x scale
            # print(f"Initial rect: {initial_rect}, Zoomed out rect: {rect}")

            normal_raw = renderer.get_frame_raw(
                *initial_rect.topleft, *initial_rect.size, *renderer.paper_size
            )
            normal_image = Image.frombytes(
                "RGBA", renderer.paper_size, normal_raw, "raw", "RGBA"
            )

            zoomed_out_raw = renderer.get_frame_raw(
                *rect.topleft, *rect.size, *renderer.paper_size
            )
            zoomed_out_image = Image.frombytes(
                "RGBA", renderer.paper_size, zoomed_out_raw, "raw", "RGBA"
            )

            rect = initial_rect.scale_by(0.5, 0.5)  # Zoomed in, aka 2x scale
            # print(f"Zoomed in rect: {rect}")

            zoomed_in_raw = renderer.get_frame_raw(
                *rect.topleft, *rect.size, *renderer.paper_size
            )
            zoomed_in_image = Image.frombytes(
                "RGBA", renderer.paper_size, zoomed_in_raw, "raw", "RGBA"
            )

            # Join the images into one combined image for comparison
            combined_image = Image.new(
                "RGB", (renderer.paper_size[0] * 3, renderer.paper_size[1])
            )

            combined_image.paste(normal_image, (0, 0))
            combined_image.paste(zoomed_out_image, (renderer.paper_size[0], 0))
            combined_image.paste(zoomed_in_image, (renderer.paper_size[0] * 2, 0))

            combined_image.save(ZOOM_DIRECTORY / f"{self.get_filename(renderer)}.png")

    def test_109_renderer_get_paragraphs(self):
        for renderer in self.renderers:
            if not renderer.paragraphs:
                continue
            filename = self.get_filename(renderer) + ".json"
            paras = renderer.get_paragraphs_dict()
            with open(os.path.join(PARAGRAPHS_DIRECTORY / filename), "w") as f:
                json.dump(paras, f, indent=4)

    def test_110_renderer_to_png_file_full(self):
        for renderer in self.renderers:
            filename = self.get_filename(renderer) + ".png"
            filename_backdrop = self.get_filename(renderer) + ".backdrop.png"
            filename_no_debug = self.get_filename(renderer) + ".no_debug.png"
            filename_size_tracker = self.get_filename(renderer) + ".size.txt"

            l, t, r, b = 0, 0, 0, 0
            for layer in renderer.layers:
                l = min(l, layer.size_tracker.left)
                t = min(t, layer.size_tracker.top)
                r = max(r, layer.size_tracker.right)
                b = max(b, layer.size_tracker.bottom)
            width = int(r - l)
            height = int(b - t)
            raw = renderer.get_frame_raw(int(l), int(t), width, height, width, height)
            image = Image.frombytes("RGBA", (width, height), raw, "raw", "RGBA")

            background = Image.new("RGB", image.size, "#A0D0A0")
            background.paste(image, mask=image.getchannel("A"))

            background.save(os.path.join(PNG_DIRECTORY / filename_backdrop))
            image.save(os.path.join(PNG_DIRECTORY / filename))

            set_debug_mode(False)
            raw = renderer.get_frame_raw(int(l), int(t), width, height, width, height)
            image = Image.frombytes("RGBA", (width, height), raw, "raw", "RGBA")
            image.save(os.path.join(PNG_DIRECTORY / filename_no_debug))
            set_debug_mode(True)

            # Save the size tracker information
            with open(os.path.join(PNG_DIRECTORY / filename_size_tracker), "w") as f:
                f.write(f"[{l}, {t}, {r}, {b}]")
