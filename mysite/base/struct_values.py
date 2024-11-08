from django.template.defaultfilters import filesizeformat

from wagtail.blocks import StructValue


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
