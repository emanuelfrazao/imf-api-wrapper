---
title: IMF API wrapper
description: a `python` wrapper API for IMF's API that is consistent, transparent, and easy to use.
---
# intro

the *International Monetary Fund* [IMF] has some publicly available data on its website and behind a public API, but the latter is poorly documented, hard to use, and inconsistent.

this project aims to build a wrapper for `python` around that API that is able to extract all data and information on each dataset from a single entry-point.


# context

the IMF has several datasets, each with:

* information related to its description, methodology, time coverage, metrics being used, and others;
* specific (and described) parameters and attributes;
* a collection of time-series data, each associated with a set of parameter values.


# ui

the wrapper is accessed through a single class `IMFWrapper`.

by initializing the object as

```python
imf = IMFWrapper()
```

one is able to do 2 things:

* accessing the datasets, with

```python
for dataset, description in imf.datasets.items():
    print(f"{dataset}: {description}")
```

* grabbing a `Dataset` instance, e.g.:

```python
pcps = imf.get_dataset('PCPS')
dots = imf.get_dataset('DOTS')
bop = imf.get_dataset('BOP')
```

then, with a `Dataset` instance, one is able to:

* see information on metadata (e.g., definition, description, time coverage, methodology, etc) and on common parameters and attributes for the dataset's data series
* grab data series given arguments to the parameters
