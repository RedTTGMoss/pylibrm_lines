from tests.base import *


class TestOutputs(BaseTest):

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
            filename = self.get_filename(renderer) + '.md'
            renderer.to_md_file(os.path.join(MD_DIRECTORY / filename))

    def test_103_renderer_to_txt_file(self):
        for renderer in self.renderers:
            if not renderer.paragraphs:
                continue
            filename = self.get_filename(renderer) + '.txt'
            renderer.to_txt_file(os.path.join(TXT_DIRECTORY / filename))

    def test_104_renderer_to_png_file(self):
        for renderer in self.renderers:
            filename = self.get_filename(renderer) + '.png'
            renderer.to_image_file(os.path.join(PNG_DIRECTORY / filename))

    def test_105_renderer_get_layers(self):
        for renderer in self.renderers:
            layers = renderer.layers
            for layer in layers:
                from_uuid = renderer.get_layer_by_uuid(layer.uuid)
                self.assertEqual(layer, from_uuid, f"Layer {layer.uuid} not found in renderer layers")

    def test_106_renderer_get_size_tracker(self):
        for renderer in self.renderers:
            for layer in renderer.layers:
                size_tracker = layer.size_tracker
                self.assertIsNotNone(size_tracker, f"Size tracker for layer {layer.uuid} is None")

    def test_107_render_scaled(self):
        for renderer in self.renderers:
            initial_rect = Rect(0, 0, *renderer.paper_size)
            rect = initial_rect.scale_by(2, 2)  # Zoomed out, aka 0.5x scale
            # print(f"Initial rect: {initial_rect}, Zoomed out rect: {rect}")

            normal_raw = renderer.get_frame_raw(*initial_rect.topleft, *initial_rect.size, *renderer.paper_size)
            normal_image = Image.frombytes('RGBA', renderer.paper_size, normal_raw, 'raw', 'RGBA')

            zoomed_out_raw = renderer.get_frame_raw(*rect.topleft, *rect.size, *renderer.paper_size)
            zoomed_out_image = Image.frombytes('RGBA', renderer.paper_size, zoomed_out_raw, 'raw', 'RGBA')

            rect = initial_rect.scale_by(0.5, 0.5)  # Zoomed in, aka 2x scale
            # print(f"Zoomed in rect: {rect}")

            zoomed_in_raw = renderer.get_frame_raw(*rect.topleft, *rect.size, *renderer.paper_size)
            zoomed_in_image = Image.frombytes('RGBA', renderer.paper_size, zoomed_in_raw, 'raw', 'RGBA')

            # Join the images into one combined image for comparison
            combined_image = Image.new('RGB', (renderer.paper_size[0] * 3, renderer.paper_size[1]))

            combined_image.paste(normal_image, (0, 0))
            combined_image.paste(zoomed_out_image, (renderer.paper_size[0], 0))
            combined_image.paste(zoomed_in_image, (renderer.paper_size[0] * 2, 0))

            for y in range(renderer.paper_size[1]):
                combined_image.putpixel((renderer.paper_size[0] - 1, y), (150, 0, 0, 255))
                combined_image.putpixel((renderer.paper_size[0], y), (255, 0, 0, 255))
                combined_image.putpixel((renderer.paper_size[0] + 1, y), (150, 0, 0, 255))

                combined_image.putpixel((renderer.paper_size[0] * 2 - 1, y), (0, 0, 150, 255))
                combined_image.putpixel((renderer.paper_size[0] * 2, y), (0, 0, 255, 255))
                combined_image.putpixel((renderer.paper_size[0] * 2 + 1, y), (0, 0, 150, 255))

            combined_image.save(ZOOM_DIRECTORY / f"{self.get_filename(renderer)}.png")
