import logging

from django.template.defaultfilters import filesizeformat
from django.utils.functional import cached_property

from wagtail.blocks import StructValue

logger = logging.getLogger(__name__)


class RatingsStructValue(StructValue):

    def _round_to_nearest_5(self, x):
        return 5 * round(x / 5)

    @cached_property
    def stats(self):
        five = self.get("five", 0)
        four = self.get("four", 0)
        three = self.get("three", 0)
        two = self.get("two", 0)
        one = self.get("one", 0)

        weighted_sum = 5 * five + 4 * four + 3 * three + 2 * two + 1 * one

        total = five + four + three + two + one
        avg_rating = weighted_sum / total
        score = round(avg_rating, 1)
        stars = round(avg_rating)

        star_percentages = {
            "5": self._round_to_nearest_5(100 * five / total),
            "4": self._round_to_nearest_5(100 * four / total),
            "3": self._round_to_nearest_5(100 * three / total),
            "2": self._round_to_nearest_5(100 * two / total),
            "1": self._round_to_nearest_5(100 * one / total),
        }

        logger.info("total:%s" % total)
        logger.info("score:%s" % score)
        logger.info("stars:%s" % stars)
        logger.info("star_percentages:%s" % star_percentages)

        return total, score, stars, star_percentages

    def get_total_ratings(self):
        return self.stats[0]

    def get_score(self):
        return self.stats[1]

    def get_star_colors(self):
        stars = self.stats[2]
        return ["gold"] * stars + ["lightgrey"] * (5 - stars)

    def get_star_percentages(self):
        return self.stats[3]


class LinkStructValue(StructValue):
    def get_url(self):
        link = self.get("link")
        page = self.get("page")
        document = self.get("document")

        return link or page.url or document.url or ""

    def get_title(self):
        if title := self.get("title"):
            return title

        if page := self.get("page"):
            page = page.specific
            return page.title

        document = self.get("document")

        return document.title or ""

    def get_link_type(self) -> str:
        if self.get("page"):
            return "internal"

        if self.get("document"):
            return "document"

        return "external"

    def get_file_size(self) -> str:
        if document := self.get("document"):
            return filesizeformat(document.file.size)
        return ""

    def get_extension_type(self) -> str:
        if document := self.get("document"):
            return document.file_extension.upper()
        return ""
