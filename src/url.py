from utils import is_non_string_iterable
from requests import Session
from exceptions import WrapperException

class URLFactory:
    
    BASE = "http://dataservices.imf.org/REST/SDMX_JSON.svc"
    
    @classmethod
    def dataflow(self) -> str:
        return f"{self.BASE}/Dataflow"
    
    @classmethod
    def data_structure(self, dataset_id: str) -> str: 
        return f"{self.BASE}/DataStructure/{dataset_id}"
    
    @classmethod
    def metadata_structure(self, dataset_id: str) -> str:
        return f"{self.BASE}/MetadataStructure/{dataset_id}"
    
    @classmethod
    def compact_data(self, 
                    dataset_id: str, 
                    parameters_args: list[list[str] | str],
                    start: str = '1900',
                    end: str = '2100') -> str:
        
        arguments_string = self._build_arguments_string(parameters_args)
        
        return f"{self.BASE}/CompactData/{dataset_id}/{arguments_string}?startPeriod={start}&endPeriod={end}"
    
    @classmethod
    def generic_metadata(self, 
                         dataset_id: str, 
                         parameters_args: list[list[str] | str],
                         start: str = '1900',
                         end: str = '2100') -> str:
        
        arguments_string = self._build_arguments_string(parameters_args)
        
        return f"{self.BASE}/GenericMetadata/{dataset_id}/{arguments_string}?startPeriod={start}&endPeriod={end}"
    
    @staticmethod
    def _build_arguments_string(parameters_args: list[list[str] | str],
                                args_sep: str = '+',
                                params_sep: str = '.') -> str:
        
        return params_sep.join(args_sep.join(param) if is_non_string_iterable(param) else param
                                 for param in parameters_args)

    