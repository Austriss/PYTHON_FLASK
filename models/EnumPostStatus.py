from enum import Enum


class EnumPostStatus(str, Enum):
    not_set = 'not_set'
    draft = 'draft'
    published = 'published'
    deleted = 'deleted'

