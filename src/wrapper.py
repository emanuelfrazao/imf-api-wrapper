"""Module with wrapper class for the IMF's (weird) API.

The API follows a specific logic, which the wrapper superficially replicates, namely - it organizes itself with:
* a list of datasets (accessible by the method `datasets`)
* for each dataset, a specific set of fields and options on the data (accessible by the method `datastruct`)
* for each dataset, the corresponding data (accessible by the method `data`)
"""


# outsourced imports
from httpx import Client, AsyncClient, Response
from re import search
from json import JSONDecodeError
from time import perf_counter, sleep
from collections import deque

# local imports
from globals import global_last_requests, BASE_URL, BASE_HEADERS, MAX_URL_SIZE
from exceptions import LimitExceeded, UnknownServerException
from url import URLFactory
from dataset import Dataset
from models.dataset import Attribute
from models.api import DataflowResponse, DataStructureResponse, CompactDataResponse, SeriesItem
from utils import is_non_string_iterable    

class IMFWrapper:

    sync_client = lambda self: Client(base_url=BASE_URL, headers=BASE_HEADERS)
    async_client = lambda self: AsyncClient(base_url=BASE_URL, headers=BASE_HEADERS)
    
    def __init__(self):
        """Initialize the IMFWrapper class, already making a request to the IMF API to get the available datasets.
        """
        # Set last requests queue for managing maximum requests per second
        # self._last_requests = deque(maxlen=10)
        
        # Make request and set request time
        with self.sync_client() as client:
            response = client.get("/Dataflow")
        
        global_last_requests.append(perf_counter())
        print(global_last_requests)
        self._check_response(response)
        
        # Parse json data into datasets, and set them as a property
        parsed_data = DataflowResponse.from_raw(response.json())
        self._datasets = {dataset.id: dataset.desc for dataset in parsed_data.datasets}
        
    def _check_response(self,
                        response: Response) -> None:
        """Process the status code of a response from the IMF API.
        """
        match response.status_code:
            case 200: pass
            case 302: raise LimitExceeded("The limit of requests per day has been exceeded.")
            case _:   raise UnknownServerException(f"Request to IMF API failed with status code {response.status_code}.")
        
        if "application/json" not in response.headers.get("Content-Type", ''):
            raise UnknownServerException(f"Response from IMF API is not a valid JSON object.")
    
    @staticmethod
    def _dataset_has_date(description) -> bool:
        """Check if a dataset description contains a date."""
        return search(r"20\d{2}", description) is not None
    
    @property
    def datasets(self,
                 without_dates: bool | None = True) -> dict[str, str]:
        """Mapping of datasets to their descriptions.
        It default to the datasets that do not correspond to a specific time period, since those are inconsistent.
        """
        # Return all datasets if flag is None
        if without_dates is None:
            return self._datasets
        
        # Otherwise, filter accordingly and return
        return {dataset_id: description 
                    for dataset_id, description in self._datasets.items() 
                        if without_dates ^ self._dataset_has_date(description)}
    
    def get_dataset(self,
                    dataset_id: str) -> Dataset:
        
        # Assert dataset is available
        assert dataset_id in self._datasets, \
            f"Dataset {dataset_id!r} not found in the list of datasets available. Call `datasets` to get the list of available datasets."
        
        # Check whether we need to wait for the next request, and do so if necessary
        if len(global_last_requests) == 10 and ( required_wait := perf_counter() - global_last_requests.popleft() ) < 5:
            sleep(required_wait)
        
        # Make request and set request time
        with self.sync_client() as client:
            response = client.get(f"/DataStructure/{dataset_id}")
        
        global_last_requests.append(perf_counter())
        self._check_response(response)
        
        # Parse json data into dataset information
        parsed_data = DataStructureResponse.from_raw(response.json())
        
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
