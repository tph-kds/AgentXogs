"""
Rich output rendering for AgentXogs CLI with colors and formatting.
Enhanced with rich-gradient for animated gradients, panels, and rules.
"""

from __future__ import annotations

import asyncio
import json
from shutil import get_terminal_size
import sys
import threading
import time
from datetime import datetime
from typing import Any, Callable, List, Optional, Tuple
from rich import print as rprint
from rich.console import Console
from rich.box import ROUNDED, HEAVY, ASCII, DOUBLE
from rich.rule import Rule
from rich_gradient import Gradient, Panel, AnimatedGradient, AnimatedPanel
from rich.text import Text
from rich.segment import Segment
from rich.align import Align

# ANSI color codes
COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "italic": "\033[3m",
    "underline": "\033[4m",
    
    # Foreground colors
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    
    # Bright foreground colors
    "bright_black": "\033[90m",
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_magenta": "\033[95m",
    "bright_cyan": "\033[96m",
    "bright_white": "\033[97m",
    
    # Background colors (40-47)
    "bg_black": "\033[40m",
    "bg_red": "\033[41m",
    "bg_green": "\033[42m",
    "bg_yellow": "\033[43m",
    "bg_blue": "\033[44m",
    "bg_magenta": "\033[45m",
    "bg_cyan": "\033[46m",
    "bg_white": "\033[47m",
    
    # Bright background colors (100-107)
    "bg_bright_black": "\033[100m",
    "bg_bright_red": "\033[101m",
    "bg_bright_green": "\033[102m",
    "bg_bright_yellow": "\033[103m",
    "bg_bright_blue": "\033[104m",
    "bg_bright_magenta": "\033[105m",
    "bg_bright_cyan": "\033[106m",
    "bg_bright_white": "\033[107m",
}

# Emojis for visual feedback
EMOJIS = {
    "success": "✓",
    "error": "✗",
    "warning": "⚠",
    "info": "ℹ",
    "思考": "🔮",
    "fetch": "📥",
    "parse": "📋",
    "analyze": "🔍",
    "detect": "🚨",
    "summary": "📊",
    "hypothesis": "🧪",
    "action": "🎯",
    "time": "⏱",
    "logs": "📄",
    "events": "⚡",
    "metrics": "📈",
    "arrow": "➤",
}

# Box styles for gradient panels
BOX_STYLES = {
    "rounded": ROUNDED,
    "heavy": HEAVY,
    "ascii": ASCII,
    "double": DOUBLE,
}

# Predefined gradient color palettes
GRADIENT_PALETTES = {
    # Classic gradients
    "sunset": ["#FF6B6B", "#FF8E53", "#F9D423", "#FF6B6B"],
    "ocean": ["#4ECDC4", "#44A08D", "#093637"],
    "rainbow": ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00", "#0000FF", "#4B0082", "#9400D3"],
    "neon": ["#FF00FF", "#00FFFF", "#FF00FF"],
    "fire": ["#FF4500", "#FF8C00", "#FFD700"],
    "aurora": ["#00FF87", "#60EFFF", "#00FF87"],
    "cosmic": ["#7B4397", "#DC2430", "#FDC830"],
    
    # New gradients
    "midnight": ["#0F0C29", "#302B63", "#24243E"],
    "hacker": ["#00FF00", "#00CC00", "#009900"],
    "royal": ["#141E30", "#243B55", "#141E30"],
    "berry": ["#833ab4", "#fd1d1d", "#fcb045"],
    "slime": ["#bdc3c7", "#2c3e50", "#bdc3c7"],
    "matrix": ["#00FF00", "#CCFFCC", "#00FF00"],
    "plasma": ["#FF6B6B", "#C44569", "#772E79"],
    "vapor": ["#FF71CE", "#01CDDE", "#05FFE1", "#FF71CE"],
    "void": ["#000000", "#1A1A2E", "#16213E", "#0F3460"],
    "candy": ["#F0F", "#0FF", "#F0F"],
    "gold": ["#FFD700", "#FFA500", "#FFD700"],
    "silver": ["#C0C0C0", "#E8E8E8", "#C0C0C0"],
    "ruby": ["#E0115F", "#900020", "#E0115F"],
    "emerald": ["#50C878", "#2E8B57", "#50C878"],
    "sapphire": ["#0F52BA", "#0067A5", "#0F52BA"],
    "amethyst": ["#9966CC", "#663399", "#9966CC"],
    
    # Status gradients
    "success": ["#00B09B", "#96C93D"],
    "warning": ["#F2994A", "#F2C94C"],
    "error": ["#EB5757", "#C0392B"],
    "info": ["#2F80ED", "#56CCF2"],
}

# Global console for rich-gradient
_console = Console()


class Align:
    """Text alignment utilities."""
    
    @staticmethod
    def center(text, width: int = None, fillchar: str = " ") -> str:
        """Center text within a given width.
        
        Args:
            text: The text (str or Text) to center
            width: The total width (default: console width - 4)
            fillchar: Character to fill (default: space)
        
        Returns:
            Centered text string
        """
        width = width or (_console.width - 4)
        if isinstance(text, str):
            return text.center(width, fillchar)
        else:
            # Rich Text object - use Rich's Align
            from rich.align import Align as RichAlign
            return RichAlign(text, align="center", width=width)
    
    @staticmethod
    def left(text, width: int = None, fillchar: str = " ") -> str:
        """Left-align text within a given width.
        
        Args:
            text: The text (str or Text) to left-align
            width: The total width (default: console width - 4)
            fillchar: Character to fill (default: space)
        
        Returns:
            Left-aligned text string
        """
        width = width or (_console.width - 4)
        if isinstance(text, str):
            return text.ljust(width, fillchar)
        else:
            from rich.align import Align as RichAlign
            return RichAlign(text, align="left", width=width)
    
    @staticmethod
    def right(text, width: int = None, fillchar: str = " ") -> str:
        """Right-align text within a given width.
        
        Args:
            text: The text (str or Text) to right-align
            width: The total width (default: console width - 4)
            fillchar: Character to fill (default: space)
        
        Returns:
            Right-aligned text string
        """
        width = width or (_console.width - 4)
        if isinstance(text, str):
            return text.rjust(width, fillchar)
        else:
            from rich.align import Align as RichAlign
            return RichAlign(text, align="right", width=width)
    
    @staticmethod
    def center_lines(lines: list, width: int = None) -> str:
        """Center multiple lines.
        
        Args:
            lines: List of text lines (str or Text)
            width: The total width
        
        Returns:
            Centered text with newlines
        """
        width = width or (_console.width - 4)
        centered = [Align.center(line, width) for line in lines]
        return "\n".join(centered)


class AnimatedGradientText:
    """Animated gradient text that cycles through colors."""
    
    def __init__(
        self,
        text: str,
        palette: list[str] = None,
        interval: float = 0.15,
        iterations: int = 0,  # 0 = infinite
    ):
        self.text = text
        self.colors = palette or GRADIENT_PALETTES["neon"]
        self.interval = interval
        self.iterations = iterations
        self._running = False
        self._stop_event = threading.Event()
    
    def _animate(self, callback: Callable[[str], None]):
        """Animation loop."""
        iteration = 0
        idx = 0
        
        while not self._stop_event.is_set():
            if self.iterations > 0 and iteration >= self.iterations:
                break
            
            colors = self.colors
            result = ""
            char_count = len(self.text)
            color_count = len(colors)
            
            for i, char in enumerate(self.text):
                color_idx = (idx + i) % color_count
                result += f"[{colors[color_idx]}]{char}[/]"
            
            callback(f"\r{result}", end="", flush=True)
            idx = (idx + 1) % color_count
            iteration += 1
            time.sleep(self.interval)
        
        # Clear the line
        callback("\r" + " " * 80 + "\r")
    
    def start(self, callback: Callable[[str], None] = None):
        """Start the animation."""
        self._stop_event.clear()
        self._running = True
        callback = callback or print
        thread = threading.Thread(target=self._animate, args=(callback,), daemon=True)
        thread.start()
        return thread
    
    def stop(self):
        """Stop the animation."""
        self._stop_event.set()
        self._running = False


class GradientRule:
    """Create gradient separator lines (rules)."""
    
    @staticmethod
    def create(
        text: str = "",
        colors: list[str] = None,
        width: int = None,
        align: str = "center",
        style: str = "rounded",
    ) -> Rule:
        """Create a gradient rule.
        
        Args:
            text: Text to display in the rule
            colors: List of colors for gradient
            width: Total width of the rule
            align: Text alignment ('left', 'center', 'right')
            style: Box style ('rounded', 'heavy', 'ascii', 'double')
        
        Returns:
            A Rich Rule object with gradient
        """
        colors = colors or GRADIENT_PALETTES["sunset"]
        width = width or _console.width
        
        if text:
            rule = Rule(text, align=align, style="cyan")
        else:
            rule = Rule(style="cyan")
        
        return rule
    
    @staticmethod
    def gradient_line(
        length: int = 50,
        colors: list[str] = None,
        direction: str = "horizontal",
    ) -> str:
        """Create a gradient line string.
        
        Args:
            length: Length of the line
            colors: Colors to gradient through
            direction: 'horizontal' or 'vertical'
        
        Returns:
            A string with gradient colors
        """
        colors = colors or GRADIENT_PALETTES["ocean"]
        
        if direction == "horizontal":
            segments = len(colors)
            seg_len = length // segments
            result = ""
            
            for i, color in enumerate(colors):
                is_last = i == segments - 1
                seg_l = seg_len + (length % segments if is_last else 0)
                result += f"[{color}]{'─' * seg_l}[/]"
            
            return result
        else:
            return '\n'.join([f"[{color}]│[/]" for color in colors for _ in range(length // len(colors))])


class OutputFormatter:
    """Rich output formatter with colors and styling."""
    
    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors and sys.stdout.isatty()
    
    def _color(self, color: str, text: str = "") -> str:
        """Apply color to text."""
        if not self.use_colors:
            return text
        return f"{COLORS.get(color, COLORS['reset'])}{text}{COLORS['reset']}"
    
    def block(self, width: int = 1, height: int = 1, color: str = "reset", force_color: bool = False) -> str:
        """Create a colored block with specific width and height.
        
        Args:
            width: Number of characters wide (default: 1)
            height: Number of lines tall (default: 1)
            color: Color name (default: reset)
            force_color: Force color output even if not a tty
        
        Returns:
            A string representing a colored block
        """
        if not self.use_colors and not force_color:
            return " " * width * height
        char = " "
        bg = COLORS.get(f"bg_{color}", COLORS.get(color, ""))
        reset = COLORS.get("reset", "\033[0m")
        line = f"{bg}{char * width}{reset}"
        return line * height
    
    def block_line(self, width: int, color: str = "reset", force_color: bool = False) -> str:
        """Create a single line colored block.
        
        Args:
            width: Number of characters wide
            color: Color name
            force_color: Force color output even if not a tty
        
        Returns:
            A string representing a colored line block
        """
        if not self.use_colors and not force_color:
            return " " * width
        bg = COLORS.get(f"bg_{color}", COLORS.get(color, ""))
        reset = COLORS.get("reset", "\033[0m")
        return f"{bg}{' ' * width}{reset}"
    
    def gradient_block(self, width: int, colors: list[str] = None) -> str:
        """Create a horizontal gradient block.
        
        Args:
            width: Total width of the block
            colors: List of colors to gradient through
        
        Returns:
            A string representing a gradient block
        """
        if colors is None:
            colors = ["cyan", "blue", "magenta"]
        if not self.use_colors:
            return " " * width
        
        segments = len(colors)
        seg_width = width // segments
        result = ""
        reset = COLORS.get("reset", "\033[0m")
        
        for i, color in enumerate(colors):
            is_last = i == segments - 1
            seg_w = seg_width + (width % segments if is_last else 0)
            bg = COLORS.get(f"bg_{color}", COLORS.get(color, ""))
            result += f"{bg}{' ' * seg_w}"
        
        return f"{result}{reset}"
    
    def _style(self, style: str, text: str) -> str:
        """Apply style to text."""
        if not self.use_colors:
            return text
        return f"{COLORS.get(style, '')}{text}{COLORS['reset']}"

    def arrow_line(self, length: int = 10, color: str = "bright_blue") -> str:
        """Create an arrow line."""
        arrow = EMOJIS["arrow"]
        line = arrow + "─" * (length - 1)
        return self._color(color, line)
        
    def title(self, text: str) -> str:
        """Display a title."""
        line = "=" * (len(text) + 4)
        return f"\n{self._color('bright_cyan', line)}\n{self._color('bright_cyan', '│ ')}{self._color('bold', text)}{self._color('bright_cyan', ' │')}\n{self._color('bright_cyan', line)}\n"
    
    def header(self, text: str) -> str:
        """Display a section header."""
        return f"\n{self._color('bright_blue', '▶')} {self._color('bold', text)}\n"
    
    def success(self, text: str) -> str:
        """Display success message."""
        return f"{self._color('green', EMOJIS['success'])} {text}"
    
    def error(self, text: str) -> str:
        """Display error message."""
        return f"{self._color('red', EMOJIS['error'])} {text}"
    
    def warning(self, text: str) -> str:
        """Display warning message."""
        return f"{self._color('yellow', EMOJIS['warning'])} {text}"
    
    def info(self, text: str) -> str:
        """Display info message."""
        return f"{self._color('blue', EMOJIS['info'])} {text}"
    
    def thinking(self, text: str) -> str:
        """Display thinking/thinking indicator."""
        return f"{self._color('magenta', EMOJIS['思考'])} {self._style('italic', text)}"
    
    def metric(self, label: str, value: Any, unit: str = "") -> str:
        """Display a metric."""
        return f"{self._color('cyan', label)}: {self._color('bright_white', str(value))} {unit}"
    
    def timestamp(self, dt: datetime) -> str:
        """Display formatted timestamp."""
        return self._color('dim', dt.strftime("%Y-%m-%d %H:%M:%S"))
    
    def json_pretty(self, data: Any) -> str:
        """Format JSON data with colors."""
        json_str = json.dumps(data, indent=2, sort_keys=True)
        if not self.use_colors:
            return json_str
        
        # Simple syntax highlighting for JSON
        result = []
        in_string = False
        for i, char in enumerate(json_str):
            if char == '"' and (i == 0 or json_str[i-1] != '\\'):
                in_string = not in_string
                result.append(COLORS['green'])
                result.append(char)
                result.append(COLORS['reset'])
            elif in_string:
                result.append(char)
            elif json_str[i:i+5] in ['true', 'fals']:
                result.append(COLORS['bright_magenta'])
                result.append(char)
                result.append(COLORS['reset'])
            elif json_str[i:i+4] == 'null':
                result.append(COLORS['dim'])
            else:
                result.append(char)
        return ''.join(result)
    
    def divider(self, char: str = "─", length: int = 50) -> str:
        """Display a divider line."""
        return self._color('dim', char * length)
    
    def box(
        self,
        text: str,
        title: str = "",
        border_color: str = "bright_blue",
        padding: Optional[tuple[int, int]] = (1, 1),
    ) -> str:
        """Display text in a box."""
        lines = text.split('\n')
        max_len = max(len(line) for line in lines)
        box_width = max_len + (padding[1] * 2) + 2
        
        top = self._color(border_color, "┌" + "─" * (box_width - 2) + "┐")
        bottom = self._color(border_color, "└" + "─" * (box_width - 2) + "┘")
        
        content = []
        for line in lines:
            padded = " " * padding[1] + line + " " * (max_len - len(line) + padding[1])
            content.append(self._color(border_color, "│") + padded + self._color(border_color, "│"))
        
        if title:
            title_line = f" {title} "
            title_padding = "─" * ((box_width - len(title_line) - 2) // 2)
            title_bar = self._color(border_color, f"├{title_padding}{title_line}{title_padding}┤")
        
        result = [top] + content + [bottom]
        return '\n'.join(result)
    
    def list_item(self, bullet: str, text: str, indent: int = 0) -> str:
        """Display a list item."""
        prefix = "  " * indent
        return f"{prefix}{self._color('bright_blue', bullet)} {text}"
    
    def highlight(self, text: str, highlight: str) -> str:
        """Highlight specific text."""
        return text.replace(highlight, self._color('bright_yellow', highlight))
    
    def gradient_title(
            self, 
            title: str, 
            inline_text: str = "", 
            palette: str = "sunset", 
            subtitle: Optional[str] = "", 
            animated: Optional[bool] = False,
            padding: Optional[tuple[int, int]] = (1, 4),
    ) -> None:
        """Print a gradient title using rich-gradient Panel.
        
        Args:
            text: The title text to display (centered in box)
            inline_text: Optional inline text to display in the title
            palette: Name of gradient palette to use (default: sunset)
            subtitle: Optional subtitle text (bottom-right of box)
            animated: Whether to show animated dots
            padding: Padding (top, bottom)
        """
        colors = GRADIENT_PALETTES.get(palette, GRADIENT_PALETTES["sunset"])
        
        # Create animated inline_text if requested
        if animated:
            dots = ["   ", ".  ", ".. ", "..."]
            inline_text = dots[0]  # Static for now, would need animation context
        
        # Use first positional arg for centered inline_text, title for top-center, subtitle for bottom-right
        panel = Panel(
            inline_text,
            title=(" " + title + " ") if title else None,
            subtitle=subtitle if subtitle else "Powered by AgentXogs",
            colors=colors,
            box=ROUNDED,
            padding=padding,
            expand=True,
        )
        _console.print(Align.center(panel))
    
    def gradient_panel(
        self, 
        inline_text: str,
        title: str, 
        palette: str = "sunset", 
        subtitle: str = "",
        box_style: str = "rounded",
        animated: bool = False,
        padding: Optional[tuple[int, int]] = (1, 2),
    ) -> None:
        """Display content in a gradient panel.
        
        Args:
            title: The title text (centered at top of box)
            inline_text: The inline_text to display
            palette: Name of gradient palette to use
            subtitle: Optional subtitle text (bottom-right of box)
            box_style: Box style ('rounded', 'heavy', 'ascii', 'double')
            animated: Whether to use animated panel
            padding: Padding inside the box
        """
        colors = GRADIENT_PALETTES.get(palette, GRADIENT_PALETTES["sunset"])
        box = BOX_STYLES.get(box_style, ROUNDED)
        
        if animated:
            # Use AnimatedPanel for animated gradient effect
            panel = AnimatedPanel(
                inline_text,
                title=(" " + title + " ") if title else None,
                subtitle="Powered by AgentXogs" if not subtitle else subtitle,
                colors=colors,
                box=box,
                padding=padding,
                expand=True,
            )
        else:
            panel = Panel(
                inline_text,
                title=(" " + title + " ") if title else None,
                subtitle="Powered by AgentXogs" if not subtitle else subtitle,
                colors=colors,
                box=box,
                padding=padding,
                expand=True,
            )
        _console.print(Align.center(panel))
    
    def gradient_text(self, text: str, palette: str = "ocean") -> str:
        """Create gradient text.
        
        Args:
            text: The text to gradient
            palette: Name of gradient palette to use
        
        Returns:
            Gradient renderable
        """
        colors = GRADIENT_PALETTES.get(palette, GRADIENT_PALETTES["ocean"])
        return Gradient(text, colors=colors)
    
    def print_gradient(self, text: str, palette: str = "neon") -> None:
        """Print gradient text.
        
        Args:
            text: The text to display
            palette: Name of gradient palette to use
        """
        colors = GRADIENT_PALETTES.get(palette, GRADIENT_PALETTES["neon"])
        gradient = Gradient(text, colors=colors)
        _console.print(gradient)
    
    def print_animated_gradient(
        self, 
        text: str, 
        palette: str = "neon", 
        iterations: int = 0,
        interval: float = 0.15,
    ) -> None:
        """Print animated gradient text.
        
        Args:
            text: The text to display
            palette: Name of gradient palette to use
            iterations: Number of iterations (0 = infinite)
            interval: Animation speed in seconds
        """
        colors = GRADIENT_PALETTES.get(palette, GRADIENT_PALETTES["neon"])
        animated = AnimatedGradientText(
            text=text,
            palette=colors,
            iterations=iterations,
            interval=interval,
        )
        
        def callback(output: str, **kwargs):
            _console.print(output, **kwargs)
        
        animated.start(callback)
        
        # If finite iterations, wait for completion
        if iterations > 0:
            time.sleep(iterations * interval * len(colors) / 10)
            animated.stop()
    
    def print_gradient_rule(
        self,
        text: str = "",
        palette: str = "sunset",
        width: int = None,
        align: str = "center",
    ) -> None:
        """Print a gradient rule/separator line.
        
        Args:
            text: Text to display in the rule (optional)
            palette: Name of gradient palette to use
            width: Width of the rule
            align: Text alignment ('left', 'center', 'right')
        """
        colors = GRADIENT_PALETTES.get(palette, GRADIENT_PALETTES["sunset"])
        width = width or _console.width - 4
        
        if text:
            # Create gradient text for the rule
            gradient_text = ""
            char_count = len(text)
            color_count = len(colors)
            
            for i, char in enumerate(text):
                color_idx = (i * color_count) // char_count
                gradient_text += f"[{colors[color_idx]}]{char}[/]"
            
            rule = Rule(gradient_text, align=align, style=colors[0])
        else:
            rule = Rule(style=colors[0])
        
        _console.print(rule)
    
    def print_gradient_box(
        self,
        inline_text: str,
        title: str = "",
        subtitle: str = "",
        palette: str = "sunset",
        box_style: str = "rounded",
        padding: Optional[tuple[int, int]] = (1, 2),
    ) -> None:
        """Print inline_text in a gradient box with border.
        
        Args:
            inline_text: The inline_text to display
            title: Optional title for the box
            subtitle: Optional subtitle text (displayed below main text)
            palette: Name of gradient palette to use
            box_style: Box style ('rounded', 'heavy', 'ascii', 'double')
            padding: Padding inside the box
        """
        colors = GRADIENT_PALETTES.get(palette, GRADIENT_PALETTES["sunset"])
        box = BOX_STYLES.get(box_style, ROUNDED)
        
        # Create a simple panel with gradient border
        panel = Panel(
            inline_text,
            title=(" " + title + " ") if title else None,
            subtitle="Powered by AgentXogs" if not subtitle else subtitle,
            colors=colors,
            box=box,
            padding=padding,
        )
        _console.print(Align.center(panel))
    
    def print_centered_box(
        self,
        inline_text: str,
        title: str,
        subtitle: str = "",
        palette: str = "sunset",
        box_style: str = "rounded",
        padding: Optional[tuple[int, int]] = (1, 2),
    ) -> None:
        """Print centered text in a gradient box.
        
        Args:
            inline_text: The centered text to display
            title: title for the box
            subtitle: Optional subtitle text (displayed below main text)
            palette: Name of gradient palette to use
            box_style: Box style ('rounded', 'heavy', 'ascii', 'double')
            padding: Padding inside the box
        """
        colors = GRADIENT_PALETTES.get(palette, GRADIENT_PALETTES["sunset"])
        box = BOX_STYLES.get(box_style, ROUNDED)
        
        # Format content with centered text
        if subtitle:
            inline_text = f"\n{inline_text}\n{subtitle}\n"
        else:
            inline_text = f"\n{inline_text}\n"
        
        panel = Panel(
            inline_text,
            title=title,
            subtitle="Powered by AgentXogs" if not subtitle else subtitle,
            colors=colors,
            box=box,
            padding=padding,
        )
        _console.print(Align.center(panel))


# Global formatter instance
formatter = OutputFormatter()


def print_title(text: str):
    """Print a title."""
    print(formatter.title(text))


def print_header(text: str):
    """Print a section header."""
    print(formatter.header(text))


def print_success(text: str):
    """Print a success message."""
    print(formatter.success(text))


def print_error(text: str):
    """Print an error message."""
    print(formatter.error(text))


def print_warning(text: str):
    """Print a warning message."""
    print(formatter.warning(text))


def print_info(text: str):
    """Print an info message."""
    print(formatter.info(text))


def print_thinking(text: str):
    """Print a thinking indicator."""
    print(formatter.thinking(text))


def print_gradient_title(
        title: str, 
        inline_text: str = "", 
        palette: str = "sunset", 
        subtitle: Optional[str] = "", 
        animated: Optional[bool] = False,
        padding: Optional[tuple[int, int]] = (1, 4)
):
    """Print a gradient title.
    
    Args:
        title: The title text to display
        inline_text: Optional inline text to display within the title panel
        palette: Name of gradient palette to use
        subtitle: Optional subtitle to display
        animated: Whether to animate the title
        padding: Padding (top, bottom)
    """
    formatter.gradient_title(
        title=title, 
        palette=palette, 
        inline_text=inline_text, 
        subtitle=subtitle, 
        animated=animated,
        padding=padding
    )


def print_gradient(text: str, palette: str = "neon"):
    """Print gradient text.
    
    Args:
        text: The text to display
        palette: Name of gradient palette to use
    """
    formatter.print_gradient(text, palette)


def print_animated_gradient(text: str, palette: str = "neon", iterations: int = 0):
    """Print animated gradient text.
    
    Args:
        text: The text to display
        palette: Name of gradient palette to use
        iterations: Number of iterations (0 = infinite)
    """
    formatter.print_animated_gradient(text, palette, iterations)


def print_gradient_panel(
    inline_text: str,
    title: str, 
    subtitle: str = "",
    palette: str = "sunset",
    animated: bool = False,
):
    """Print inline_text in a gradient panel.
    
    Args:
        title: The panel title
        inline_text: The inline_text to display
        palette: Name of gradient palette to use
        subtitle: Optional subtitle
        animated: Whether to use animated panel
    """
    formatter.gradient_panel(
        title=title, 
        inline_text=inline_text, 
        palette=palette, 
        subtitle=subtitle, 
        animated=animated)


def print_gradient_rule(text: str = "", palette: str = "sunset", width: int = None):
    """Print a gradient rule/separator line.
    
    Args:
        text: Text to display in the rule
        palette: Name of gradient palette to use
        width: Width of the rule
    """
    formatter.print_gradient_rule(text, palette, width)


def print_gradient_box(
    inline_text: str,
    title: str = "",
    subtitle: str = "",
    palette: str = "sunset",
    box_style: str = "rounded",
    padding: Optional[tuple[int, int]] = (1, 1),
):
    """Print inline_text in a gradient box.
    
    Args:
        inline_text: The inline_text to display
        title: Optional title for the box
        subtitle: subtitle text (displayed below main text)
        palette: Name of gradient palette to use
        box_style: Box style ('rounded', 'heavy', 'ascii', 'double')
        padding: Padding tuple (vertical, horizontal)
    """
    formatter.print_gradient_box(
        inline_text=inline_text,
        title=title,
        subtitle=subtitle,
        palette=palette,
        box_style=box_style,
        padding=padding
    )


def print_arrow_line(text: str = "", length: int = 10, color: str = "bright_blue"):
    """Print an arrow line or text with arrow prefix.
    
    Args:
        text: Optional text to display after arrow
        length: Length of the arrow line
        color: Color name
    """
    if text:
        arrows = {
            "cyan": "➤",
            "green": "✓",
            "red": "✗",
            "yellow": "⚠",
            "blue": "▶",
            "purple": "◆",
        }
        arrow = arrows.get(color, arrows["cyan"])
        print(f"{formatter._color(color, arrow)} {text}")
    else:
        print(formatter.arrow_line(length, color))


def print_centered_box(
    inline_text: str,
    title: str,
    subtitle: str = "",
    palette: str = "sunset",
    box_style: str = "rounded",
    padding: Optional[tuple[int, int]] = (1, 1),
):
    """Print centered text in a gradient box.
    
    Args:
        inline_text: The centered text to display
        title: The title for the box
        subtitle: Optional subtitle text (displayed below main text)
        palette: Name of gradient palette to use
        box_style: Box style ('rounded', 'heavy', 'ascii', 'double')
        padding: Padding tuple (vertical, horizontal)
    """
    formatter.print_centered_box(
        inline_text=inline_text, 
        title=title,
        subtitle=subtitle, 
        palette=palette, 
        box_style=box_style,
        padding=padding
    )


def apply_gradient(text: str, colors: list[str], bold: bool = True) -> Text:
    """Apply gradient colors to text.
    
    Args:
        text: Text to apply gradient to
        colors: List of colors to gradient through
        bold: Whether to make text bold
    
    Returns:
        Rich Text object with gradient styling
    """
    gradient_text = Text()
    length = max(len(text), 1)
    
    for i, char in enumerate(text):
        color_index = int(i / length * (len(colors) - 1))
        style = f"bold {colors[color_index]}" if bold else colors[color_index]
        gradient_text.append(char, style=style)
    
    return gradient_text

def build_gradient_line(width: int, palette: str = "ocean") -> Text:
    colors = GRADIENT_PALETTES.get(palette, GRADIENT_PALETTES["ocean"])
    line = Text()
    length = max(width, 1)

    for i in range(length):
        color_index = int(i / length * (len(colors) - 1))
        line.append("─", style=f"color({colors[color_index]})")

    return line

def print_gradient_inline_multiple_text_with_rows(
    rows: List[List[Tuple[str, Optional[str]]]],
    sep: str = "   ",
    separator_palette: str = "ocean",
):
    # 1️⃣ Calculate max column widths
    col_count = max(len(row) for row in rows)
    col_widths = [0] * col_count

    for row in rows:
        for i, (text, _) in enumerate(row):
            col_widths[i] = max(col_widths[i], len(text))

    rendered_lines = []

    # 2️⃣ Build aligned rows
    for irow, row in enumerate(rows):
        line = Text()

        for i, (text, palette) in enumerate(row):
            padded = text.center(col_widths[i])

            if palette:
                colors = GRADIENT_PALETTES.get(palette, GRADIENT_PALETTES["neon"])
                line.append(apply_gradient(padded, colors))
            else:
                line.append(padded)

            if i < len(row) - 1:
                line.append(sep)

        rendered_lines.append(line)

        # 3️⃣ Insert separator BETWEEN rows
        if irow < len(rows) - 1:
            block_width = len(line.plain)
            rendered_lines.append(
                build_gradient_line(block_width, separator_palette)
            )

    # 4️⃣ Center entire block
    for line in rendered_lines:
        _console.print(Align.center(line))


# Gradient Rule
gradient_with_rule = GradientRule()

def print_gradient_with_rule(
    text: str,
    palette: str = "sunset",
    width: int = None,
    align: str = "center",
    style: str = "rounded",
    n_colors: int = 1,
):
    """Print gradient text with a rule above and below.
    
    Args:
        text: The text to display
        palette: Name of gradient palette to use
        width: Width of the rule
        align: Text alignment ('left', 'center', 'right')
        style: Box style ('rounded', 'heavy', 'ascii', 'double')
        n_colors: Number of colors to use
    """
    colors = GRADIENT_PALETTES.get(palette, GRADIENT_PALETTES["sunset"])
    width = width or _console.width - 4
    
    # Create gradient text for the rule
    gradient_text = ""
    char_count = len(text)
    
    for i, char in enumerate(text):
        color_idx = int(i / char_count * (len(colors) - 1))
        if n_colors < 1 and n_colors != -1:
            n_colors = 1
        if n_colors == -1:
            n_colors = len(colors) + 1
        elif n_colors == 1:
            color_idx = 0
        elif n_colors == 2:
            color_idx = 0 if i < char_count / 2 else len(colors) - 1
        elif n_colors >= 3:
            segment_length = char_count / (n_colors - 1)
            color_idx = min(int(i / segment_length), n_colors - 1)

        gradient_text += f"[{colors[color_idx]}]{char}[/]"
    
    # Print rule with gradient text
    rule = Rule(gradient_text, align=align, style=style)
    _console.print(rule)
