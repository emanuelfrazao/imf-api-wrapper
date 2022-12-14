"""Module with wrapper class for the IMF's (weird) API.

The API follows a specific logic, which the wrapper superficially replicates, namely - it organizes itself with:
* a list of datasets (accessible by the method `datasets`)
* for each dataset, a specific set of fields and options on the data (accessible by the method `datastruct`)
* for each dataset, the corresponding data (accessible by the method `data`)
"""
# outsourced imports
from ast import Tuple
from functools import cache
from typing import Optional, Dict, NewType
from requests import Session
from pandas import DataFrame
from enum import Enum

# local imports
from url import URLBuilder
from utils import get_nested_value
from exceptions import ServerException, WrapperException

class IMFWrapper:
    BASE_URL = "http://dataservices.imf.org/REST/SDMX_JSON.svc"

    def __init__(self):
        """Initialize the IMFWrapper class."""
        self.session = Session()
    
    @cache
    def datasets(self,
                 dataset_filter: Optional[str] = None,
                 description_filter: Optional[str] = None,
                 with_dates: Optional[bool] = None) -> DataFrame:
        """Returns a DataFrame with the list of the datasets currently registered for the IMF API.

        Args:
            dataset_filter (Optional[str], optional): a string to filter on the dataset. Defaults to None.
            description_filter (Optional[str], optional): a string to filter on the description. Defaults to None.
            with_dates (Optional[bool], optional): whether to filter for the datasets with specific dates. Defaults to None.

        Raises:
            Exception: _description_

        Returns:
            DataFrame: _description_
        """
        
        # Build url
        url_builder = URLBuilder(self.BASE_URL)
        url = url_builder.add_path('Dataflow').to_string()
        
        # Get response from url
        response = self.session.get(url)
        if response.status_code != 200:
            raise WrapperException(f"Unknown reason for error on url {url!r}.")
            
        # Get list of dataset items from response
        json_data = response.json()
        items = json_data['Structure']['Dataflows']['Dataflow']
        
        # Build data-frame
        dataframe = DataFrame(data=[(item['KeyFamilyRef']['KeyFamilyID'], item['Name']['#text']) for item in items],
                                columns=('dataset', 'description'))
        
        # Sort, and optionally filter
        dataframe.sort_values(by='dataset', ignore_index=True, inplace=True)
        if with_dates is not None:
            dates_mask = dataframe['description'].str.contains(r"20\d{2}")
            dataframe = dataframe[dates_mask] if with_dates else dataframe[~ dates_mask]
        
        return dataframe
            
    def datastruct(self,
                   dataset: str) -> dict:
        
        # Assert proper dataset
        available_datasets = self.datasets()['dataset'].to_list()
        assert dataset in available_datasets, \
            f"""Dataset {dataset!r} not found in the list of datasets available. 
            Call `datasets` method to see the list of available datasets."""
        
        # Build url
        url_builder = URLBuilder(self.BASE_URL)
        url = url_builder.add_path('DataStructure').add_path(dataset).to_string()
        
        # Get response from url
        response = self.session.get(url)
        if response.status_code != 200:
            raise WrapperException(f"Unknown reason for error on url {url!r}.")
        
        # Get dataset items on codes, concepts and components - from response
        json_data = response.json()['Structure']
        components_items:   dict[str, str | list] = json_data['KeyFamilies']['KeyFamily']['Components']
        code_items:         list[dict] = json_data['CodeLists']['CodeList']
        concept_items:      list[dict] = json_data['Concepts']['ConceptScheme']['Concept']
        
        # Build components dictionary and return
            ## Create dictionary with information on components items
        components: TwoLevelDict = dict(build_component(component_type, item)
                                        for component_type, items in components_items.items()
                                            for item in (items if isinstance(items, list) else [items]))
        
            ## Extract extra information on code components
        codes_info = dict(build_code(item) for item in code_items)
            
            ## Extract extra information on non-code components
        value_types_info = dict(build_value_type(item) for item in concept_items)
        
            ## Add information on components items
        filled_components = fill_components(components, codes_info, value_types_info)
        
        return filled_components



class ComponentType(str, Enum):
    param: str = 'parameter'
    series_attr: str = 'series_attribute'
    obs_attr: str = 'observation_attribute'
    unknown: str = 'unknown'
    
    @classmethod
    def from_item_type(cls, item_type: str):
        match item_type:
            case 'Dimension': 
                return cls.param
            case 'Attribute': 
                return cls.series_attr
            case 'TimeDimension' | 'PrimaryMeasure': 
                return cls.obs_attr
            case other: 
                return cls.unknown
            
OneLevelDict = NewType('OneLevelDict', Dict[str, object])
TwoLevelDict = NewType('TwoLevelDict', Dict[str, OneLevelDict])
            
def build_component(component_type, item) -> tuple[str, dict[str, str]]:
    return item['@conceptRef'], {
        'type': ComponentType.from_item_type(component_type), 
        'code': item.get('@codelist')
    }
    
def _extract_code_value_info(value: dict) -> dict[str, str]:
    return {'value': value['@value'], 'description': value['Description']['#text']}

def build_code(item) -> tuple[str, dict[str, str | list[str]]]:
    values = item['Code'] if isinstance(item['Code'], list) else [item['Code']]
    
    return item['@id'], {
        'description': (item.get('Description') or item['Name'])['#text'],
        'values': [_extract_code_value_info(value) for value in values]
    }

def build_value_type(item) -> tuple[str, dict[str, str]]:
    return item['@id'], {'value_type': item.get('TextFormat', {}).get('@textType')}

def fill_components(components: TwoLevelDict, 
                    codes_info: TwoLevelDict, 
                    value_types_info: OneLevelDict) -> TwoLevelDict:
    
    filled_components = {}
    for component, features in components.items():
        # Fill component with code info if code is present
        if (code := features['code']) in codes_info:
            filled_components[component] = {**features, **codes_info[code]}
        
        # Fill component with value type info if code is not present (the type should be obs_attribute)
        else:
            assert features['type'] == ComponentType.obs_attr # TODO: right message
            filled_components[component] = {**features, **value_types_info[component]}
            
    return filled_components