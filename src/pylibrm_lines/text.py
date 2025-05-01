import base64
from dataclasses import dataclass
from enum import Enum
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .renderer import Renderer

@dataclass
class TextFormattingOptions:
    bold: bool
    italic: bool

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

class FormattedText:
    renderer: 'Renderer'
    text: str
    formatting: TextFormattingOptions

    def __init__(self, renderer: 'Renderer', text: str, formatting: TextFormattingOptions):
        self.renderer = renderer
        self.text = text
        self.formatting = formatting

    @classmethod
    def from_dict(cls, renderer, formatted_text):
        return cls(
            renderer,
            formatted_text['text'],
            TextFormattingOptions.from_dict(formatted_text['formatting']),
        )


class ParagraphStyle(Enum):
    BASIC = 0
    PLAIN = 1
    HEADING = 2
    BOLD = 3
    BULLET = 4
    BULLET2 = 5
    CHECKBOX = 6
    CHECKBOX_CHECKED = 7

class Paragraph:
    renderer: 'Renderer'
    contents: List[FormattedText]
    start_id: str
    style: ParagraphStyle

    def __init__(self, renderer: 'Renderer', contents: List[FormattedText], start_id: str, style: ParagraphStyle):
        self.renderer = renderer
        self.contents = contents
        self.start_id = start_id
        self.style = style

    @classmethod
    def from_dict(cls, renderer: 'Renderer', paragraph):
        return cls(
            renderer,
            [FormattedText.from_dict(renderer, formatted_text) for formatted_text in paragraph['contents']],
            paragraph['startId'],
            ParagraphStyle(paragraph['style'])
        )