from collections import OrderedDict
from pandas import DataFrame
import httpx
from makefun import create_function

from globals import MAX_URL_SIZE, BASE_URL
from url import URLFactory
from models.dataset import Attribute
from models.api import CompactDataResponse, SeriesItem
from utils import is_non_string_iterable


class Dataset:
    
    MAX_URL_SIZE = MAX_URL_SIZE - len(BASE_URL)
    
    def __init__(self, 
                 dataset_id: str,
                 parameters: list[Attribute],
                 observation_attrs: list[Attribute],
                 series_attrs: list[Attribute],
                 annotations: dict[str, str],
                 **kwargs):
        
        # Set direct information
        self.id = dataset_id
        
        # Set general info based on annotations
        self.info = annotations
        for key, value in annotations.items():
            if hasattr(self, key):
                key = 'info_' + key    
            setattr(self, key, value)
        
        # Set info and data types for parameters and attributes
        self._parameters_info = {param.name: param for param in parameters}
        self.parameters = tuple(param.name for param in parameters)
        
        # Set attributes info and data types
        self._obs_attrs_info = {attr.name: attr for attr in observation_attrs}
        self.obs_attrs = tuple(attr.name for attr in observation_attrs)
        
        self._series_attrs_info = {attr.name: attr for attr in series_attrs}
        self.series_attrs = tuple(attr.name for attr in series_attrs)
        
        # Create data model for the series in the dataset and the expected response
        series_attrs_types = {attr.name: attr.as_type() for attr in [*parameters, *series_attrs]}
        obs_attrs_types = {attr.name: attr.as_type() for attr in observation_attrs}
        
        self.SeriesItemDynamic = SeriesItem.with_fields(obs_attrs_types, series_attrs_types)
        self.CompactDataResponse = CompactDataResponse[self.SeriesItemDynamic]
    
        # Redefine signature of get_data method to match the parameters
        self.get_data = create_function(f"get_data({', '.join(param + '=None' for param in self.parameters)})", self.get_data)
        
    def get_data(self, *args, **kwargs) -> list[DataFrame]:
        """Get data from the dataset with the given arguments to parameters. 
        Note that:
            * For some datasets the arguments are required, and the IMF API is not explicit about which.
            * There is an upper limit on the size of the url that can be requested."""
        # Assert parameters are valid
        for param in kwargs.keys():
            assert param in self.parameters, f"Parameter {param!r} not available for this dataset. Use one of the following: {self.parameters}."
        
        # Build parameters arguments
        params = OrderedDict()
        for i, param in enumerate(self.parameters):
            args = kwargs.get(param) or (args[i] if i < len(args) else '')
            params[param] = args if is_non_string_iterable(args) else [args]
    
        # Assert parameters' arguments are valid
        for key, values in params.items():
            for value in values:
                assert not value or value in self._parameters_info[key].values, f"Value {value!r} not available for parameter {key!r}."
        
        # Build url
        url = URLFactory.compact_data(self.id, params.values())
        
        # Assert size of url is not too large (max is 323...)
        assert len(url) <= MAX_URL_SIZE, f"Requesting url is too large: length ({len(url)}) > max ({MAX_URL_SIZE}), for {url!r}. Choose fewer parameters."
        
        # Get data and assert consistency
        json_data = url.get_json(self._client)
        parsed_data = self.CompactDataResponse.from_raw(json_data)
        
        return [series.to_dataframe() for series in parsed_data.series]   
    
    @staticmethod
    def _build_parameters_string(params_args: list[str, list[str]]) -> str:
        return '.'.join('+'.join(param) if is_non_string_iterable(param) else param
                                 for param in params_args)
    
    def _match_attr(self, key: str) -> Attribute:
        match key.upper():
            case _ as key if key in self._parameters_info:
                return self._parameters_info[key]
            case _ as key if key in self._series_attrs_info:
                return self._series_attrs_info[key]
            case _ as key if key in self._obs_attrs_info:
                return self._obs_attrs_info[key]
            case _:
                raise AttributeError(f"{key!r} is not a component in dataset.")
        
    def values_of(self, key: str) -> list[str] | str:
        """Get the values of a parameter."""
        values = self._match_attr(key).values
        return list(values.keys()) if isinstance(values, dict) else values

    def description_of(self, key: str) -> str:
        """Get the description of a component."""
        attr = self._match_attr(key)
        return attr.desc, attr.values
    
    def __repr__(self):
        return f"Dataset({self.id!r}, parameters={self.parameters})"