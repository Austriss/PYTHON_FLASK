import dataclasses

@dataclasses.dataclass
class ModelImage:
    image_id: int = 0
    image_uuid: str = ""
    post_id: int = 0
    is_deleted: bool = False
