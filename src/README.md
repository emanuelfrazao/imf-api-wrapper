---
title: IMF API wrapper specification
description: project specification - context and technical details
---
# intro

## context

so, the IMF (as in, the International Monetary Fund) has a bunch of public data - and I'm wanting to scrape it.

their website offers a (very poorly documented) API to extract (what seems to be -) most of their public data available.

the API, on top of not being well documented, is somewhat opaque and weirdly structured - but still, follows a discernable logic.

there are 2 public unofficial wrappers (for `python` and `R`) developed for it, and they are good for referencing, but - 'are either not exhaustive (in the case of the `python` one), or follow the exact same logic of the API (the `R`'s), which (again!) is not great (!)

## goal

the goal of this project is to wrap another API around IMF's - initially it'll be just a `python` API (as in, a simple package - which would be nice to put into `PyPI`). eventually, we may actually keep scraping the IMF's API structure iot build a full-fledged RESTful experience - with (who knows? -) some free DNS (would be a nice candidate POC for `deno deploy`).

## extra info

the IMF has a list of datasets available; this list is accessible through an API endpoint.

every dataset has time series data - multiple ones - each being -:

* on some (from the API user's perspective - opaque) metric,
* with some unit,

datasets have names and descriptions, and may either consider a multi-year time period, or, specifically, a single year/quarter - in which case the interface differs.

for each dataset, one can gather data on it (either all of the corresponding data, or only unspecific filtered parts - which is a problem from the user's perspective).

most datasets - as is common for this domain - will have *indicators*, along with a common set of meta information.

# references

* **API resources**:

  * [API "docs"](http://dataservices.imf.org/REST/SDMX_JSON.svc/helphttps:/)
  * [API's own "help page"](https://datahelp.imf.org/knowledgebase/articles/838041-sdmx-2-0-restful-web-service)
  * [(3-part series of) blog posts (for python) describing some functionality of the API](http://www.bd-econ.com/imfapi1.html)
* **other wrappers**:

  * [R's](https://github.com/mingjerli/IMFData/)
  * [python's](https://pypi.org/project/imfpy/)

# IMF's API investigation

(- building on top of resources and other wrappers, and some exploration)

## routes

every publicly [documented](http://dataservices.imf.org/REST/SDMX_JSON.svc/helphttps:/) API route corresponds to a `GET` method and returns `json` data.

### common response schema

the responses from all of the main `GET` routes meet the same basic schema , namely - and informally -:

```json
{
    < single root key - randomly corresponding to call >: {
        "@xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
        "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "@xmlns": "http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message",
        "@xsi:schemaLocation": "http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure https://registry.sdmx.org/schemas/v2_0/SDMXStructure.xsd http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message https://registry.sdmx.org/schemas/v2_0/SDMXMessage.xsd",
        "Header": < so-called meta information - useless >,
        < ... call related sub keys > : { ... }
    }
}
```

meanwhile, all' these schema links do not work

### `GET` routes

#### `/Dataflow`

* **description**: get the datasets available
* **url**: `http://dataservices.imf.org/REST/SDMX_JSON.svc/Dataflow`
* **known errors**:
  * `400`: if one writes `<url>/*`
* **response schema specificity**:
  * root key: `"Structure"`
  * sub-keys - a single stream with:
    * `"Dataflows"` - a mapping with expectedly a single key:
      * `"Dataflow"` - a list of items, each with 7 keys, but only 2 relevant (`"Name`, `"KeyFamilyRef"`):

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

#### `/CompactData`

* **description**: get data (either filtered or not) on a given dataset
* **notes**:
  * each dataset has its own *dimensions* (on the API's lingo), which stand for positional parameters
  * arguments to these parameters are sometimes required and sometimes not (e.g., not required for `PCPS` and required for `BOP`), and on an unreliable fashion - there seems to be no indication on which side a dataset falls.
* **url**: `http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/{dataset}[/{...positional}][/?{...options}]`
* **examples**:
  * for Primary Commodity Price System [PCPS]:
    * `http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/PCPS`, for getting the whole dataset
    * `http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/PCPS/A`, for specifieng
* **arguments**:
  * positional (and optional):
  * query:
* **known errors**:
  * `400`:
    * if one writes `<main_url>/` (with the ending backslash)
    * if one writes `<main_url>/<suffix>[/...]` such that `<suffix>` does not correspond to a dataset
* **response schema specificity**:
  * root key: `"CompactData"`
  * sub keys:
    * `"Dataset"` - a mapping with one relevant key:
      * `"Series"` - a list of items, each a mapping with keys:
        * `"@FREQ"`:
        * `""`:
        * `""`:
        * `""`:
        * `""`:
        * `""`:

#### `DataStructure`

* **description**: get the structure of the data for a given dataset - i.e.
* **url**: `http://dataservices.imf.org/REST/SDMX_JSON.svc/DataStructure/{dataset}`
* **known errors**:
  * `400`: if one writes `<base>/` (with the ending backslash)
  * `500`: if one writes `<base>/<suffix>` such that `<suffix>` does not correspond to a `dataset`
* **response schema specificity**:
  * root key: `"Structure"`
  * sub-keys:
    * `"

```
http://dataservices.imf.org/REST/SDMX_JSON.svc/DataStructure/{database ID}
```

## 1.3 CompactData Method

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
