import pymupdf

from tests.base import *


class TestBackdrop(BaseTest):
    def test_001_test_backdrop_pil(self):
        image = Image.open(os.path.join(OTHER_DIRECTORY, 'lines_icon.png'))
        # image = Image.new('RGBA', (256, 256), (255, 0, 0, 100))  # Create a red square image
        for renderer in self.renderers:
            renderer.set_backdrop_image(image)
            filename = self.get_filename(renderer) + '.png'
            renderer.to_image_file(os.path.join(PIL_BACKDROP_DIRECTORY / filename))

    def test_002_test_backdrop_pymupdf(self):
        pdf = pymupdf.open(os.path.join(OTHER_DIRECTORY, '1000x500.pdf'))
        # image = Image.new('RGBA', (256, 256), (255, 0, 0, 100))  # Create a red square image
        for renderer in self.renderers:
            renderer.set_backdrop_pymupdf(pdf[0])
            filename = self.get_filename(renderer) + '.png'
            renderer.to_image_file(os.path.join(PDF_BACKDROP_DIRECTORY / filename))
