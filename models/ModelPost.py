import dataclasses

from models.EnumPostStatus import EnumPostStatus


@dataclasses.dataclass
class ModelPost:
    post_id: int = 0
    url_slug: str = ""
    title: str = ""
    body: str = ""
    thumbnail_uuid: str = ""
    created: int = 0
    modified: int = 0
    status: EnumPostStatus = EnumPostStatus.not_set # ALT + ENTER

    parent_post_id: int = None
    children_posts = []
    depth: int = 0

    all_tags = []