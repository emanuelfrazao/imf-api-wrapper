
class URLBuilder:
    
    def __init__(self, base):
        self._url = base
        
    def add_path(self, subpath):
        self._url = f"{self._url}/{subpath}"
        return self
        
    def add_positional_arguments(self, parameters_args: list[str | list[str]], args_sep='+', params_sep='.'):
        
        arguments_string = params_sep.join(args_sep.join(param) if isinstance(param, list) else param
                                       for param in parameters_args)
        self._url = f"{self._url}/{arguments_string}"
        return self
    
    def add_query(self, **options: str):
        query_string = '&'.join(f"{key}={value}" for key, value in options.items())
        self._url = f"{self._url}?{query_string}"
        return self
    
    def to_string(self):
        return self._url
    
    def __str__(self):
        return self._url
    
    def __repr__(self):
        return f"URLBuilder({self._url})"
    
def build_url(base, subpaths, positional_params = [], options = {}):
    
    builder = URLBuilder(base)
    
    for path in subpaths:
        builder.add_path(path)
    
    if positional_params:
        builder.add_positional_arguments(positional_params)
    
    if options:
        builder.add_query(**options)
    
    return builder.to_string()
    