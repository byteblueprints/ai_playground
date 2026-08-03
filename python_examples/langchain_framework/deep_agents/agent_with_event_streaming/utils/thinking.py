import sys
import threading
import time
from typing import Optional

from .colors import colorize

# ANSI: return cursor to column 0, then clear the rest of the line. Needed
# so leftover spinner text isn't left dangling when it's replaced with
# something shorter (e.g. "Assistant: | processing" -> "").
_CLEAR_LINE = "\r\033[K"


class ThinkingIndicator:
    def __init__(
        self,
        label: str = "Assistant",
        entity: str = "coordinator",
        frames: Optional[list[str]] = None,
        interval: float = 0.08,
    ) -> None:
        self.label = colorize(f"{label}:", entity, bold=True)
        self.frames = frames or ["|", "/", "-", "\\"]
        self.interval = interval
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._index = 0

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self, final_message: str = "") -> None:
        if not self._thread:
            return

        self._stop_event.set()
        self._thread.join(timeout=0.2)
        self._thread = None
        if final_message:
            sys.stdout.write(f"{_CLEAR_LINE}{self.label} {final_message}\n")
        else:
            sys.stdout.write(_CLEAR_LINE)
        sys.stdout.flush()

    def _run(self) -> None:
        while not self._stop_event.is_set():
            frame = self.frames[self._index % len(self.frames)]
            self._index += 1
            sys.stdout.write(f"{_CLEAR_LINE}{self.label} {frame} Processing")
            sys.stdout.flush()
            time.sleep(self.interval)

    def clear(self) -> None:
        sys.stdout.write(_CLEAR_LINE)
        sys.stdout.flush()