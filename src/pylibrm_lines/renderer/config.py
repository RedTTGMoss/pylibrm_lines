from typing import List

from pylibrm_lines.pens import PEN_COMBINED_VERSIONS, ALL_PEN_IDS


class RendererConfig:
    def __init__(self, renderer, config_ptr):
        self._renderer = renderer
        self._config = config_ptr

    @property
    def version(self) -> int:
        return self._config.contents.configVersion

    @property
    def use_whitelist(self) -> bool:
        return self._config.contents.useWhitelist

    @use_whitelist.setter
    def use_whitelist(self, value: bool):
        self._config.contents.useWhitelist = value

    @property
    def enable_text(self) -> bool:
        return self._config.contents.enableText

    @enable_text.setter
    def enable_text(self, value: bool):
        self._config.contents.enableText = value

    @property
    def enable_images(self) -> bool:
        return self._config.contents.enableImages

    @enable_images.setter
    def enable_images(self, value: bool):
        self._config.contents.enableImages = value

    @property
    def enable_glyph_highlights(self) -> bool:
        return self._config.contents.enableGlyphHighlights

    @enable_glyph_highlights.setter
    def enable_glyph_highlights(self, value: bool):
        self._config.contents.enableGlyphHighlights = value

    @property
    def enable_backdrop(self) -> bool:
        return self._config.contents.enableBackdrop

    @enable_backdrop.setter
    def enable_backdrop(self, value: bool):
        self._config.contents.enableBackdrop = value

    @property
    def _pen_whitelist(self) -> List[int]:
        return self._config.contents.penWhitelist

    @property
    def _pen_blacklist(self) -> List[int]:
        return self._config.contents.penBlacklist

    @staticmethod
    def _combine_pens(pens: List[int]) -> List[int]:
        for combined_value, combination in PEN_COMBINED_VERSIONS.items():
            if combination[0] in pens and combination[1] in pens:
                pens.append(combined_value)
                # pens.remove(combination[0])
                # pens.remove(combination[1])
        return pens

    @staticmethod
    def _uncombine_pens(pens: List[int]) -> List[int]:
        for combined_value, combination in PEN_COMBINED_VERSIONS.items():
            if combined_value in pens:
                pens.append(combination[0])
                pens.append(combination[1])
                # pens.remove(combined_value)
        return pens

    @property
    def _allowed_pens(self) -> List[int]:
        if self.use_whitelist:
            return [pen for pen in self._pen_whitelist if pen != -1]
        else:
            blacklist = [pen for pen in self._pen_blacklist if pen != -1]
            return [pen for pen in ALL_PEN_IDS if pen not in blacklist]

    @property
    def _disallowed_pens(self) -> List[int]:
        if self.use_whitelist:
            whitelist = [pen for pen in self._pen_whitelist if pen != -1]
            return [pen for pen in ALL_PEN_IDS if pen not in whitelist]
        else:
            return [pen for pen in self._pen_blacklist if pen != -1]

    @property
    def allowed_pens(self) -> List[int]:
        return self._combine_pens(self._allowed_pens)

    @property
    def disallowed_pens(self) -> List[int]:
        return self._combine_pens(self._disallowed_pens)

    def _enable_pen(self, pen_id: int):
        if self.use_whitelist:
            if pen_id in self._pen_whitelist:
                return
            for i in range(len(self._pen_whitelist)):
                if self._pen_whitelist[i] == -1:
                    self._pen_whitelist[i] = pen_id
                    break
        else:
            if pen_id not in self._pen_blacklist:
                return
            for i in range(len(self._pen_blacklist)):
                if self._pen_blacklist[i] == pen_id:
                    self._pen_blacklist[i] = -1
                    break

    def _disable_pen(self, pen_id: int):
        if self.use_whitelist:
            if pen_id not in self._pen_whitelist:
                return
            for i in range(len(self._pen_whitelist)):
                if self._pen_whitelist[i] == pen_id:
                    self._pen_whitelist[i] = -1
                    break
        else:
            if pen_id in self._pen_blacklist:
                return
            for i in range(len(self._pen_blacklist)):
                if self._pen_blacklist[i] == -1:
                    self._pen_blacklist[i] = pen_id
                    break

    def enable_pen(self, pen_id: int):
        if pen_id not in ALL_PEN_IDS:
            raise ValueError(f"Invalid pen ID: {pen_id}")
        if pen_id in PEN_COMBINED_VERSIONS:
            for sub_pen in PEN_COMBINED_VERSIONS[pen_id]:
                self._enable_pen(sub_pen)
        else:
            self._enable_pen(pen_id)

    def disable_pen(self, pen_id: int):
        if pen_id not in ALL_PEN_IDS:
            raise ValueError(f"Invalid pen ID: {pen_id}")
        if pen_id in PEN_COMBINED_VERSIONS:
            for sub_pen in PEN_COMBINED_VERSIONS[pen_id]:
                self._disable_pen(sub_pen)
        else:
            self._disable_pen(pen_id)