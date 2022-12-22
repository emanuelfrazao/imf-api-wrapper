"""Module with wrapper class for the IMF's (weird) API.

The API follows a specific logic, which the wrapper superficially replicates, namely - it organizes itself with:
* a list of datasets (accessible by the method `datasets`)
* for each dataset, a specific set of fields and options on the data (accessible by the method `datastruct`)
* for each dataset, the corresponding data (accessible by the method `data`)
"""


# outsourced imports
from functools import cached_property
from requests import Session
from re import search
from makefun import create_function
from collections import OrderedDict
from pandas import DataFrame

# local imports
from config import BASE_URL, BASE_HEADERS, MAX_URL_SIZE
from url import URL
from models.imf.dataflow import DataflowResponse
from models.imf.datastructure import DataStructureResponse
from models.imf.compactdata import CompactDataResponse, SeriesItem
from models.wrapper.dataset import Attribute
from utils import is_non_string_iterable

__all__ = [
    'IMFWrapper',
]



class Dataset:
    
    def __init__(self, 
                 dataset_id: str,
                 parameters: list[Attribute],
                 observation_attrs: list[Attribute],
                 series_attrs: list[Attribute],
                 annotations: dict[str, str],
                 **kwargs):
        
        # Set direct information
        self.id = dataset_id
        self._session = kwargs.pop('session', Session())
        
        # Build base url for downloading data
        self._base_url = URL(BASE_URL).add_path('CompactData').add_path(dataset_id)
        
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
        url: URL = self._base_url.copy() \
            .add_positional_arguments(params.values())
        
        # Assert size of url is not too large (max is 323...)
        assert len(url) <= MAX_URL_SIZE, f"Requesting url is too large: length ({len(url)}) > max ({MAX_URL_SIZE}), for {url!r}. Choose fewer parameters."
        
        # Get data and assert consistency
        json_data = url.get_json(self._session)
        parsed_data = self.CompactDataResponse.from_raw(json_data)
        
        return [series.to_dataframe() for series in parsed_data.series]   
    
    
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
    

class IMFWrapper:

    def __init__(self):
        """Initialize the IMFWrapper class, making a request to the IMF API to get the available datasets."""
        # Set session
        self.session = Session()
        
        # Set datasets available
            ## Get response from corresponding url
        url = URL(BASE_URL).add_path('Dataflow')
        json_data = url.get_json(self.session)
        
            ## Parse json data into datasets
        parsed_data = DataflowResponse.from_raw(json_data)
        self._datasets = {dataset.id: dataset.desc for dataset in parsed_data.datasets}
        

    @property
    def datasets(self,
                 without_dates: bool | None = True) -> dict[str, str]:
        """Mapping of datasets to their descriptions.
        It default to the datasets that do not correspond to a specific time period, since those are inconsistent.
        """
        if without_dates is None:
            return self._datasets
        
        has_date = lambda description: search(r"20\d{2}", description) is not None
        
        return {dataset_id: description 
                    for dataset_id, description in self._datasets.items() 
                        if without_dates ^ has_date(description)}
    
    def get_dataset(self,
                    dataset_id: str) -> Dataset:
        
        # Assert dataset is available
        assert dataset_id in self._datasets, f"Dataset {dataset_id!r} not found in the list of datasets available. Call `datasets` to get the list of available datasets."
        
        # Get response from url
        url = URL(BASE_URL).add_path('DataStructure').add_path(dataset_id)
        json_data = url.get_json(self.session)
        
        # Parse json data
        parsed_data = DataStructureResponse.from_raw(json_data)
        
        # Extract information on concepts and codes (required for filling information on parameters and attributes)
        concepts_info = {concept.name: concept for concept in parsed_data.concepts}
        codes_info = {code.id: code for code in parsed_data.codes}
        
        # Build parameters, attributes and annotations
        parameters, obs_attrs, series_attrs = [], [], []
        
        for item in parsed_data.parameters:
            parameters.append(Attribute(name=item.name, desc=concepts_info[item.name].desc, values=codes_info[item.code_id].values_dict))
        
        for item in parsed_data.attributes:
            name = item.name
            desc = concepts_info[name].desc
            
            if item.is_obs:
                obs_attrs.append(Attribute(name=name, desc=desc, values=concepts_info[name].value_type))
            else:
                series_attrs.append(Attribute(name=name, desc=desc, values=codes_info[item.code_id].values_dict))
                
        annotations = {annotation.title: annotation.desc for annotation in parsed_data.annotations}       
        
        # Create and return dataset
        return Dataset(dataset_id, parameters, obs_attrs, series_attrs, annotations)


if __name__ == '__main__':
    imf = IMFWrapper()
    pcps = imf.get_dataset('PCPS')