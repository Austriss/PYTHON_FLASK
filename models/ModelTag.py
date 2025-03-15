import dataclasses


@dataclasses.dataclass
class ModelTag:
    tag_id: int = 0
    label: str = ""
    is_deleted: bool = False
