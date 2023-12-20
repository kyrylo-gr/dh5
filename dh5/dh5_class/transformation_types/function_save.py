# flake8: noqa: D100
import inspect
import logging
from typing import Any


class Function:
    """Function class contains code of a function that can be evaluated.

    Examples:
    --------
    >>> func = Function("def func(a, b): return a + b")
    >>> func.code # -> "def current_func(a, b): return a + b"
    >>> func.eval(1, 2) # -> 3

    Function is evaluated on first eval call and not before.

    Moreover, __call__ method can be used if the function was already evaluated:

    >>> func = Function("def func(a, b): return a + b")
    >>> func.code # -> "def current_func(a, b): return a + b"
    >>> func(1, 2) # -> TypeError("Function was never evaluated.")
    >>> func.eval(1, 2) # -> 3
    >>> func(1, 2) # -> 3

    """

    code: str = ""
    func = None
    original_name: str = ""

    _read_only = True

    def __init__(self, code: str):
        """Create a `Function` from the code provided.

        Args:
            code (str): Code of the function.
        """
        index_name = code.find("(")
        if index_name == -1:
            return
        self.original_name = code[4:index_name]
        self.code = "def current_func" + code[index_name:]
        if not self.code.endswith("\n"):
            self.code += "\n"

    def _evaluate_func(self):
        """Evaluate the function code and store it in the self.func."""
        if self.code == "":
            raise ValueError(
                f"Function {self.original_name} cannot be loaded because the code is empty."
            )

        try:
            cc = compile(self.code, "<string>", "single")  # noqa: DUO110
            eval(cc)  # pylint: disable=W0123 # noqa: DUO104
        except SyntaxError:
            logging.warning(
                "Function %s cannot be loaded because unexpected SyntaxError.", self.original_name
            )
            return

        self.func = locals().get("current_func")

    def eval(self, *args, **kwds):
        """Evaluate the function and return the result."""
        if self.func is None:
            self._evaluate_func()
        if self.func is None:
            raise SyntaxError(f"Cannot call run a function defined by:\n{self.code}")
        return self.func(*args, **kwds)  # type: ignore

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        """Evaluate the function and return the result if the function was already compiled."""
        if self.func is None:
            raise ImportError(
                "Function was never evaluated. On the first run use the eval(...) method instead."
            )
        return self.func(*args, **kwds)  # type: ignore

    def __str__(self):
        return f"Function: {self.code}"  # pragma: no cover


def function_to_str(func):
    """Return the code source of the function using inspect library."""
    if inspect.isfunction(func):
        return inspect.getsource(func)

    name = func.__name__ if hasattr(func, "__name__") else ""
    raise ValueError(f"Function {name} must be a function and not a module or a class.")
