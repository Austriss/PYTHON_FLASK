
import dataclasses

@dataclasses.dataclass
class ModelUser:
    user_id: int = 0
    email: str = ""
    password_hash: str = ""