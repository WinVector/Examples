
import numpy as np
import pandas as pd
from type_signature import non_null_types_in_frame
from type_signature import TypeCheckSwitch
# from type_signature import TypeSignatureNOOP as TypeSignature
from type_signature import TypeSignatureRaises as TypeSignature


def test_tchecks_on():
    TypeCheckSwitch().on()

    @TypeSignature({
            'a': int, 
            'b': int, 
            'c': {'x': int},
            },
            return_spec={'z': float})
    def fn(a, /, b, *, c, d=None):
        """doc"""
        return d

    help(fn)

    threw = False
    try:
        fn()
    except TypeError as e:
        print(e)
        threw = True
    assert threw

    try:
        fn(1, 2)
    except TypeError as e:
        print(e)
        threw = True
    assert threw

    threw = False
    try:
        fn(1, 2, c=3)
    except TypeError as e:
        print(e)
        threw = True
    assert threw

    threw = False
    try:
        fn(1, 2, c=pd.DataFrame({'z': [7]}))
    except TypeError as e:
        print(e)
        threw = True
    assert threw

    fn(1, 2, c=pd.DataFrame({'x': [3]}), d=pd.DataFrame({'z': [7.0]}))

    fn(1, b=2, c=pd.DataFrame({'x': [3]}), d=pd.DataFrame({'z': [7.0]}))

    threw = False
    try:
        fn(1, 2, c=pd.DataFrame({'x': [3.0]}))
    except TypeError as e:
        print(e)
        threw = True
    assert threw

    rv = None
    threw = False
    try:
        fn(1, 2, c=pd.DataFrame({'x': [30], "z": [17.2]}), d=pd.DataFrame({'q': [7.0]}))
    except TypeError as e:
        print(e.args[0])
        rv = e.args[1]
        threw = True
    assert threw

    rv

    @TypeSignature(
            {'a': pd.DataFrame},
            return_spec=int,
    )
    def g(a):
        return a.shape[0]

    threw = False
    try:
        g(a=7)
    except TypeError as e:
        print(e)
        threw = True
    assert threw

    threw = False
    try:
        g(7)
    except TypeError as e:
        print(e)
        threw = True
    assert threw
    g(a=pd.DataFrame({'x': [5]}))
    threw = False
    try:
        g({'x': [5]})
    except TypeError as e:
        print(e)
        threw = True
    assert threw
    d =  pd.DataFrame({
            'b': [1, 3, 4],
            'q': np.nan,
            'r': [1, None, 3],
            's': [np.nan, 2.0, 3.0],
            'x': [1, 7.0, 2],
            'y': ["a", None, np.nan],
            'z': [1, 1.0, False],
        })
    d.dtypes
    non_null_types_in_frame(d)


def test_tchecks_off():
    TypeCheckSwitch().off()

    """ begin text
    We add a decorator that shows the types of at least a subset of positional and named arguments. Declarations are either Python types, or sets of types. A special case is Pandas data frames, where we specify a required subset of columns and their value type-sets. "return_spec" is reserved to name the return type of the function (so the function we are working with may not have an argument of that name).
    """  # end text

    @TypeSignature({
            'a': int, 
            'b': int, 
            'c': {'x': int},
            },
            return_spec={'z': float})
    def fn(a, /, b, *, c, d=None):
        """doc"""
        return d

    threw = False
    try:
        fn(1, 2, c=pd.DataFrame({'z': [7]}))
    except TypeError as e:
        print(e)
        threw = True
    assert not threw
