from dataclasses import dataclass
from enum import Enum
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from pylibrm_lines.renderer import Renderer


@dataclass
class TextFormattingOptions:
    bold: bool
    italic: bool
    deletedLength: int

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


class FormattedText:
    renderer: 'Renderer'
    text: str
    formatting: TextFormattingOptions

    def __init__(self, renderer: 'Renderer', text: str, formatting: TextFormattingOptions):
        self.renderer = renderer
        self._text = text
        self._formatting = formatting

    @classmethod
    def from_dict(cls, renderer, formatted_text):
        return cls(
            renderer,
            formatted_text['text'],
            TextFormattingOptions.from_dict(formatted_text['formatting']),
        )

    @property
    def text(self) -> str:
        return self._text

    @property
    def formatting(self) -> TextFormattingOptions:
        return self._formatting


class ParagraphStyle(Enum):
    BASIC = 0
    PLAIN = 1
    HEADING = 2
    BOLD = 3
    BULLET = 4
    BULLET2 = 5
    CHECKBOX = 6
    CHECKBOX_CHECKED = 7
    CHECKBOX_TAB = 8
    CHECKBOX_TAB_CHECKED = 9
    NUMBERED = 10
    NUMBERED_TAB = 11


class ParagraphStyleNew:
    legacy_style: ParagraphStyle

    def __init__(self, legacy_style: ParagraphStyle, base_style: int, style_properties: int, tab_offset: float,
                 tabbed: int, is_legacy: bool = True):
        self.legacy_style = legacy_style
        self.base_style = base_style
        self.style_properties = style_properties
        self.tab_offset = tab_offset
        self.tabbed = tabbed
        self.is_legacy = is_legacy
        self.extra = {}

    @classmethod
    def from_dict(cls, data: dict):
        new = cls(
            ParagraphStyle(data.get('legacyStyle')),
            data.get('baseStyle'),
            data.get('styleProperties'),
            data.get('tabOffset'),
            data.get('tabbed'),
            is_legacy=data.get('isLegacy', True),
        )
        new.extra['_fontSize'] = data.get('_fontSize')
        new.extra['_styleHeight'] = data.get('_styleHeight')
        new.extra['_styleLabel'] = data.get('_styleLabel')


class Paragraph:
    renderer: 'Renderer'
    contents: List[FormattedText]
    start_id: str
    style: ParagraphStyle

    def __init__(self, renderer: 'Renderer', contents: List[FormattedText], start_id: str, style: ParagraphStyleNew):
        self.renderer = renderer
        self._contents = contents
        self._start_id = start_id
        self._style = style

    @classmethod
    def from_dict(cls, renderer: 'Renderer', paragraph):
        return cls(
            renderer,
            [FormattedText.from_dict(renderer, formatted_text) for formatted_text in paragraph['contents']],
            paragraph['startId'],
            ParagraphStyleNew.from_dict(paragraph['style'])
        )

    @property
    def contents(self) -> List[FormattedText]:
        return self._contents

    @property
    def start_id(self) -> str:
        return self._start_id

    @property
    def style(self) -> ParagraphStyle:
        return self._style
