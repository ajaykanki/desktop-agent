import subprocess
from pathlib import Path
import warnings

warnings.filterwarnings(
    "ignore", message="Apply externally defined coinit_flags", category=UserWarning
)
from pywinauto.application import Application


# TODO: Use Win32 API directly instead of subprocess
# Time: ~0.6-0.9 seconds
def is_process_running(name: str):
    result = subprocess.run(
        ["tasklist", "/fi", "imagename eq " + name], capture_output=True, text=True
    )
    return name in result.stdout.lower()


def launch_process(executable_path: str, window_title: str):
    exec_path = Path(executable_path)
    if not exec_path.exists():
        raise FileNotFoundError(f"Executable not found at {executable_path}")

    # Extract the executable name from the path
    if is_process_running(exec_path.name):
        return False

    app = Application().start(str(exec_path), timeout=60)
    dlg = app.window(title=window_title)
    dlg.wait("ready", timeout=60)
    return True
