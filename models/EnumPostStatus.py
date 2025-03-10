import enum


class EnumPostStatus(enum.Enum):
    not_set = 'not_set'
    draft = 'draft'
    published = 'published'
    deleted = 'deleted'
