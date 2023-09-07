

from functools import wraps
from typing import Optional
import pprint
import numpy as np
import pandas as pd

def _prep_type_arg(v):
    """
    Transform/enforce type, set of types, or pandas data frame with types or sets of types columns.
    """
    assert v is not None
    if isinstance(v, type):
        return v
    elif isinstance(v, set):
        assert len(v) > 0
        for vi in v:
            assert(isinstance(vi, type))
    elif isinstance(v, pd.DataFrame):
        v = v.reset_index(drop=True, inplace=False)
        assert v.shape[1] >= 0
        assert v.shape[0] < 2
        if v.shape[0] > 0:
            for col_name in list(v.columns):
                vj = v[col_name].values[0]
                if vj is not None:
                    if isinstance(vj, type):
                        vj = {vj}
                        v[col_name].values[0] = vj
                    assert isinstance(vj, set)
                    assert len(vj) > 0
                    for vij in vj:
                        assert(isinstance(vij, type))
        return v
    return type(v)

class TypeSignature:
    """
    Class as a type checking decorator.
    """
    def __init__(self, *args, **kwargs) -> None:
        """
        Check argument types and "return_type".
        Types must be in specified set. Pandas data frames must have at least declared columns and expected types in those columns.
        """
        self.args = [_prep_type_arg(v) for v in args]
        self.kwargs = {k: _prep_type_arg(v) for k, v in kwargs.items() if k != "return_type"}
        self.return_type = None
        try:
            self.return_type = _prep_type_arg(kwargs["return_type"])
        except KeyError:
            pass
    
    def _check_type(self, *, expected_type, observed_value) -> Optional[str]:
        if expected_type is None:
            return None
        if isinstance(expected_type, type):
            if not isinstance(observed_value, expected_type):
                observed_type = type(observed_value)
                return f" should be type {expected_type.__name__}, was type {observed_type.__name__}"
        elif isinstance(expected_type, set):
            if not np.any([isinstance(vi, ti) for ti in expected_type]):
                tnames = "{" + ", ".join(sorted([t.__name__ for t in expected_type])) + "}"
                return f" one of {tnames} expected, was type {observed_type.__name__}"
        elif isinstance(expected_type, pd.DataFrame):
            if not isinstance(observed_value, pd.DataFrame):
                observed_type = type(observed_value)
                return f" should be type pandas.DataFrame, was type {observed_type.__name__}"
            msgs = []
            for col_name in expected_type.columns:
                if col_name not in observed_value.columns:
                    msgs.append(f" missing required column '{col_name}'")
                else:
                    if (expected_type.shape[0] > 0) and (observed_value.shape[0] > 0):
                        expected_type_set = expected_type[col_name].values[0]
                        if expected_type_set is not None:
                            for vi in observed_value[col_name]:
                                if (vi is not None) and (not np.any([isinstance(vi, ti) for ti in expected_type_set])):
                                    tnames = "{" + ", ".join(sorted([t.__name__ for t in expected_type_set])) + "}"
                                    msgs.append(f" column '{col_name}' has a type {type(vi).__name__} entry, when one of {tnames} expected")
                                    break
            if len(msgs) > 0:
                return ", ".join(msgs)
        return None

    def __call__(self, f):
        @wraps(f)
        def wrapped_fn(*args, **kwargs):
            # check types of positional arguments
            for i in range(len(args)):
                expected_type = self.args[i]
                msg = self._check_type(expected_type=expected_type, observed_value=args[i])
                if msg is not None:
                    raise ValueError(f"{f.__name__} arg {i} {msg}")
            # check types of named arguments
            for k, observed_value in kwargs.items():
                expected_type = None
                try:
                    expected_type = self.kwargs[k]
                except KeyError:
                    pass
                msg = self._check_type(expected_type=expected_type, observed_value=observed_value)
                if msg is not None:
                    raise ValueError(f"{f.__name__} arg {k} {msg}")
            return_value = f(*args, **kwargs)
            msg = self._check_type(expected_type=self.return_type, observed_value=return_value)
            if msg is not None:
                raise ValueError(f"return value: {msg}")
            return return_value
        type_doc = (
            "\narg types:"
            + "\n positional args\n" + pprint.pformat(self.args) 
            + "\n named args\n" + pprint.pformat(self.kwargs) 
            + "\n return type\n" + pprint.pformat(self.return_type)
            + "\n")
        if f.__doc__ is None:
            wrapped_fn.__doc__ = type_doc
        else:
            wrapped_fn.__doc__ = type_doc + "\n\n" + f.__doc__
        return wrapped_fn
