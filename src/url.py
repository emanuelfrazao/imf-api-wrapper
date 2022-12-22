from utils import is_non_string_iterable
from requests import Session
from exceptions import WrapperException

class URL:
    
    def __init__(self, base):
        self._url = base
        
    def add_path(self, subpath) -> 'URL':
        self._url = f"{self._url}/{subpath}"
        return self
    
    def add_paths(self, subpaths) -> 'URL':
        for subpath in subpaths:
            self.add_path(subpath)
        return self
        
    def add_positional_arguments(self, parameters_args: list[str | list[str]], args_sep='+', params_sep='.') -> 'URL':
        
        arguments_string = params_sep.join(args_sep.join(param) if is_non_string_iterable(param) else param
                                       for param in parameters_args)
        self._url = f"{self._url}/{arguments_string}"
        return self
    
    def add_query(self, **options: str) -> 'URL':
        query_string = '&'.join(f"{key}={value}" for key, value in options.items())
        self._url = f"{self._url}?{query_string}"
        return self
    
    def get_json(self,
                 session: Session = None,
                 known_errors: dict[int, tuple[Exception, str]] = {}) -> dict:
        
        s = session or Session()
        # Get response from url
        response = s.get(self._url)
        if response.status_code == 200:
            pass
        elif response.status_code in known_errors:
            error, msg = known_errors[response.status_code]
            raise error(msg)
        else:
            raise WrapperException(f"Unknown reason for error on url {self._url!r}.")
        
        return response.json()
    
    def to_string(self) -> str:
        return self._url
    
    def copy(self) -> 'URL':
        cls = self.__class__
        return cls(self._url)
        
    def __str__(self) -> str:
        return self._url
    
    def __len__(self) -> int:
        return len(self._url)
    
    def __repr__(self):
        return f"URL({self._url})"
    