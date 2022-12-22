from typing import Generic, Type, TypeVar
from pydantic import BaseModel, Field, create_model
from pydantic.generics import GenericModel
from pandas import DataFrame

from exceptions import WrapperException

class ObservationItem(BaseModel):
    
    @classmethod
    def with_fields(cls, obs_attrs: dict[str, Type]):
        return create_model('ObservationItemDynamic', 
                            __base__=cls, 
                            **{name: (type_, Field(None, alias='@' + name)) for name, type_ in obs_attrs.items()})
        
    
class SeriesItem(BaseModel):
    obs: list[ObservationItem]
    
    @classmethod
    def with_fields(cls, obs_attrs: dict[str, Type], series_attrs: dict[str, Type]):
        
        ObservationItemDynamic = ObservationItem.with_fields(obs_attrs)
        
        return create_model('SeriesItemDynamic', 
                            __base__=cls,
                            obs=(list[ObservationItemDynamic], Field(alias='Obs', default_factory=lambda: [])),
                            **{name: (type_, Field(None, alias='@' + name)) for name, type_ in series_attrs.items()})
    
    def to_dataframe(self):
        dataframe = DataFrame.from_dict(obs.dict() for obs in self.obs)
        dataframe.attrs.update((name, value) for name, value in self.__dict__.items() if name != 'obs')
        return dataframe
    
    @property
    def attrs(self):
        return tuple(value for name, value in self.__dict__.items() if name != 'obs')


SeriesItemGeneric = TypeVar('SeriesItemGeneric', bound=SeriesItem)

class CompactDataResponse(GenericModel, Generic[SeriesItemGeneric]):
    series: list[SeriesItemGeneric]
    
    @classmethod
    def from_raw(cls, json: dict):
        match json:
            case {"CompactData": {"DataSet": {"Series": series}}}:
                return cls(series=series)
            case {"CompactData": {"DataSet": _}}:
                return cls(series=[])
            case _:
                raise WrapperException("Invalid json response.")
