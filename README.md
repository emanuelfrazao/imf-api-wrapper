---
title: IMF
description: explore imf data and API on commodities and others
---

# API documentation
The API has little to no documentation, but there are 2 links worth checking:
* [imf's own "help page"](https://datahelp.imf.org/knowledgebase/articles/838041-sdmx-2-0-restful-web-service)
* [a 3-part sequence of blog posts for python describing some functionality of the API](http://www.bd-econ.com/imfapi1.html)

## 1.1 Dataflow Method

Dataflow method returns the list of the datasets, registered for the Data Service.
In order to obtain the data use the following request:

```
http://dataservices.imf.org/REST/SDMX_JSON.svc/Dataflow
```

## 1.2 DataStructure Method

DataStructure method returns the structure of the dataset.
In order to obtain the data use the following request:

```
http://dataservices.imf.org/REST/SDMX_JSON.svc/DataStructure/{database ID}
```

## 1.3 CompactData Method

CompactData method returns the compact data message.
In order to obtain the data use the following request:

<pre><a href="http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/" title="Link: http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/">http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/</a><span>{database ID}/{frequency}.{item1 from
dimension1}+{item2 from dimension1}+{item N from dimension1}.{item1 from
dimension2}+{item2 from dimension2}+{item M from dimension2}?startPeriod={start
date}&endPeriod={end date}</span><br/></pre>

## 1.4 MetadataStructure Method

MetadataStructure method returns the metadata structure of the dataset.
In order to obtain the data use the following request:

```
http://dataservices.imf.org/REST/SDMX_JSON.svc/MetadataStructure/{database ID}
```

## 1.5 GenericMetadata Method

GenericMetadata method returns the generic metadata message.
In order to obtain the data use the following request:

<pre><a href="http://dataservices.imf.org/REST/SDMX_JSON.svc/GenericMetadata/" title="Link: http://dataservices.imf.org/REST/SDMX_JSON.svc/GenericMetadata/">http://dataservices.imf.org/REST/SDMX_JSON.svc/GenericMetadata/</a><span>{database ID}/{item1 from
dimension1}+{item2 from dimension1}+{item N from dimension1}.{item1 from
dimension2}+{item2 from dimension2}+{item M from dimension2}?startPeriod={start
date}&endPeriod={end date}</span></pre>

1.6 CodeList Method

GetCodeList method returns the description of CodeLists
In order to obtain the data use the following request:

<pre><p><a href="http://dataservices.imf.org/REST/SDMX_JSON.svc/CodeList/" title="Link: http://dataservices.imf.org/REST/SDMX_JSON.svc/CodeList/">http://dataservices.imf.org/REST/SDMX_JSON.svc/CodeList/</a>{codelist code}_{database ID}</p></pre>

## 1.7 MaxSeriesInResult Method

GetMaxSeriesInResult method returns the maximum number of time series that can be returned by CompactData.
In order to obtain the data use the following request:

```
http://dataservices.imf.org/REST/SDMX_JSON.svc/GetMaxSeriesInResult
```
