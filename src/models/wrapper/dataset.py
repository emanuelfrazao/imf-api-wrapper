from typing import Optional, Literal
from pydantic import BaseModel

class Attribute(BaseModel):
    """This could be a parameter or a series attribute."""
    name: str
    desc: str
    values: dict[str, str] | str
    
    def as_type(self):
        match self.values:
            case v if isinstance(v, dict):
                return Literal[tuple(v.keys())]
            case 'Double':
                return Optional[float]
            case 'DateTime':
                return Optional[str]
            case _:
                return Optional[str]