from typing import Optional
from urllib.parse import urljoin


class BaseParser:
    def __init__(self, base_url: str):
        self.base_url = base_url

    @staticmethod
    async def _extract_text(
        element,
        selector: Optional[str] = None,
        parent_tag: Optional[str] = None,
        parent_class: Optional[str] = None,
        child_tag: Optional[str] = None,
    ) -> Optional[str]:
        if selector:
            tag = element.select_one(selector)
            return tag.get_text(strip=True) if tag else None

        if parent_tag and parent_class:
            parent = element.find(parent_tag, class_=parent_class)
            if parent:
                if child_tag:
                    child = parent.find(child_tag)
                    return child.get_text(strip=True) if child else None
                return parent.get_text(strip=True)
        return None

    @staticmethod
    async def _extract_attribute(
        element,
        tag: Optional[str] = None,
        attribute: Optional[str] = None,
        selector: Optional[str] = None,
        parent_class: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> Optional[str]:

        if selector:
            tag_element = element.select_one(selector)
            if tag_element and attribute in tag_element.attrs:
                value = tag_element[attribute]
                return urljoin(base_url, value) if base_url else value

        parent = element.find("div", class_=parent_class) if parent_class else element
        if parent and tag:
            tag_element = parent.find(tag)
            if tag_element and attribute and tag_element.has_attr(attribute):
                value = tag_element[attribute]

                return urljoin(base_url, value) if base_url else value
        return None

    @staticmethod
    def _add_book(item: dict, books: list):
        title = item.get("name")
        price = item.get("price")
        url = item.get("url")
        if title:
            books.append(
                {
                    "title": title,
                    "price": price,
                    "url": url,
                }
            )
