
from dataclasses import dataclass
from typing import List, Optional
    
@dataclass(frozen=True)
class Parameter:
    name: str
    code: str
    desc: str
    values: list[str]
    values_desc: dict[str, str]
    
@dataclass(frozen=True)
class ObservationAttribute:
    name: str
    desc: str
    value_type: str
    
@dataclass(frozen=True)
class SeriesAttribute:
    name: str
    code: str
    desc: str
    values: list[str]
    values_desc: dict[str, str]

class DatasetStructure:
    """A data structure for the IMF data."""
    
    def __init__(self, dataset, 
                 parameters: list[Parameter],
                 ser_attrs: list[SeriesAttribute],
                 obs_attrs: list[ObservationAttribute]):
        self.dataset = dataset
        
        self.params = [param.name for param in parameters]
        self._parameters = {param.name: param for param in parameters}
        
        self.ser_attrs = [attr.name for attr in ser_attrs]
        self._series_attributes = {attr.name: attr for attr in ser_attrs}
        
        self.obs_attrs = [attr.name for attr in obs_attrs]
        self._observation_attributes = {attr.name: attr for attr in obs_attrs}
    
    def _assert_is_component(self, key):
        assert key in self._parameters or key in self._observation_attributes or key in self._series_attributes, \
            f"{key!r} is not a parameter, observation attribute nor a series attribute for this dataset."
    
    def _assert_has_code(self, key):
        assert key in self._parameters or key in self._series_attributes, \
            f"{key!r} is not a parameter nor a series attribute for this dataset."
    
    def _assert_has_type(self, key):
        assert key in self._observation_attributes, \
            f"{key!r} is not an observation attribute for this dataset."
    
    def code(self, key: str):
        self._assert_has_code(key)
        return (self._parameters.get(key) or self._series_attributes.get(key)).code
    
    def desc(self, key):
        self._assert_is_component(key)
        return (self._parameters.get(key) or self._series_attributes.get(key) or self._observation_attributes.get(key)).desc
    
    def values(self, key):
        self._assert_has_code(key)
        return (self._parameters.get(key) or self._series_attributes.get(key)).values
    
    def value_type(self, key):
        self._assert_has_type(key)
        return self._observation_attributes[key].value_type
    
    def values_desc(self, key, value = None):
        self._assert_has_code(key)
        desc = self._parameters[key].values_desc
        if value is None:
            return desc
        else:
            assert value in desc, f"{value!r} is not a valid value for {key!r}."
            return desc[value]
    
    def __repr__(self):
        return f"DatasetStructure({self.dataset}, params={self.params})"