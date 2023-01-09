"""Represents the IMF Dataflow API response."""

from pydantic import BaseModel, Field, validator, ValidationError
from exceptions import WrapperException

class DatasetItem(BaseModel):
    """Represents a dataset item in the IMF's API `/Dataflow` response."""
    id: str = Field(..., alias='KeyFamilyRef')
    desc: str = Field(..., alias='Name')

    # Processing
    @validator('id', pre=True)
    def process_identifier(cls, v):
        return v['KeyFamilyID'] if isinstance(v, dict) else v
    
    @validator('desc', pre=True)
    def process_description(cls, v):
        return v.get('#text', '') if isinstance(v, dict) else v

class DataflowResponse(BaseModel):
    """Represents IMF's API `/Dataflow` response, comprised of a list of datasets."""
    datasets: list[DatasetItem]
    
    # Processing
    @classmethod
    def from_raw(cls, json: dict):
        match json:
            case {
                    'Structure': {
                        'Dataflows': {
                            'Dataflow': datasets
                        }
                    }
                }: 
                return cls(datasets=datasets)
            case _:
                raise WrapperException("Necessary data not found in json.")