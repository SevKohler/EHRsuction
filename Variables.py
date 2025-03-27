from enum import Enum

class Platforms(Enum):
    BETTER = "better"
    EHRBASE = "ehrbase"


class ExportType(Enum):
    CANONICAL = "canonical"
    FLAT = "flat"
