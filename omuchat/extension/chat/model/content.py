from __future__ import annotations

from typing import List, Literal, NotRequired, TypedDict

from omuchat.interface.model import Model

type ContentJson = TextContentJson
type Content = TextContent


class ContentComponentJson[T: str](TypedDict):
    type: T
    siblings: NotRequired[List[ContentJson]] | None


class ContentComponent(Model[ContentComponentJson]):
    def __init__(self, type: str, siblings: List[Content] | None = None) -> None:
        self.type = type
        self.siblings = siblings

    @classmethod
    def from_json(cls, json: ContentJson) -> Content:
        match json["type"]:
            case "text":
                return TextContent.from_json(json)
            case _:
                raise ValueError(f"Unknown content type: {json['type']}")

    def json(self) -> ContentComponentJson:
        return ContentComponentJson(
            type=self.type,
            siblings=[sibling.json() for sibling in self.siblings]
            if self.siblings
            else [],
        )


class TextContentJson(ContentComponentJson[Literal["text"]]):
    text: str


class TextContent(ContentComponent, Model[TextContentJson]):
    def __init__(self, text: str, siblings: List[Content] | None = None) -> None:
        super().__init__(type="text", siblings=siblings)
        self.text = text

    def json(self) -> TextContentJson:
        return {
            "type": "text",
            "text": self.text,
            "siblings": [sibling.json() for sibling in self.siblings]
            if self.siblings
            else [],
        }

    @classmethod
    def of(cls, text: str) -> TextContent:
        return cls(text=text)

    @classmethod
    def from_json(cls, json: TextContentJson) -> TextContent:
        return cls(text=json["text"])

    def __str__(self) -> str:
        return self.text


class ImageContentJson(ContentComponentJson[Literal["image"]]):
    url: str
    id: str


class ImageContent(ContentComponent, Model[ImageContentJson]):
    def __init__(
        self, url: str, id: str, siblings: List[Content] | None = None
    ) -> None:
        super().__init__(type="image", siblings=siblings)
        self.url = url
        self.id = id

    def json(self) -> ImageContentJson:
        return {
            "type": "image",
            "url": self.url,
            "id": self.id,
            "siblings": [sibling.json() for sibling in self.siblings]
            if self.siblings
            else [],
        }

    @classmethod
    def of(cls, url: str, id: str) -> ImageContent:
        return cls(url=url, id=id)

    @classmethod
    def from_json(cls, json: ImageContentJson) -> ImageContent:
        return cls(url=json["url"], id=json["id"])

    def __str__(self) -> str:
        return f"[Image: {self.url}]"
