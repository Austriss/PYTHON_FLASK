import dataclasses


@dataclasses.dataclass
class ModelTags:
    tag_id: int = 0
    label: str = ""
    is_deleted: bool = False
