import dataclasses

from models.EnumPostStatus import EnumPostStatus
from models.ModelTag import ModelTag


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
    children_posts: list = dataclasses.field(default_factory=list)
    depth: int = 0
    all_tags: list[ModelTag] = dataclasses.field(default_factory=list)
