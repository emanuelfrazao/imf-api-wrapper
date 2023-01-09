from typing import Literal
from pydantic import BaseModel, Field, validator

from exceptions import WrapperException

def extract_text(value: dict[str, str]):
    return value.get('#text', '')

class ConceptItem(BaseModel):
    name: str = Field(..., alias='@id')
    desc: str = Field(..., alias='Name')
    value_type: str | None = Field(None, alias='TextFormat')
    
    # Processing
    process_description = validator('desc', pre=True, allow_reuse=True)(extract_text)
    
    @validator('value_type', pre=True)
    def process_value_type(cls, value: dict[str, str]):
        return value.get('@textType', None)

class _CodeValueItem(BaseModel):
    value: str = Field(..., alias='@value')
    desc: str = Field(..., alias='Description')
    
    # Processing
    process_description = validator('desc', pre=True, allow_reuse=True)(extract_text)
    
class CodeItem(BaseModel):
    id: str = Field(..., alias='@id')
    values: list[_CodeValueItem] = Field(..., alias='Code')
    
    @property
    def values_dict(self):
        return {value.value: value.desc for value in self.values}
    
    # Processing
    @validator('values', pre=True)
    def process_values(cls, v: list | object):
        return v if isinstance(v, list) else [v]

class ParameterItem(BaseModel):
    name: str = Field(..., alias='@conceptRef')
    code_id: str = Field(..., alias='@codelist')

class AttributeItem(BaseModel):
    name: str = Field(..., alias='@conceptRef')
    code_id: str | None = Field(None, alias='@codelist')
    level: Literal['series', 'observation'] = Field('observation', alias='@attachmentLevel')
    
    @property
    def is_obs(self):
        return self.level == 'observation'
    
    # Processing
    @validator('level', pre=True)
    def process_level(cls, v: str):
        return 'observation' if v is None else v.lower()
    
    
    
class AnnotationItem(BaseModel):
    title: str = Field(..., alias='AnnotationTitle')
    desc: str = Field(..., alias='AnnotationText')
    
    # Post-processing
    @validator('title', pre=False)
    def process_title(cls, v: str):
        return v.strip().lower().replace(' ', '_')
    
    # Pre-processing
    process_description = validator('desc', pre=True, allow_reuse=True)(extract_text)


class DataStructureResponse(BaseModel):
    codes: list[CodeItem]
    concepts: list[ConceptItem]
    parameters: list[ParameterItem]
    attributes: list[AttributeItem]
    annotations: list[AnnotationItem]
    
    # Processing
    @classmethod
    def from_raw(cls, json: dict):
        match json:
            case {
                    'Structure': {
                        'CodeLists': {
                            'CodeList': codes
                        },
                        'Concepts': {
                            'ConceptScheme': {
                                'Concept': concepts
                            }
                        },
                        'KeyFamilies': {
                            'KeyFamily': {
                                'Components': {
                                    'Dimension': parameters,
                                    'TimeDimension': time_attr,
                                    'PrimaryMeasure': value_attr,
                                    'Attribute': other_attrs
                                },
                                'Annotations': {
                                    'Annotation': annotations
                                },
                            }
                        }
                    }
                }:
                return cls(
                    codes=codes,
                    concepts=concepts,
                    parameters=parameters,
                    attributes=[time_attr, value_attr, *other_attrs],
                    annotations=annotations
                )
                
            case _:
                raise WrapperException("Necessary data not found in json.")