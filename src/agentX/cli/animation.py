"""
Animated thinking indicators and spinner animations for AgentX CLI.
Enhanced with Rich Live for flicker-free smooth updates.
"""

from __future__ import annotations

import threading
import time
from typing import Callable, Optional

# Animation frames for thinking indicator
THINKING_FRAMES = [
    "   .   ",
    "  ..   ",
    " ...   ",
    "  ...  ",
    "   ...",
    "    ..",
    "     .",
    "    ..",
    "   ...",
    "  ...  ",
    "   .. ",
    "    . ",
]

SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
DOTS_FRAMES = ["   ", "·  ", "·· ", "···", " ··", "  ·", "   "]


class AnimatedSpinner:
    """Animated spinner with customizable frames - uses Rich Live for smooth updates."""
    
    def __init__(
        self,
        frames: list[str] = SPINNER_FRAMES,
        interval: float = 0.1,
        prefix: str = "",
        suffix: str = "...",
        use_live: bool = True,
    ):
        self.frames = frames
        self.interval = interval
        self.prefix = prefix
        self.suffix = suffix
        self.use_live = use_live
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callback: Optional[Callable[[str], None]] = None
        self._message = ""
        self._live = None
        self._console = None
    
    def _get_frame(self, index: int) -> str:
        """Get the frame at the given index."""
        return self.frames[index % len(self.frames)]
    
    def _render(self, index: int = 0) -> str:
        """Render the current spinner state."""
        frame = self._get_frame(index)
        return f"\r{self.prefix}{frame}{self._message} {self.suffix}"
    
    def start(self, message: str = "", callback: Optional[Callable[[str], None]] = None):
        """Start the animation."""
        self._message = message
        self._callback = callback or print
        self._running = True
        
        if self.use_live:
            # Use Rich Live for flicker-free updates
            from rich.live import Live
            from rich.console import Console
            from rich.text import Text
            
            self._console = Console()
            
            def get_renderable():
                import time
                index = int(time.time() / self.interval) % len(self.frames)
                frame = self._get_frame(index)
                return Text(f"{self.prefix}{frame}{self._message} {self.suffix}", style="cyan")
            
            self._live = Live(
                get_renderable(),
                console=self._console,
                transient=True,
                refresh_per_second=1.0 / self.interval,
            )
            self._live.start()
        else:
            # Fallback to threading-based animation
            self._thread = threading.Thread(target=self._animate, daemon=True)
            self._thread.start()
    
    def _animate(self):
        """Animation loop for threading-based animation."""
        index = 0
        while self._running:
            frame = self._get_frame(index)
            if self._callback:
                self._callback(f"\r{self.prefix}{frame}{self._message} {self.suffix}")
            index += 1
            time.sleep(self.interval)
    
    def update(self, message: str):
        """Update the message."""
        self._message = message
    
    def stop(self, final_message: str = ""):
        """Stop the animation."""
        self._running = False
        if self._live:
            self._live.stop()
        if self._thread:
            self._thread.join(timeout=0.5)
        
        # Clear the line and show final message
        print("\r" + " " * (len(self.prefix) + len(self._message) + len(self.suffix) + 15), end="\r")
        if final_message:
            print(f"\r✓ {final_message}")


class ThinkingIndicator:
    """Gemini-style thinking indicator with animated dots - uses Rich Live."""
    
    def __init__(self, interval: float = 0.4, use_live: bool = True):
        self.interval = interval
        self.use_live = use_live
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callback: Optional[Callable[[str], None]] = None
        self._stage = ""
        self._live = None
        self._console = None
    
    def _render(self, index: int = 0) -> str:
        """Render the thinking indicator state."""
        frame = THINKING_FRAMES[index % len(THINKING_FRAMES)]
        stage = self._stage or "Thinking"
        return f"\r🔮 {stage}{frame}"
    
    def start(self, stage: str = "", callback: Optional[Callable[[str], None]] = None):
        """Start the thinking indicator."""
        self._stage = stage
        self._callback = callback or print
        self._running = True
        
        if self.use_live:
            # Use Rich Live for flicker-free updates
            from rich.live import Live
            from rich.console import Console
            from rich.text import Text
            
            self._console = Console()
            
            def get_renderable():
                import time
                index = int(time.time() / self.interval) % len(THINKING_FRAMES)
                frame = THINKING_FRAMES[index]
                stage = self._stage or "Thinking"
                return Text(f"🔮 {stage}{frame}", style="magenta")
            
            self._live = Live(
                get_renderable(),
                console=self._console,
                transient=True,
                refresh_per_second=1.0 / self.interval,
            )
            self._live.start()
        else:
            # Fallback to threading-based animation
            self._thread = threading.Thread(target=self._animate, daemon=True)
            self._thread.start()
    
    def _animate(self):
        """Animation loop for threading-based animation."""
        index = 0
        while self._running:
            frame = THINKING_FRAMES[index % len(THINKING_FRAMES)]
            stage = self._stage or "Thinking"
            if self._callback:
                self._callback(f"\r🔮 {stage}{frame}")
            index += 1
            time.sleep(self.interval)
    
    def update(self, stage: str):
        """Update the thinking stage."""
        self._stage = stage
    
    def stop(self, final_message: str = ""):
        """Stop the thinking indicator."""
        self._running = False
        if self._live:
            self._live.stop()
        if self._thread:
            self._thread.join(timeout=0.5)
        
        # Clear the thinking line
        print("\r" + " " * 60, end="\r")
        if final_message:
            print(f"\r✓ {final_message}")


class ProgressBar:
    """Animated progress bar - uses Rich for smooth rendering."""
    
    def __init__(
        self,
        total: int,
        width: int = 30,
        fill: str = "█",
        empty: str = "░",
        prefix: str = "",
        use_live: bool = True,
    ):
        self.total = total
        self.width = width
        self.fill = fill
        self.empty = empty
        self.prefix = prefix
        self.current = 0
        self._running = False
        self.use_live = use_live
        self._live = None
        self._console = None
    
    def _render(self) -> str:
        """Render the current progress."""
        percent = (self.current / self.total) * 100
        filled = int(self.width * self.current // self.total)
        bar = self.fill * filled + self.empty * (self.width - filled)
        return f"\r{self.prefix} |{bar}| {percent:5.1f}%"
    
    def update(self, current: int, message: str = ""):
        """Update progress."""
        self.current = current
        percent = (current / self.total) * 100
        filled = int(self.width * current // self.total)
        bar = self.fill * filled + self.empty * (self.width - filled)
        print(f"\r{self.prefix} |{bar}| {percent:5.1f}% {message}", end="\r")
    
    def complete(self, message: str = "Done!"):
        """Complete the progress bar."""
        print(f"\r{self.prefix} |{self.fill * self.width}| 100.0% {message}")
    
    def start(self):
        """Start the progress bar with Rich Live."""
        if self.use_live:
            from rich.live import Live
            from rich.console import Console
            from rich.text import Text
            
            self._console = Console()
            
            def get_renderable():
                percent = (self.current / self.total) * 100
                filled = int(self.width * self.current // self.total)
                bar = self.fill * filled + self.empty * (self.width - filled)
                return Text(
                    f"{self.prefix} |{bar}| {percent:5.1f}%",
                    style="cyan"
                )
            
            self._live = Live(
                get_renderable(),
                console=self._console,
                transient=False,
                refresh_per_second=10.0,
            )
            self._live.start()
            self._running = True
    
    def set_progress(self, current: int):
        """Set current progress."""
        self.current = current
        if self._live and self._running:
            percent = (self.current / self.total) * 100
            filled = int(self.width * self.current // self.total)
            bar = self.fill * filled + self.empty * (self.width - filled)
            self._live.update(
                Text(f"{self.prefix} |{bar}| {percent:5.1f}%", style="cyan")
            )
    
    def stop(self, message: str = None):
        """Stop the progress bar."""
        self._running = False
        if self._live:
            self._live.stop()
        if message:
            print(f"\r✓ {message}")


def animate_thinking(
    message: str,
    duration: float = 2.0,
    stage: str = "Thinking",
) -> str:
    """
    Show animated thinking indicator for a duration.
    
    Args:
        message: Message to display
        duration: How long to show (seconds)
        stage: Current thinking stage
    
    Returns:
        The final message
    """
    indicator = ThinkingIndicator(interval=0.15)
    
    def callback(text):
        print(text, end="", flush=True)
    
    indicator.start(stage, callback)
    time.sleep(duration)
    indicator.stop()
    return message


def animated_fetch(
    message: str,
    duration: float = 1.5,
) -> str:
    """Show animated fetching indicator."""
    spinner = AnimatedSpinner(frames=SPINNER_FRAMES, interval=0.1)
    
    def callback(text):
        print(text, end="", flush=True)
    
    spinner.start(message, callback)
    time.sleep(duration)
    spinner.stop(f"Fetched: {message}")
    return message


def animated_parse(
    message: str,
    duration: float = 1.0,
) -> str:
    """Show animated parsing indicator."""
    spinner = AnimatedSpinner(frames=DOTS_FRAMES, interval=0.2)
    
    def callback(text):
        print(text, end="", flush=True)
    
    spinner.start(message, callback)
    time.sleep(duration)
    spinner.stop(f"Parsed: {message}")
    return message


# Convenience class for using Rich Progress directly
class RichProgressBar:
    """Rich Progress bar for smooth, flicker-free progress updates."""
    
    def __init__(self, console=None, transient=True):
        from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
        from rich.console import Console
        
        self.console = console or Console()
        self.transient = transient
        self._progress = None
        self._task_id = None
    
    def start(
        self,
        description: str = "Processing",
        total: int = 100,
        show_speed: bool = True,
    ):
        """Start a progress bar."""
        from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
        
        columns = [
            SpinnerColumn(style="cyan"),
            TextColumn("[bold cyan]{task.description}[/]"),
            BarColumn(complete_style="cyan", finished_style="green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ]
        
        if show_speed:
            columns.append(TimeElapsedColumn())
        
        self._progress = Progress(
            *columns,
            console=self.console,
            transient=self.transient,
        )
        
        self._task_id = self._progress.add_task(description, total=total)
        self._progress.start()
        return self
    
    def update(self, advance: int = 1, description: str = None):
        """Advance the progress bar."""
        if self._progress and self._task_id is not None:
            self._progress.advance(self._task_id, advance)
            if description:
                self._progress.update(self._task_id, description=description)
    
    def stop(self, message: str = None):
        """Stop the progress bar."""
        if self._progress:
            self._progress.stop()
            if message:
                self.console.print(f"✓ {message}", style="green")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, *args):
        """Context manager exit."""
        self.stop()
