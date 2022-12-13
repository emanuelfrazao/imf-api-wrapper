
class URLBuilder:
    
    BASE = "http://dataservices.imf.org/REST/SDMX_JSON.svc"
    
    @classmethod
    def dataflow(cls):
        """For returning the list of the datasets, registered for the Data Service."""
        return cls.BASE + "/Dataflow"
    

def main():
    import requests
    dataflow_url = URLBuilder.dataflow()

    print(dataflow_url)

if __name__ == '__main__':
    main()