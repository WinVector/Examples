

Code to enforce function signature and data frame schemas in Python for Pandas.

This module supplies a Python function decorator demonstrated [here](https://github.com/WinVector/Examples/blob/main/arg_types/schema_check.ipynb).

In particular the `SchemaRaises` decorator (usually imported with `from data_schema import SchemaRaises as SchemaCheck` or as `import schema_check` to allow easy management) annotates functions. It adds a type checking prologue and epilogue, alters the documentation, and attaches itself to the wrapped function as a new `data_schema` attribute. It supplies input and output partial schema specifications for the function and data frame arguments as attributes `arg_specs` and `return_spec` respectively.

The argument specs are as follows:

  * Dictionaries are used both for maps from argument names to allowed type sets and data frame column names to expected non-null type sets.
  * Type sets can be written as sets of types or, as a single type.
  * Items that are not None, types, sets, or dictionaries are converted to types.

The test criterion is: a function or data frame must have *at least* the specified columns, and *no more* than the set of specified types used for non-null values in these columns.

What this all means, and how to use it, is easiest shown in [the demo](https://github.com/WinVector/Examples/blob/main/arg_types/schema_check.ipynb).

Unit tests:

```
python -m pytest tests
```