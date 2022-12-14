---
title: IMF
description: explore imf data and API on commodities and others
---
# API documentation

## external references

The API has little to no documentation, but there are 2 links worth checking:

* [IMF's own "help page"](https://datahelp.imf.org/knowledgebase/articles/838041-sdmx-2-0-restful-web-service)
* [a 3-part sequence of blog posts for python describing some functionality of the API](http://www.bd-econ.com/imfapi1.html)

## personal notes

(- building on both documentations, and some exploration)

every public API route corresponds to a `get` method.

### `get` method routes

every `get` route returns json data to the user.

#### general response schema

the responses from all of the main `get` paths are given as `json` and meet the same basic schema , namely - and informally -:

```json
{
    < root key - randomly corresponding to call >: {
        "@xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
        "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "@xmlns": "http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message",
        "@xsi:schemaLocation": "http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure https://registry.sdmx.org/schemas/v2_0/SDMXStructure.xsd http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message https://registry.sdmx.org/schemas/v2_0/SDMXMessage.xsd",
        "Header": < meta information - useless >,
        < ... call related keys > : { ... }
    }
}
```

the schema links, meanwhile, do not work (!)

#### Dataflow

* description: get the datasets available
* url: `http://dataservices.imf.org/REST/SDMX_JSON.svc/Dataflow`
* response schema specificity:
  * root key: `"Structure"`
  * sub-keys:
    * `"Dataflows"` - with expectedly a single key:
      * `"Dataflow"` - a list of items of the form:

```json

{
    "@id": < a general dataset identifier - expectedly `DS-<dataset>` >,
    "@version": < expectedly the version of the dataset on the API >,
    "@agencyID": < the source from which the dataset is taken - expectedly "IMF" >,
    "@isFinal": < whether it is final (?) - expectedly "true" >,
    "@xmlns": < the non-functioning schema url >,
    "Name": {
        "@xml:lang": "en",
        "#text": < description of the dataset | RELEVANT >
    },
    "KeyFamilyRef": {
        "KeyFamilyID": < dataset identifier | RELEVANT >,
        "KeyFamilyAgencyID": < the identifier for the source from which the dataset is taken - expectedly "IMF" >,
    }
}
```

#### DataStructure

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
