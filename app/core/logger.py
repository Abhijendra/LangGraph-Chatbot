import logging
import sys
from contextvars import ContextVar
from typing import Any
from app.core.config import settings

# ContextVar allows you to pass context safely down concurrent async requests/tasks
# We use this to track LangGraph thread IDs dynamically across the request lifespan
log_context: ContextVar[dict[str, Any]] = ContextVar("log_context", default={})


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that merges systemic global configurations, 
    dynamic async runtime context (like thread_ids), and the message.
    """
    def format(self, record: logging.LogRecord) -> str:
        # Fetch current asynchronous context variables (e.g. tracking thread_id)
        ctx = log_context.get()
        
        # Build out a clean structured log object
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": "uvicorn" if record.name == "uvicorn.error" else record.name,
            "message": record.getMessage(),
            "env": settings.ENVIRONMENT.value
        }
        
        # Inject dynamic tracking data if populated
        if ctx:
            log_data.update(ctx)
            
        # Exception tracing capture
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        # If in Production/Staging, print pure minified JSON blocks for log aggregators
        if settings.ENVIRONMENT.value in ["production", "staging"]:
            import json
            return json.dumps(log_data)
            
        # Local development string formatting (Clean, human-readable console layout)
        context_str = f" | {ctx}" if ctx else ""
        return f"{log_data['timestamp']} | {log_data['level']} | {log_data['logger']}{context_str} | {log_data['message']}"


def setup_logging() -> None:
    """
    Configures the root logger and hijacks framework logger handlers (FastAPI, Uvicorn).
    Ensures unified telemetry format across the entire service.
    """
    # Determine default global logging level based on configuration settings
    log_level = logging.INFO if settings.DEBUG else logging.INFO
    
    # Initialize standard stream console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(StructuredFormatter(datefmt="%Y-%m-%d %H:%M:%S"))
    
    # Configure root logger rules
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = [console_handler]
    
    # Silence overly verbose external dependencies if needed
    for n in ("httpx", "httpx2", "httpcore", "httpcore2", "openai"):
        logging.getLogger(n).setLevel(logging.WARNING)
    
    # logging.getLogger("httpx").setLevel(logging.WARNING)
    # logging.getLogger("openai").setLevel(logging.WARNING)
    
    # Redirect Uvicorn webserver log output through our custom formatter
    for logger_name in ("uvicorn.error", "uvicorn.access", "fastapi"):
        framework_logger = logging.getLogger(logger_name)
        framework_logger.handlers = [console_handler]
        framework_logger.propagate = False
