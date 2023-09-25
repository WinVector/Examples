
import tempfile
from pprint import pformat
from rpy2 import robjects
from rpy2.robjects.packages import importr
from IPython.display import Image
from rpy2.robjects import pandas2ri
import numpy as np
import pandas as pd


ggplot2 = importr("ggplot2")


def last_ggplot() -> Image:
    """
    Return last ggplot2 run in R as an IPython.display.Image.
    """
    with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as tf:
        ggplot2.ggsave(
            filename=tf.name, 
            units="in", 
            width=8, 
            height=5
        )
        result = Image(filename=tf.name)
    return result


def convert_arg_to_R(arg):
    """
    Convert arg to something that can be transported to R.

    :param arg: argument to convert
    :return: converted argument
    """
    if isinstance(arg, pd.DataFrame):
        with (robjects.default_converter + pandas2ri.converter).context():
            arg = robjects.conversion.get_conversion().py2rpy(arg)
        return arg
    if isinstance(arg, float):
        arg = float(arg)  # get rid of np types
        return arg
    if isinstance(arg, int):
        arg = int(arg)   # get rid of np types
        return arg   
    return arg


def get_ggplot_fn_by_name(fn_name: str):
    """
    Retrieve a function by name from the R namespace, and then wrap it to 
    return the last_ggplot() after the function is called.

    :param fn_name: name of R function to lookup.
    :return: function that calls R function and then returns last ggplot2
    """
    assert isinstance(fn_name, str)
    fn = robjects.r[fn_name]
    fn_formals = str(robjects.r(f"as.list(formals({fn_name}))")).strip()
    fn_env = str(robjects.r(f'environment({fn_name})')).strip()
    fn_srcfile = str(robjects.r(f'attr(attr({fn_name}, "srcref"), "srcfile")')).strip()
    # fn_attr = str(robjects.r(f'attributes({fn_name})')).strip()
    def w_fn(*args, **kwargs):
        r_args = [convert_arg_to_R(arg) for arg in args]
        r_kwargs = {k: convert_arg_to_R(v) for k, v in kwargs.items()}
        plt_obj = fn(*r_args, **r_kwargs)  # conversion of return value causes evaluation of plot
        return last_ggplot()
    w_fn.__name__ = fn_name
    w_fn.__doc__ = f"""
imported R function {fn_name}() (assumed to return a ggplot)
 wrapped fn returns IPython.display.Image
R source file: {fn_srcfile}
R definition environment: {fn_env}
R arguments:
{fn_formals}
"""
    return w_fn
