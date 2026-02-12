"""
Rich Live Display - Smooth UI re-rendering with real-time updates.
Uses Rich's Live context manager for flicker-free terminal updates.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Callable, Optional, Dict, List
from rich.live import Live
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.layout import Layout
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.style import Style
from rich import box
from rich.box import ROUNDED, HEAVY

from .output import GRADIENT_PALETTES, _console

# Animation frames
SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
THINKING_FRAMES = ["◌", "◍", "◎", "●", "◐", "◑"]


class LiveStatusDisplay:
    """Rich Live display for real-time status updates with smooth re-rendering."""
    
    def __init__(
        self,
        console: Console = None,
        transient: bool = False,
        refresh_per_second: float = 4.0,
    ):
        self.console = console or _console
        self.transient = transient
        self.refresh_per_second = refresh_per_second
        self._live: Optional[Live] = None
        self._current_stage = ""
        self._status_message = ""
        self._progress_value = 0
        self._total_steps = 100
        self._completed_steps: List[str] = []
        self._is_running = False
    
    def _render_content(self) -> Panel:
        """Render the current state as a Panel."""
        # Build status content
        content = Text()
        
        # Current stage with highlight
        if self._current_stage:
            content.append(f"● {self._current_stage}\n", style="bold cyan")
        
        # Status message
        if self._status_message:
            content.append(f"{self._status_message}\n", style="dim")
        
        # Progress bar
        bar_width = 30
        filled = int(bar_width * self._progress_value / max(1, self._total_steps))
        bar = "█" * filled + "░" * (bar_width - filled)
        percent = int(self._progress_value / max(1, self._total_steps) * 100)
        content.append(f"[{bar}] {percent}%\n", style="cyan")
        
        # Completed steps
        if self._completed_steps:
            content.append("\n✓ Completed:\n", style="green")
            for step in self._completed_steps[-5:]:  # Show last 5
                content.append(f"  ✓ {step}\n", style="dim green")
        
        # Spinner animation
        import time
        frame = SPINNER_FRAMES[int(time.time() * self.refresh_per_second) % len(SPINNER_FRAMES)]
        content.append(f"\n{frame} Processing...", style="magenta")
        
        return Panel(
            content,
            title="[bold]AgentX Live Status[/bold]",
            subtitle=f"Last updated: {datetime.now().strftime('%H:%M:%S')}",
            box=ROUNDED,
            style="cyan on black",
            padding=(1, 2),
        )
    
    def start(self, title: str = "Processing..."):
        """Start the live display."""
        self._is_running = True
        self._live = Live(
            self._render_content(),
            console=self.console,
            transient=self.transient,
            refresh_per_second=self.refresh_per_second,
        )
        self._live.start()
    
    def update(
        self,
        stage: str = None,
        message: str = None,
        progress: int = None,
        total: int = None,
        completed: str = None,
    ):
        """Update the display with new values."""
        if stage is not None:
            self._current_stage = stage
        if message is not None:
            self._status_message = message
        if progress is not None:
            self._progress_value = progress
        if total is not None:
            self._total_steps = total
        if completed is not None:
            if completed not in self._completed_steps:
                self._completed_steps.append(completed)
        
        if self._live and self._is_running:
            self._live.update(self._render_content())
    
    def set_progress(self, current: int, total: int = None):
        """Set progress percentage."""
        self._progress_value = current
        if total is not None:
            self._total_steps = total
        if self._live and self._is_running:
            self._live.update(self._render_content())
    
    def add_completed(self, step_name: str):
        """Mark a step as completed."""
        self._completed_steps.append(step_name)
        if self._live and self._is_running:
            self._live.update(self._render_content())
    
    def stop(self, final_message: str = None):
        """Stop the live display."""
        self._is_running = False
        if self._live:
            self._live.stop()
            if final_message:
                self.console.print(f"✓ {final_message}")


class LivePipelineDisplay:
    """Live display for pipeline steps with smooth transitions."""
    
    def __init__(
        self,
        console: Console = None,
        refresh_per_second: float = 8.0,
    ):
        self.console = console or _console
        self.refresh_per_second = refresh_per_second
        self._live: Optional[Live] = None
        self._steps: List[Dict[str, Any]] = []
        self._current_step = -1
        self._is_running = False
    
    def _render_content(self) -> Panel:
        """Render pipeline status as a styled table."""
        table = Table(show_header=False, box=None, padding=0)
        table.add_column("Status", width=4)
        table.add_column("Step", width=30)
        table.add_column("Progress", width=35)
        
        import time
        frame = SPINNER_FRAMES[int(time.time() * self.refresh_per_second) % len(SPINNER_FRAMES)]
        
        for i, step in enumerate(self._steps):
            status_icon = ""
            style = "dim"
            
            if i < self._current_step or step.get("progress", 0) >= 100:
                status_icon = "✓"
                style = "green"
            elif i == self._current_step:
                status_icon = frame
                style = "bold cyan"
            elif i > self._current_step:
                status_icon = "○"
                style = "dim white"
            
            # Progress bar for current step (show 100% as Done)
            if step.get("progress", 0) >= 100:
                progress_text = "Done"
                style = "green"
            elif i == self._current_step and step.get("progress", 0) > 0:
                bar_width = 25
                prog = step.get("progress", 0)
                filled = int(bar_width * prog / 100)
                bar = "█" * filled + "░" * (bar_width - filled)
                progress_text = f"[{bar}] {prog}%"
            else:
                progress_text = step.get("status", "")
            
            table.add_row(
                f"[{style}]{status_icon}[/]",
                f"[{style}]{step['name']}[/]",
                f"[{style}]{progress_text}[/]",
            )
        
        return Panel(
            table,
            title="[bold cyan]Pipeline Progress[/bold cyan]",
            subtitle="Real-time Analysis Updates",
            box=ROUNDED,
            style="cyan on black",
            padding=(1, 2),
        )
    
    def set_steps(self, steps: List[str]):
        """Initialize steps list."""
        self._steps = [
            {"name": step, "status": "", "progress": 0}
            for step in steps
        ]
        self._current_step = -1
    
    def start_step(self, step_index: int, message: str = ""):
        """Mark a step as current."""
        self._current_step = step_index
        if step_index < len(self._steps):
            self._steps[step_index]["status"] = message or "Running..."
            self._steps[step_index]["progress"] = 0
        
        if self._live and self._is_running:
            self._live.update(self._render_content())
    
    def update_progress(self, progress: int):
        """Update current step progress."""
        if self._current_step >= 0 and self._current_step < len(self._steps):
            self._steps[self._current_step]["progress"] = progress
            # Auto-complete step when progress reaches 100%
            if progress >= 100:
                self._steps[self._current_step]["status"] = "Done"
                self._steps[self._current_step]["progress"] = 100
        
        if self._live and self._is_running:
            self._live.update(self._render_content())
    
    def complete_step(self, step_index: int, status: str = "Done"):
        """Mark a step as completed."""
        if step_index < len(self._steps):
            self._steps[step_index]["status"] = status
            self._steps[step_index]["progress"] = 100
        
        if self._live and self._is_running:
            self._live.update(self._render_content())
    
    def start(self):
        """Start the live display."""
        self._is_running = True
        self._live = Live(
            self._render_content(),
            console=self.console,
            transient=False,
            refresh_per_second=self.refresh_per_second,
        )
        self._live.start()
    
    def stop(self, final_message: str = None):
        """Stop the live display."""
        self._is_running = False
        if self._live:
            self._live.stop()
        
        # Mark all remaining steps as pending
        for i, step in enumerate(self._steps):
            if i > self._current_step:
                step["status"] = "Pending"
                step["progress"] = 0
        
        # Print final state
        if self.console:
            self.console.print()
            for step in self._steps:
                if step.get("progress", 0) >= 100:
                    self.console.print(f"✓ {step['name']}: {step['status']}", style="green")
            if final_message:
                self.console.print(f"\n✓ {final_message}", style="bold green")


class LiveProgressBar:
    """Rich Progress with live updates for progress bars."""
    
    def __init__(
        self,
        console: Console = None,
        transient: bool = True,
    ):
        self.console = console or _console
        self.transient = transient
        self._progress: Optional[Progress] = None
        self._task_id: Optional[int] = None
    
    def create_progress(
        self,
        description: str = "Processing",
        total: int = 100,
        show_speed: bool = True,
    ) -> Progress:
        """Create and start a progress bar."""
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
        
        self._task_id = self._progress.add_task(
            description,
            total=total,
        )
        
        self._progress.start()
        return self._progress
    
    def update(self, advance: int = 1, visible: bool = True):
        """Advance the progress bar."""
        if self._progress and self._task_id is not None:
            self._progress.advance(self._task_id, advance)
    
    def stop(self, message: str = None):
        """Stop the progress bar."""
        if self._progress:
            self._progress.stop()
            if message:
                self.console.print(f"✓ {message}", style="green")


class LiveStatusPanel:
    """A live-updating status panel with multiple sections."""
    
    def __init__(
        self,
        title: str = "Status",
        console: Console = None,
        refresh_per_second: float = 4.0,
    ):
        self.console = console or _console
        self.refresh_per_second = refresh_per_second
        self.title = title
        self.sections: Dict[str, Any] = {}
        self._live: Optional[Live] = None
        self._is_running = False
    
    def add_section(self, name: str, content: Any, style: str = "dim"):
        """Add a section to the panel."""
        self.sections[name] = {"content": content, "style": style}
    
    def update_section(self, name: str, content: Any):
        """Update a section's content."""
        if name in self.sections:
            self.sections[name]["content"] = content
        else:
            self.add_section(name, content)
        
        if self._live and self._is_running:
            self._live.update(self._render_content())
    
    def _render_content(self) -> Panel:
        """Render the panel content."""
        content = Text()
        
        for name, section in self.sections.items():
            content.append(f"[bold]{name}:[/] ", style=section.get("style", "dim"))
            content.append(f"{section['content']}\n", style=section.get("style", "dim"))
        
        import time
        frame = SPINNER_FRAMES[int(time.time() * self.refresh_per_second) % len(SPINNER_FRAMES)]
        content.append(f"\n{frame} Live updating...", style="magenta")
        
        return Panel(
            content,
            title=f"[bold]{self.title}[/bold]",
            box=ROUNDED,
            style="cyan on black",
            padding=(1, 2),
        )
    
    def start(self):
        """Start the live display."""
        self._is_running = True
        self._live = Live(
            self._render_content(),
            console=self.console,
            transient=False,
            refresh_per_second=self.refresh_per_second,
        )
        self._live.start()
    
    def stop(self, final_message: str = None):
        """Stop the live display."""
        self._is_running = False
        if self._live:
            self._live.stop()
            if final_message:
                self.console.print(f"✓ {final_message}")


# Convenience functions for async usage
async def async_live_pipeline(
    steps: List[str],
    console: Console = None,
    step_delays: List[float] = None,
):
    """Run a pipeline with live updates (async version)."""
    display = LivePipelineDisplay(console=console)
    display.set_steps(steps)
    display.start()
    
    step_delays = step_delays or [0.5] * len(steps)
    
    for i, step in enumerate(steps):
        display.start_step(i, f"Processing {step}...")
        await asyncio.sleep(step_delays[i] * 0.5)
        display.update_progress(50)
        await asyncio.sleep(step_delays[i] * 0.5)
        display.complete_step(i, "Done")
    
    display.stop("Pipeline complete!")
    return True


# Simple sync wrapper for pipeline
def run_live_pipeline(
    steps: List[str],
    console: Console = None,
    step_delays: List[float] = None,
):
    """Run a pipeline with live updates (sync version)."""
    import time
    
    display = LivePipelineDisplay(console=console)
    display.set_steps(steps)
    display.start()
    
    step_delays = step_delays or [0.5] * len(steps)
    
    for i, step in enumerate(steps):
        display.start_step(i, f"Processing {step}...")
        time.sleep(step_delays[i] * 0.5)
        display.update_progress(50)
        time.sleep(step_delays[i] * 0.5)
        display.complete_step(i, "Done")
    
    display.stop("Pipeline complete!")
    return True
