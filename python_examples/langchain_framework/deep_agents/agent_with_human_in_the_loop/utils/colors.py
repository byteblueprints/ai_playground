import sys


def _enable_windows_virtual_terminal() -> None:
    """Force-enable ANSI escape processing on Windows consoles.

    colorama's autodetection can fail to enable virtual terminal
    processing when stdout is wrapped by a launcher (e.g. ``uv run``),
    even though the underlying console does support it. Calling
    SetConsoleMode directly is a reliable fallback.
    """
    if sys.platform != "win32":
        return

    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        for handle_id in (-11, -12):  # STD_OUTPUT_HANDLE, STD_ERROR_HANDLE
            handle = kernel32.GetStdHandle(handle_id)
            if handle in (0, None, -1):
                continue
            mode = ctypes.c_uint32()
            if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                continue
            enable_vt = 0x0004  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
            kernel32.SetConsoleMode(handle, mode.value | enable_vt)
    except Exception:
        pass


_enable_windows_virtual_terminal()

try:
    from colorama import Style, init
except ImportError:  # pragma: no cover - fallback for minimal environments
    Style = None  # type: ignore[assignment]

    def init(*_: object, **__: object) -> None:
        return None


init(autoreset=False, convert=False, strip=False)

RESET = Style.RESET_ALL if Style is not None else "\033[0m"
BOLD = Style.BRIGHT if Style is not None else "\033[1m"


def _rgb(red: int, green: int, blue: int) -> str:
    """24-bit truecolor escape code.

    We deliberately avoid colorama's named `Fore.*` colors (standard 16-color
    ANSI codes 30-37/90-97): most terminal themes let users freely remap
    those 16 slots, so e.g. "magenta" and "cyan" can end up rendering as
    near-identical hues depending on the user's color scheme. Explicit RGB
    values sidestep the terminal's palette entirely.
    """
    return f"\033[38;2;{red};{green};{blue}m"


ENTITY_COLORS = {
    "coordinator": _rgb(0, 174, 239),  # sky blue
    "subagent": _rgb(255, 191, 0),  # amber
    "subagent_status": _rgb(50, 205, 50),  # lime green
    "subagent_input": _rgb(135, 206, 250),  # light blue
    "subagent_output": _rgb(255, 160, 122),  # light salmon
    "tool": _rgb(255, 105, 180),  # hot pink
    "tool_status": _rgb(255, 140, 66),  # orange
    "error": _rgb(255, 85, 85),  # red
    "neutral": _rgb(220, 220, 220),  # light gray
    "reasoning": _rgb(178, 102, 255),  # lavender
    "reasoning_status": _rgb(64, 224, 208),  # turquoise
    "user": _rgb(80, 220, 100),  # green
}


def colorize(text: str, entity: str, *, bold: bool = False) -> str:
    color = ENTITY_COLORS.get(entity, ENTITY_COLORS["neutral"])
    prefix = f"{BOLD}{color}" if bold else color
    return f"{prefix}{text}{RESET}"