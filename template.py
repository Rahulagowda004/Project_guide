import os
from pathlib import Path
import logging
import subprocess
import sys

#logging string
logging.basicConfig(level=logging.INFO, format='[%(asctime)s]: %(message)s:')

project_name = 'Chat_With_Rahul'

list_of_files = [
    f"{os.getcwd()}/data/__init__.py",
    f"{os.getcwd()}/notebooks/__init__.py",
    f"{os.getcwd()}/static/__init__.py",
    f"{os.getcwd()}/templates/__init__.py",
    f"{os.getcwd()}/static/style.css",
    f"{os.getcwd()}/templates/index.html",
    f"{os.getcwd()}/test/__init__.py",
    f"{os.getcwd()}/{project_name}/__init__.py",
    f"{os.getcwd()}/{project_name}/config/__init__.py",
    f"{os.getcwd()}/{project_name}/config/config.yaml",
    f"{os.getcwd()}/{project_name}/exceptions/__init__.py",
    f"{os.getcwd()}/{project_name}/model/__init__.py",
    f"{os.getcwd()}/{project_name}/logger/__init__.py",
    f"{os.getcwd()}/{project_name}/logger/custom_logger.py",
    f"{os.getcwd()}/{project_name}/prompts/__init__.py",
    f"{os.getcwd()}/{project_name}/utils/__init__.py",
]


for filepath in list_of_files:
    filepath = Path(filepath)
    filedir, filename = os.path.split(filepath)

    if filedir !="":
        os.makedirs(filedir, exist_ok=True)
        logging.info(f"Creating directory; {filedir} for the file: {filename}")

    if (not os.path.exists(filepath)) or (os.path.getsize(filepath) == 0):
        with open(filepath, "w") as f:
            pass
            logging.info(f"Creating empty file: {filepath}")
            
    else:
        logging.info(f"{filename} is already exists")


###############custom exception file creation starts here###############
path = f"{os.getcwd()}/{project_name}/exceptions/custom_exception.py"
os.makedirs(os.path.dirname(path), exist_ok=True)
content = """import sys
import traceback
from typing import Optional, cast

class DocumentPortalException(Exception):
    def __init__(self, error_message, error_details: Optional[object] = None):
        # Normalize message
        if isinstance(error_message, BaseException):
            norm_msg = str(error_message)
        else:
            norm_msg = str(error_message)

        # Resolve exc_info (supports: sys module, Exception object, or current context)
        exc_type = exc_value = exc_tb = None
        if error_details is None:
            exc_type, exc_value, exc_tb = sys.exc_info()
        else:
            if hasattr(error_details, "exc_info"):  # e.g., sys
                #exc_type, exc_value, exc_tb = error_details.exc_info()
                exc_info_obj = cast(sys, error_details)
                exc_type, exc_value, exc_tb = exc_info_obj.exc_info()
            elif isinstance(error_details, BaseException):
                exc_type, exc_value, exc_tb = type(error_details), error_details, error_details.__traceback__
            else:
                exc_type, exc_value, exc_tb = sys.exc_info()

        # Walk to the last frame to report the most relevant location
        last_tb = exc_tb
        while last_tb and last_tb.tb_next:
            last_tb = last_tb.tb_next

        self.file_name = last_tb.tb_frame.f_code.co_filename if last_tb else "<unknown>"
        self.lineno = last_tb.tb_lineno if last_tb else -1
        self.error_message = norm_msg

        # Full pretty traceback (if available)
        if exc_type and exc_tb:
            self.traceback_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
        else:
            self.traceback_str = ""

        super().__init__(self.__str__())

    def __str__(self):
        # Compact, logger-friendly message (no leading spaces)
        base = f"Error in [{self.file_name}] at line [{self.lineno}] | Message: {self.error_message}"
        if self.traceback_str:
            return f"{base}\\nTraceback:\\n{self.traceback_str}"
        return base

    def __repr__(self):
        return f"DocumentPortalException(file={self.file_name!r}, line={self.lineno}, message={self.error_message!r})"
"""
with open(path, "r+", encoding="utf-8") as file:
    if len(file.read()) == 0:
        file.write(content)
print(f"Successfully wrote {len(content)} characters to {path}")
print(f"File created at: {os.path.abspath(path)}")

###############custom logger file creation
def ensure_structlog():
    try:
        import structlog  # type: ignore
        print("structlog already installed:", structlog.__version__)
        return
    except ImportError:
        print("structlog not found — installing...")

    # Prefer using `uv add structlog` if `uv` CLI is available, otherwise fall back to pip
    try:
        subprocess.check_call(["uv", "add", "structlog"])
    except FileNotFoundError:
        # `uv` CLI not found — fall back to pip
        subprocess.check_call([sys.executable, "-m", "pip", "install", "structlog"])
    except subprocess.CalledProcessError:
        # `uv` failed — fall back to pip
        subprocess.check_call([sys.executable, "-m", "pip", "install", "structlog"])

    import importlib
    importlib.invalidate_caches()
    pkg = __import__("structlog")
    print("Installed structlog:", getattr(pkg, "__version__", "unknown"))
    
ensure_structlog()
path = f"{os.getcwd()}/{project_name}/logger/custom_logger.py"
os.makedirs(os.path.dirname(path), exist_ok=True)
content = """import os
import logging
from datetime import datetime
import structlog

class CustomLogger:
    def __init__(self, log_dir="logs"):
        self.logs_dir = os.path.join(os.getcwd(), log_dir)
        os.makedirs(self.logs_dir, exist_ok=True)
        log_file = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
        self.log_file_path = os.path.join(self.logs_dir, log_file)

    def get_logger(self, name=__file__):
        logger_name = os.path.basename(name)

        file_handler = logging.FileHandler(self.log_file_path)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(message)s"))

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(message)s"))

        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            handlers=[console_handler, file_handler]
        )

        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
                structlog.processors.add_log_level,
                structlog.processors.EventRenamer(to="event"),
                structlog.processors.JSONRenderer()
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        return structlog.get_logger(logger_name)
"""
with open(path, "r+", encoding="utf-8") as file:
    if len(file.read()) == 0:
        file.write(content)
print(f"Successfully wrote {len(content)} characters to {path}")
print(f"File created at: {os.path.abspath(path)}")

