import os
import webbrowser
import psutil
import subprocess
from langchain_core.tools import StructuredTool

import inspect
from typing import Type, Any, Dict, Tuple, Callable
from pydantic import BaseModel, Field, create_model
from docstring_parser import parse, DocstringStyle


def get_cpu():
    """Return current CPU usage percentage"""
    return psutil.cpu_percent(interval=1)


def get_ram_usage():
    """Return current RAM usage in MB"""
    return psutil.virtual_memory().used / (1024 * 1024)


def open_chrome():
    """Open Google Chrome browser"""
    webbrowser.open()


def open_calculator():
    """Open Windows Calculator application"""
    os.system("calc")


def open_notepad():
    """Open Windows Notepad application"""
    os.system("notepad")


def execute_shell_cmd(cmd: str):
    """
    Execute a PowerShell command and return output or error message

    Args:
        cmd: PowerShell command string to execute

    Returns:
        str: Command output if successful, error message if failed
    """
    try:
        result = subprocess.run(
            ["powershell", "-Command", cmd], capture_output=True, text=True, check=True
        )
        return result.stdout or "Command executed successfully"
    except subprocess.CalledProcessError as e:
        return e.stderr


def create_tool(func):
    """Create schema for a placeholder tool."""
    return StructuredTool.from_function(
        func,
        name=func.__name__,
        description=func.__doc__,
        args_schema=create_pydantic_model_from_function(func),
    )


def create_pydantic_model_from_function(
    func: Callable,
    model_name: str = None,
    docstring_style: DocstringStyle = DocstringStyle.GOOGLE,
) -> Type[BaseModel]:
    """
    Dynamically creates a Pydantic model from a function's signature and docstring.

    Args:
        func: The function to inspect.
        model_name: Optional name for the generated Pydantic model. If None,
                    it defaults to "{func_name.capitalize()}Input".
        docstring_style: The style of the docstring to parse (e.g., GOOGLE, NUMPYDOC, REST).

    Returns:
        A Pydantic BaseModel class representing the function's input arguments.

    Raises:
        TypeError: If an argument is missing a type annotation. Consider adding
                   a default Any or skipping if needed for more flexibility.
    """
    sig = inspect.signature(func)
    docstring = parse(inspect.getdoc(func) or "", style=docstring_style)
    doc_params = {param.arg_name: param.description for param in docstring.params}

    fields: Dict[str, Tuple[Type, Any]] = {}
    for name, param in sig.parameters.items():

        if param.kind in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ):
            continue

        param_type = param.annotation
        if param_type is inspect.Parameter.empty:
            print(
                f"Warning: Argument '{name}' in function '{func.__name__}' is missing a type annotation. Defaulting to 'Any'."
            )
            param_type = Any
        description = doc_params.get(name)
        if param.default is inspect.Parameter.empty:
            field_definition = Field(..., description=description)
        else:
            field_definition = Field(default=param.default, description=description)
        fields[name] = (param_type, field_definition)

    if model_name is None:
        model_name = f"{func.__name__.capitalize()}Input"
    DynamicModel = create_model(model_name, **fields)
    DynamicModel.__doc__ = f"Input model for the function '{func.__name__}'.\n\n{inspect.getdoc(func) or ''}"

    return DynamicModel


tools = [
    get_cpu,
    get_ram_usage,
    open_chrome,
    open_calculator,
    open_notepad,
    execute_shell_cmd,
]


tool_registry = {func.__name__: create_tool(func) for func in tools}
