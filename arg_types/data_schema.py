"""
Tools for checking incoming and outgoing names and types of functions of data frames
"""

from functools import wraps
from typing import Any, Dict, List, Optional, Set, Type, Union
from inspect import signature
import pprint
import numpy as np
import pandas as pd


def _prep_schema_specification(v) -> Optional[Union[Type, Set, Dict]]:
    """
    Transform/enforce type, set of types, or dict of name to type maps to standard form.
    None represents no constraint.
    Types and sets of Types represent type constraints.
    Dicts represent column structure of a data frame.
    """
    if v is None:
        return None
    elif isinstance(v, type):
        return v
    elif isinstance(v, set):
        new_set = {_prep_schema_specification(vi) for vi in v}
        new_set = {vi for vi in v if v is not None}
        for vi in new_set:
            assert not isinstance(vi, set)
        return new_set
    elif isinstance(v, dict):
        new_set = {ki: _prep_schema_specification(vi) for ki, vi in v.items()}
        for vi in new_set:
            assert not isinstance(vi, dict)
        return new_set
    else:
        return type(v)


def _type_name(t) -> str:
    if not isinstance(t, type):
        t = type(t)
    return t.__name__


def non_null_types_in_frame(d: pd.DataFrame) -> Dict[str, Optional[Set[Type]]]:
    """
    Return dictionary of non-null types seen in dataframe columns.
    """
    assert isinstance(d, pd.DataFrame)
    result = dict()
    for col_name in d.columns:
        types_seen = {type(vi) for vi in d[col_name].values if not pd.isnull(vi)}
        if len(types_seen) < 1:
            result[col_name] = None
        else:
            result[col_name] = types_seen
    return result


class SchemaCheckSwitch(object):
    """
    From: https://python-patterns.guide/gang-of-four/singleton/
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SchemaCheckSwitch, cls).__new__(cls)
            cls._instance.is_on_setting = True
        return cls._instance

    def on(self) -> None:
        self.is_on_setting = True

    def off(self) -> None:
        self.is_on_setting = False

    def is_on(self) -> bool:
        return self.is_on_setting


# early build of singleton
SchemaCheckSwitch()


class SchemaBase(object):
    """
    Input and output schema decorator.
    """

    def __init__(
        self, arg_specs: Optional[Dict[str, Any]] = None, *, return_spec=None
    ) -> None:
        """
        Pandas data frames must have at least declared columns and no unexpected types in columns.
        Nulls/Nones/NaNs values are not considered to have type (treating them as missingness).
        None as type constraints are considered no-type (unfailable).

        :param arg_specs: dictionary of named args to type specifications.
        :param return_spec: optional return type specification.
        """
        self.arg_specs = _prep_schema_specification(arg_specs)
        self.return_spec = _prep_schema_specification(return_spec)


class SchemaRaises(SchemaBase):
    """
    Input and output schema decorator.
    Raises TypeError on schema violations.
    """

    def _check_spec(
        self, *, expected_type: Optional[Union[Type, Set, Dict]], observed_value
    ) -> Optional[str]:
        if expected_type is None:
            # no expectation, no failure possible
            return None
        elif isinstance(expected_type, type):
            # single type
            if not isinstance(observed_value, expected_type):
                observed_type = type(observed_value)
                return f"expected type {_type_name(expected_type)}, found type {_type_name(observed_type)}"
        elif isinstance(expected_type, set):
            # type set, expect value to be one of the types
            if not np.any([isinstance(observed_value, ti) for ti in expected_type]):
                observed_type = type(observed_value)
                type_names = (
                    "{"
                    + ", ".join(sorted([_type_name(t) for t in expected_type]))
                    + "}"
                )
                return f"expected type one of {type_names}, found type {_type_name(observed_type)}"
        elif isinstance(expected_type, dict):
            if not isinstance(observed_value, pd.DataFrame):
                observed_type = type(observed_value)
                return f"expected type pandas.DataFrame, found type {_type_name(observed_type)}"
            msgs = []
            for col_name, spec_i in expected_type.items():
                if col_name not in observed_value.columns:
                    msgs.append(f"missing required column '{col_name}'")
                else:
                    if (spec_i is not None) and (observed_value.shape[0] > 0):
                        for vi in observed_value[col_name]:
                            if not pd.isnull(vi):
                                msg_i = self._check_spec(
                                    expected_type=spec_i, observed_value=vi
                                )
                                if msg_i is not None:
                                    msgs.append(f" column '{col_name}' {msg_i}")
                                    break
            if len(msgs) > 0:
                return ", ".join(msgs)
        else:
            # should not be reached
            raise ValueError(f"expected type of type {type(expected_type)} unexpected")
        return None

    def check_args(self, *, arg_names: List[str], fname: str, args, kwargs) -> None:
        if not SchemaCheckSwitch().is_on():
            return
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
                msg = self._check_spec(
                    expected_type=expected_type, observed_value=observed_value
                )
                if msg is not None:
                    msgs.append(f"arg {k} {msg}")
        # check types of named arguments
        for k, expected_type in self.arg_specs.items():
            if k not in seen:
                if k not in kwargs.keys():
                    msgs.append(f"expected arg {k} missing")
                else:
                    observed_value = kwargs[k]
                    msg = self._check_spec(
                        expected_type=expected_type, observed_value=observed_value
                    )
                    if msg is not None:
                        msgs.append(f"arg {k} {msg}")
        if len(msgs) > 0:
            raise TypeError("\nfunction " + fname + "(), issues:\n" + "  \n".join(msgs))

    def check_return(self, *, fname: str, return_value) -> None:
        if not SchemaCheckSwitch().is_on():
            return
        assert isinstance(fname, str)
        msg = self._check_spec(
            expected_type=self.return_spec, observed_value=return_value
        )
        if msg is not None:
            raise TypeError(f"{fname}() return value: {msg}", return_value)

    def __call__(self, type_check_fn):
        """
        Wrap a function with TypeError instrumentation. For use as a decoration.
        """
        type_check_self = self
        type_check_fn_name = type_check_fn.__name__
        type_check_arg_names = [
            k for k, v in signature(type_check_fn).parameters.items()
        ]

        @wraps(type_check_fn)
        def wrapped_fn(*args, **kwargs):
            type_check_self.check_args(
                fname=type_check_fn_name,
                arg_names=type_check_arg_names,
                args=args,
                kwargs=kwargs,
            )
            type_check_return_value = type_check_fn(*args, **kwargs)
            type_check_self.check_return(
                fname=type_check_fn_name, return_value=type_check_return_value
            )
            return type_check_return_value

        type_doc = (
            "\n arg specifications\n"
            + pprint.pformat(self.arg_specs)
            + "\n return specification:\n"
            + pprint.pformat(self.return_spec)
            + "\n"
        )
        if type_check_fn.__doc__ is None:
            wrapped_fn.__doc__ = type_doc
        else:
            wrapped_fn.__doc__ = type_doc + "\n\n" + type_check_fn.__doc__
        wrapped_fn.data_schema = self
        return wrapped_fn


class SchemaMock(SchemaBase):
    """Build schema, but do not enforce or attach to fn"""

    def __call__(self, type_check_fn):
        """Does nothing."""
        return type_check_fn
