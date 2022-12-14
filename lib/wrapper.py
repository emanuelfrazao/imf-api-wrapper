"""Module with wrapper functions for the IMF (weird) API."""
from typing import Optional
import requests
from pandas import DataFrame

from url import URLBuilder
from utils import get_nested_value

BASE_URL = "http://dataservices.imf.org/REST/SDMX_JSON.svc"

def datasets(dataset_filter: Optional[str] = None,
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
    # Set fixed required variables
    KEYS_TO_DATA = ('Structure', 'Dataflows', 'Dataflow')
    url = URLBuilder.dataflow()
    
    # Get response from url
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error {response.status_code} for url {url}")
    
    # Get data from response
    json_data = response.json()
    items = get_nested_value(json_data, KEYS_TO_DATA)
    
    # Build data-frame
    dataframe = DataFrame(data=[(item['KeyFamilyRef']['KeyFamilyID'], item['Name']['#text']) for item in items],
                            columns=('dataset', 'description'))
    
    # Sort, and optionally filter
    dataframe.sort_values(by='dataset', ignore_index=True, inplace=True)
    if with_dates is not None:
        dates_mask = dataframe['description'].str.contains(r"20\d{2}")
        dataframe = dataframe[dates_mask] if with_dates else dataframe[~ dates_mask]
        
    
    return dataframe
        

        
def datastruct
        