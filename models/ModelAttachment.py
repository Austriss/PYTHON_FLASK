import dataclasses

@dataclasses.dataclass
class ModelAttachment:
    attachment_id: int = 0
    post_id: int = 0
    attachment_uuid: str = ""
    is_deleted: bool = False
