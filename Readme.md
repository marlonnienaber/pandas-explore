# pandas_explore

**pandas_explore** is a Python package designed for the exploration of columns in pandas DataFrames. It provides utilities to analyze the raw data of numerical, categorical, boolean, string and ID attributes. Furthermore single and multi-column keys can be analyzed.


## Installation

To install the package, clone the repository and install the required dependencies:

```bash
git clone https://github.com/marlonnienaber/pandas_explore
cd pandas-explore
pip install .
```

Or via pip:

```bash
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple pandas-explore
```
**important**: The --extra-index-url option ensures that dependecies are fetched from regular pipy (installation might fail without!)


## Features

**Exploration Functions**:
- explore_numerical_id
- explore_string_id
- explore_categorical_attribute
- explore_boolean_attribute
- explore_numerical_attribute
- explore_string_attribute
- explore_cleaned_key

**example**:
```bash
import pandas as pd
from pandas_explore import explore_boolean_attribute

df = ... (some pandas data frame)
explore_boolean_attribute(df['some_column_name'])
```


