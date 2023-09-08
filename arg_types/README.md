

Code to enforce function and data frame partial schemas.

Supplies a decorator demonstrated [here](https://github.com/WinVector/Examples/blob/main/arg_types/type_check.ipynb).

In particular the `TypeSignatureRaises` decorator (usually imported with `from type_signature import TypeSignatureRaises as TypeSignature` to allow easy management) annotates functions. It adds a type checking prologue and epilogue, alters the documentation, and attaches itself to the wrapped function as a new `type_schema` attribute. Itself it contains input and output partial schema specifications for the function and data frame arguments as attributes `arg_specs` and `return_spec` respectively.

The argument specs are as follows:

  * Dictionaries are used both for maps from argument names to allowed type sets and data frame column names to expected non-null type sets.
  * Type sets can be written as sets of types or, as a single type.
  * Items that are not None, types, sets, or dictionaries are converted to types.

The test criterion is: a function or data frame must have at least the specified columns, and all non-null values must be only the declared expected types.

Unit tests:

python -m pytest tests
