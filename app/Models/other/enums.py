from enum import Enum

class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"


class ValueEnumOperation(str, Enum):
    INCREMENT ='increment'
    DECREMENT = 'decrement'