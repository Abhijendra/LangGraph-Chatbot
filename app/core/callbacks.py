import logging
import time
from langchain_core.callbacks import AsyncCallbackHandler

logger = logging.getLogger("app.agent.trace")

def _trunc(value, n=500):
    s = str(value)
    return s if len(s) <= n else s[:n] + f"...[truncated, {len(s)} chars]"

class TraceHandler(AsyncCallbackHandler):

    def __init__(self, thread_id: str):

        self.thread_id = thread_id
        self._starts : dict = {}  # run_id -> start time

    async def on_tool_start(self, serialized, input_str, *, run_id, **kwargs):
        self._starts[run_id] = time.perf_counter()
        name = serialized.get("name") if serialized else kwargs.get("name")
        logger.info(f"[{self.thread_id}] TOOL START {name} input={_trunc(input_str)}")
        # return super().on_tool_start(serialized, input_str, run_id=run_id, parent_run_id=parent_run_id, tags=tags, metadata=metadata, inputs=inputs, **kwargs)

    async def on_tool_end(self, output, *, run_id, **kwargs):
        ms = (time.perf_counter() - self._starts.pop(run_id, time.perf_counter())) * 1000
        content = getattr(output, "content", output) # returns ToolMessage or raw 
        logger.info(f"[{self.thread_id}] TOOL END {ms:.0f} ms output={_trunc(content)}")


    async def on_tool_error(self, error, *, run_id, **kwargs):
        self._starts.pop(run_id, None)
        logger.error(f"[{self.thread_id}] TOOL ERROR {error!r}")

    async def on_llm_end(self, response, **kwargs):
        gen = response.generations[0][0]    
        msg = getattr(gen, "message", None)
        calls = getattr(gen, "tool_calls", None)
        usage = getattr(gen, "usage_metadaa", None)
        logger.info(f"[{self.thread_id}] LLM END tool_calls={calls} usage={usage}")

    