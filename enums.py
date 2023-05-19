import enum


class Gender(enum.Enum):
    Male = 'M'
    Female = 'F'
    Other = '?'

    @classmethod
    def choices(cls):
        return [(choice.value) for choice in cls]
