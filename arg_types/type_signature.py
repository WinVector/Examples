

from functools import wraps
from typing import Any, Dict, List, Optional
from inspect import signature
import pprint
import numpy as np
import pandas as pd

def _prep_type_arg(v):
    """
    Transform/enforce type, set of types, or pandas data frame with types or sets of types columns.
    """
    assert v is not None
    if isinstance(v, type):
        return {v}
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
    return {type(v)}

class TypeSignature:
    """
    Class as a type checking decorator.
    """
    def __init__(self, arg_specs: Optional[Dict[str, Any]]=None, *, return_spec=None) -> None:
        """
        Check argument types and "return_spec".
        Types must be in specified set. Pandas data frames must have at least declared columns and expected types in those columns.
        Wraps function to raise TypeError on argument non-compliance.

        :param arg_specs: dictionary of named args to type specifications.
        :param return_spec: optional return type specification.
        """
        if arg_specs is None:
            arg_specs = dict()
        self.arg_specs = {k: _prep_type_arg(v) for k, v in arg_specs.items()}
        self.return_spec = None
        if return_spec is not None:
            self.return_spec = _prep_type_arg(return_spec)
    
    def _check_spec(self, *, expected_type, observed_value) -> Optional[str]:
        if expected_type is None:
            return None
        if isinstance(expected_type, set):
            if not np.any([isinstance(observed_value, ti) for ti in expected_type]):
                observed_type = type(observed_value)
                tnames = "{" + ", ".join(sorted([t.__name__ for t in expected_type])) + "}"
                return f"one of {tnames} expected, was type {observed_type.__name__}"
        elif isinstance(expected_type, pd.DataFrame):
            if not isinstance(observed_value, pd.DataFrame):
                observed_type = type(observed_value)
                return f"should be type pandas.DataFrame, was type {observed_type.__name__}"
            msgs = []
            for col_name in expected_type.columns:
                if col_name not in observed_value.columns:
                    msgs.append(f"missing required column '{col_name}'")
                else:
                    if (expected_type.shape[0] > 0) and (observed_value.shape[0] > 0):
                        expected_type_set = expected_type[col_name].values[0]
                        if expected_type_set is not None:
                            for vi in observed_value[col_name]:
                                if (pd.isnull(vi) == False) and (not np.any([isinstance(vi, ti) for ti in expected_type_set])):
                                    tnames = "{" + ", ".join(sorted([t.__name__ for t in expected_type_set])) + "}"
                                    msgs.append(f" column '{col_name}' has a type {type(vi).__name__} entry, when one of {tnames} expected")
            if len(msgs) > 0:
                return ", ".join(msgs)
        return None

    def check_args(self, *, arg_names: List[str], fname: str, args, kwargs) -> None:
        assert isinstance(fname, str)
        # check positional args (by name)
        seen = set()
        msgs = []
        for i in range(len(args)):
            k = arg_names[i]
            observed_value = args[i]
            seen.add(k)
            if k in self.arg_specs.keys():
                expected_type = self.arg_specs[k]
                msg = self._check_spec(expected_type=expected_type, observed_value=observed_value)
                if msg is not None:
                    msgs.append(f"{fname}() arg {k} {msg}")
        # check types of named arguments
        for k, expected_type in self.arg_specs.items():
            if k not in seen:
                if k not in kwargs.keys():
                    msgs.append(f"{fname}() expected arg {k}")
                else:
                    observed_value = kwargs[k]
                    msg = self._check_spec(expected_type=expected_type, observed_value=observed_value)
                    if msg is not None:
                        msgs.append(f"{fname}() arg {k} {msg}")
        if len(msgs) > 0:
            raise TypeError("\n".join(msgs))

    def check_return(self, *, fname: str, return_value) -> None:
        assert isinstance(fname, str)
        msg = self._check_spec(expected_type=self.return_spec, observed_value=return_value)
        if msg is not None:
            raise TypeError(f"{fname}() return value: {msg}")

    def __call__(self, type_check_fn):
        """
        Wrap a function with TypeError instrumentation. For use as a decoration.
        """
        type_check_self = self
        type_check_fn_name = type_check_fn.__name__
        type_check_arg_names = [k for k, v in signature(type_check_fn).parameters.items()]
        @wraps(type_check_fn)
        def wrapped_fn(*args, **kwargs):
            type_check_self.check_args(fname=type_check_fn_name, arg_names=type_check_arg_names, args=args, kwargs=kwargs)
            type_check_return_value = type_check_fn(*args, **kwargs)
            type_check_self.check_return(fname=type_check_fn_name, return_value=type_check_return_value)
            return type_check_return_value
        type_doc = (
            "\n arg specifications\n" + pprint.pformat(self.arg_specs)
            + "\n return specification:\n" + pprint.pformat(self.return_spec)
            + "\n")
        if type_check_fn.__doc__ is None:
            wrapped_fn.__doc__ = type_doc
        else:
            wrapped_fn.__doc__ = type_doc + "\n\n" + type_check_fn.__doc__
        return wrapped_fn
