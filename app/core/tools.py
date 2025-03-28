import os
import webbrowser
import psutil
import subprocess
from langchain_core.tools import StructuredTool


def get_cpu():
    """Return current CPU usage percentage"""
    return psutil.cpu_percent(interval=1)


def get_ram_usage():
    """Return current RAM usage in MB"""
    return psutil.virtual_memory().used / (1024 * 1024)


def open_chrome():
    """Open Google Chrome browser to google.com"""
    webbrowser.open()


def open_calculator():
    """Open Windows Calculator application"""
    os.system("calc")


def open_notepad():
    """Open Windows Notepad application"""
    os.system("notepad")


def execute_shell_cmd(cmd):
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
        func, name=func.__name__, description=func.__doc__
    )


tools = [
    get_cpu,
    get_ram_usage,
    open_chrome,
    open_calculator,
    open_notepad,
    execute_shell_cmd,
]


tool_registry = {func.__name__: create_tool(func) for func in tools}
