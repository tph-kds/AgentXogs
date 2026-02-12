"""
Interactive prompts for AgentXogs CLI using questionary with Rich gradient styling.
Beautiful, colorful interactive selection prompts with smooth UX.
"""

from __future__ import annotations

import re
import sys
from enum import Enum
from pathlib import Path
from typing import Any, Callable, List, Optional, Union

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import questionary
from questionary import Choice, Separator, Style as QStyle, text

from rich import print as rprint
from rich.console import Console

from .output import (
    GRADIENT_PALETTES,
    _console,
    print_gradient,
    print_gradient_rule,
    print_gradient_box,
    print_gradient_title,
    print_centered_box,
    OutputFormatter,
)


class ValidationStatus(Enum):
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"


class ValidationResult:
    def __init__(self, status: ValidationStatus, message: str, hint: str = None):
        self.status = status
        self.message = message
        self.hint = hint
    
    def is_valid(self):
        return self.status == ValidationStatus.VALID


class Validators:
    @staticmethod
    def email(value: str) -> ValidationResult:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, value):
            return ValidationResult(ValidationStatus.VALID, "Valid email")
        return ValidationResult(ValidationStatus.INVALID, "Invalid email")
    
    @staticmethod
    def url(value: str) -> ValidationResult:
        pattern = r'^https?://[^\s]+$'
        if re.match(pattern, value):
            return ValidationResult(ValidationStatus.VALID, "Valid URL")
        return ValidationResult(ValidationStatus.INVALID, "Invalid URL")
    
    @staticmethod
    def path_exists(value: str) -> ValidationResult:
        if Path(value).exists():
            return ValidationResult(ValidationStatus.VALID, "Path exists")
        return ValidationResult(ValidationStatus.INVALID, "Path not found")
    
    @staticmethod
    def min_length(min_len: int) -> Callable:
        def validator(value: str) -> ValidationResult:
            if len(value) >= min_len:
                return ValidationResult(ValidationStatus.VALID, f"At least {min_len} chars")
            return ValidationResult(ValidationStatus.INVALID, f"Min {min_len} chars")
        return validator
    
    @staticmethod
    def max_length(max_len: int) -> Callable:
        def validator(value: str) -> ValidationResult:
            if len(value) <= max_len:
                return ValidationResult(ValidationStatus.VALID, f"At most {max_len} chars")
            return ValidationResult(ValidationStatus.INVALID, f"Max {max_len} chars")
        return validator
    
    @staticmethod
    def numeric_range(min_val: int, max_val: int) -> Callable:
        def validator(value: str) -> ValidationResult:
            try:
                num = int(value)
                if min_val <= num <= max_val:
                    return ValidationResult(ValidationStatus.VALID, f"In range")
                return ValidationResult(ValidationStatus.INVALID, f"Range: {min_val}-{max_val}")
            except ValueError:
                return ValidationResult(ValidationStatus.INVALID, "Not a number")
        return validator
    
    @staticmethod
    def not_empty(value: str) -> ValidationResult:
        if value and value.strip():
            return ValidationResult(ValidationStatus.VALID, "Value provided")
        return ValidationResult(ValidationStatus.INVALID, "Cannot be empty")
    
    @staticmethod
    def hostname(value: str) -> ValidationResult:
        pattern = r'^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$'
        if re.match(pattern, value) and len(value) <= 255:
            return ValidationResult(ValidationStatus.VALID, "Valid hostname")
        return ValidationResult(ValidationStatus.INVALID, "Invalid hostname")
    
    @staticmethod
    def port(value: str) -> ValidationResult:
        try:
            port = int(value)
            if 1 <= port <= 65535:
                return ValidationResult(ValidationStatus.VALID, f"Valid port {port}")
            return ValidationResult(ValidationStatus.INVALID, "Port 1-65535")
        except ValueError:
            return ValidationResult(ValidationStatus.INVALID, "Not a valid port")
    
    @staticmethod
    def ip_address(value: str) -> ValidationResult:
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, value):
            return ValidationResult(ValidationStatus.INVALID, "Invalid IP format")
        parts = value.split('.')
        if all(0 <= int(p) <= 255 for p in parts):
            return ValidationResult(ValidationStatus.VALID, "Valid IP address")
        return ValidationResult(ValidationStatus.INVALID, "Each octet 0-255")


class PromptTheme:
    THEMES = {
        "ocean": {
            "primary": "#4ECDC4", "secondary": "#44A08D", "accent": "#00FFFF",
            "highlight": "#00FF87", "pointer": "#FF6B6B", "selected": "#00FF87",
            "header": "#FF00FF", "success": "#00FF87", "warning": "#FFD700", "error": "#FF6B6B",
        },
        "sunset": {
            "primary": "#FF6B6B", "secondary": "#FF8E53", "accent": "#F9D423",
            "highlight": "#FFD700", "pointer": "#FF4500", "selected": "#FF6B6B",
            "header": "#FF00FF", "success": "#00FF87", "warning": "#FFD700", "error": "#FF6B6B",
        },
        "neon": {
            "primary": "#FF00FF", "secondary": "#00FFFF", "accent": "#FF00FF",
            "highlight": "#00FF87", "pointer": "#FFD700", "selected": "#00FFFF",
            "header": "#FF00FF", "success": "#00FF87", "warning": "#FFD700", "error": "#FF6B6B",
        },
        "cosmic": {
            "primary": "#7B4397", "secondary": "#DC2430", "accent": "#FDC830",
            "highlight": "#00FF87", "pointer": "#FF6B6B", "selected": "#7B4397",
            "header": "#DC2430", "success": "#00FF87", "warning": "#FFD700", "error": "#FF6B6B",
        },
        "fire": {
            "primary": "#FF4500", "secondary": "#FF8C00", "accent": "#FFD700",
            "highlight": "#FF6B6B", "pointer": "#FFD700", "selected": "#FF4500",
            "header": "#FF4500", "success": "#00FF87", "warning": "#FFD700", "error": "#FF6B6B",
        },
        "aurora": {
            "primary": "#00FF87", "secondary": "#60EFFF", "accent": "#00FFFF",
            "highlight": "#00FF87", "pointer": "#FF6B6B", "selected": "#00FF87",
            "header": "#60EFFF", "success": "#00FF87", "warning": "#FFD700", "error": "#FF6B6B",
        },
        "midnight": {
            "primary": "#6C5CE7", "secondary": "#A29BFE", "accent": "#74B9FF",
            "highlight": "#00CEC9", "pointer": "#FD79A8", "selected": "#6C5CE7",
            "header": "#A29BFE", "success": "#00B894", "warning": "#FDCB6E", "error": "#E17055",
        },
    }
    
    @classmethod
    def get_style(cls, theme: str = "ocean") -> list:
        colors = cls.THEMES.get(theme, cls.THEMES["ocean"])
        return [
            ("qmark", f"fg:{colors['primary']} bold"),
            ("question", f"fg:{colors['secondary']} bold"),
            ("answer", f"fg:{colors['accent']} bold"),
            ("pointer", f"fg:{colors['pointer']} bold"),
            ("highlighted", f"fg:{colors['highlight']} bold"),
            ("selected", f"fg:{colors['selected']}"),
            ("separator", f"fg:{colors['primary']}"),
            ("instruction", "fg:#888888"),
            ("header", f"fg:{colors['header']} bold"),
            ("footer", "fg:#666666 italic"),
        ]
    
    @classmethod
    def get_questionary_style(cls, theme: str = "ocean") -> QStyle:
        return QStyle(cls.get_style(theme))
    
    @classmethod
    def get_all_themes(cls) -> List[str]:
        return list(cls.THEMES.keys())


class InteractivePrompter:
    def __init__(self, theme: str = "ocean", use_colors: bool = True):
        self.theme = theme
        self.use_colors = use_colors and sys.stdout.isatty()
        self.formatter = OutputFormatter(use_colors=self.use_colors)
        self.colors = PromptTheme.THEMES.get(theme, PromptTheme.THEMES["ocean"])
    
    def _print_header(
            self, 
            text: str = "", 
            title: str = "◆ AgentXogs CLI Prompt",
            subtitle: str = None,
            padding: Optional[tuple[int, int]] = (1, 2)
    ) -> None:
        print_gradient_rule(palette=self.theme, width=_console.width - 4)
        print()
        print_centered_box(
            title=title,
            inline_text=text,
            subtitle=subtitle,
            palette=self.theme,
            box_style="rounded",
            padding=padding
        )
        print_gradient_rule(palette=self.theme, width=_console.width - 4)
        print()
    
    def _print_success(self, message: str) -> None:
        print_gradient(f"✓ {message}", palette="success")
    
    def _print_selection(self, selection: str, title: str) -> None:
        print_gradient(f"▶ Selected: {selection}", palette=self.theme)
    
    def _handle_cancellation(self, prompt_type: str = "prompt") -> None:
        print()
        print_gradient(f"◈ {prompt_type} cancelled", palette="warning")
    
    # SELECT PROMPT
    def select(
        self,
        message: str,
        title: str,
        subtitle: Optional[str] = None,
        padding: Optional[tuple[int, int]] = (1, 2),
        choices: List[Union[str, Choice]] = None,
        default: Optional[Union[str, int]] = None,
        instruction: str = "Use arrows to navigate, Enter to select",
        show_selected: bool = True,
        qmark: str = "◆",
        **kwargs,
    ) -> Any:
        self._print_header(
            text=f"{message.splitlines()[0] if message else ''} ◆\n{instruction if instruction else ''}", 
            title=title,
            subtitle=subtitle,
            padding=padding
        )
        
        styled_choices = []
        for choice in choices:
            if isinstance(choice, str):
                styled_choices.append(Choice(choice, value=choice, disabled=False))
            else:
                styled_choices.append(choice)
        
        try:
            result = questionary.select(
                message=message,
                choices=styled_choices,
                default=default,
                style=PromptTheme.get_questionary_style(self.theme),
                qmark=qmark,
                use_shortcuts=True,
                use_arrow_keys=True,
                **kwargs,
            ).ask()
            
            if result is not None and show_selected:
                self._print_selection(str(result), message)
            
            return result
            
        except KeyboardInterrupt:
            self._handle_cancellation("Selection")
            return None
        except EOFError:
            return None
    
    def select_menu(
        self,
        title: str,
        options: List[dict],
        inline_text: str = "Navigate with Arrow Keys | Enter to Select | ESC to Quit",
        subtitle: Optional[str] = None,
        padding: Optional[tuple[int, int]] = (1, 2),
    ) -> Optional[str]:
        self._print_header(
            text=inline_text,
            title=title, 
            subtitle=subtitle,
            padding=padding
        )
        
        choices = []
        for opt in options:
            if opt.get("separator"):
                choices.append(Separator(opt["title"]))
            else:
                choice = Choice(
                    title=opt.get("title", opt["id"]),
                    value=opt["id"],
                    disabled=opt.get("disabled", False),
                )
                choices.append(choice)
        
        try:
            return questionary.select(
                message=f"{title}:",
                choices=choices,
                style=PromptTheme.get_questionary_style(self.theme),
                qmark="◆",
                pointer="▶",
            ).ask()
            
        except (KeyboardInterrupt, EOFError):
            self._handle_cancellation("Menu navigation")
            return None
    
    # CONFIRM PROMPT
    def confirm(
        self,
        message: str,
        title: str = "◆ Confirmation Required",
        subtitle: Optional[str] = None,
        padding: Optional[tuple[int, int]] = (1, 2),
        default: bool = True,
        instruction: str = "Press Y for Yes, N for No, Enter to confirm",
        **kwargs,
    ) -> Optional[bool]:
        self._print_header(
            text=f"{message.splitlines()[0] if message else ''} ◆\n{instruction if instruction else ''}", 
            title=title,
            subtitle=subtitle,
            padding=padding
        )
        
        try:
            result = questionary.confirm(
                message=message,
                default=default,
                style=PromptTheme.get_questionary_style(self.theme),
                qmark="◆",
                **kwargs,
            ).ask()
            
            if result is not None:
                status = "✓ CONFIRMED" if result else "✗ CANCELLED"
                status_palette = "success" if result else "error"
                print_gradient(status, palette=status_palette)
            
            return result
            
        except (KeyboardInterrupt, EOFError):
            self._handle_cancellation("Confirmation")
            return None
    
    def confirm_action(
        self,
        action: str,
        item: str = "",
        default: bool = False,
    ) -> bool:
        message = f"◆ {action}" + (f" {item}" if item else "") + "?"
        subtitle = f"Press Y to {action.lower()}, N to cancel"
        return self.confirm(message, default=default, instruction=subtitle) or False
    
    # TEXT INPUT PROMPT
    def text(
        self,
        message: str,
        title: str = "◆ Input Required",
        subtitle: Optional[str] = None,
        padding: Optional[tuple[int, int]] = (1, 2),
        default: str = "",
        instruction: str = "Type your input and press Enter",
        validate: Optional[Callable] = None,
        **kwargs,
    ) -> Optional[str]:
        self._print_header(
            text=f"{message.splitlines()[0] if message else ''} ◆\n{instruction if instruction else ''}", 
            title=title, 
            subtitle=subtitle,
            padding=padding
        )
        
        try:
            result = questionary.text(
                message=message,
                default=default,
                style=PromptTheme.get_questionary_style(self.theme),
                qmark="◆",
                validate=validate,
                **kwargs,
            ).ask()
            
            if result:
                print_gradient(f"▶ Input: {result}", palette=self.theme)
            
            return result
            
        except (KeyboardInterrupt, EOFError):
            self._handle_cancellation("Input")
            return None
    
    def path(
        self,
        message: str,
        title: str = "◆ Path Input Required",
        subtitle: Optional[str] = None,
        padding: Optional[tuple[int, int]] = (1, 2),
        default: str = "",
        instruction: str = "Enter a valid path",
        validate: Optional[Callable] = None,
        **kwargs,
    ) -> Optional[str]:
        self._print_header(
            text=f"{message.splitlines()[0] if message else ''} ◆\n{instruction if instruction else ''}", 
            title=title,
            subtitle=subtitle,
            padding=padding
        )
        
        try:
            result = questionary.path(
                message=message,
                default=default,
                style=PromptTheme.get_questionary_style(self.theme),
                qmark="◆",
                validate=validate,
                **kwargs,
            ).ask()
            
            if result:
                print_gradient(f"▶ Path: {result}", palette=self.theme)
            
            return result
            
        except (KeyboardInterrupt, EOFError):
            self._handle_cancellation("Path input")
            return None
    
    # PASSWORD PROMPT
    def password(
        self,
        message: str,
        title: str = "◆ Password Required",
        subtitle: Optional[str] = None,
        padding: Optional[tuple[int, int]] = (1, 2),
        instruction: str = "Enter your password (hidden)",
        **kwargs,
    ) -> Optional[str]:
        self._print_header(
            text=f"{message.splitlines()[0] if message else ''} ◆\n{instruction if instruction else ''}",
            title=title,
            subtitle=subtitle,
            padding=padding
        )
        
        try:
            result = questionary.password(
                message=message,
                style=PromptTheme.get_questionary_style(self.theme),
                qmark="◆",
                **kwargs,
            ).ask()
            
            if result:
                print_gradient("▶ Password entered (hidden)", palette="success")
            
            return result
            
        except (KeyboardInterrupt, EOFError):
            self._handle_cancellation("Password input")
            return None
    
    # CHECKBOX PROMPT
    def checkbox(
        self,
        message: str,
        title: str,
        subtitle: Optional[str] = None,
        padding: Optional[tuple[int, int]] = (1, 2),
        choices: List[Union[str, Choice]] = None,
        default: Optional[List[str]] = None,
        instruction: str = "Use Space to select, Enter to confirm",
        **kwargs,
    ) -> Optional[List[str]]:
        self._print_header(
            text=f"{message.splitlines()[0] if message else ''} ◆\n{instruction if instruction else ''}",
            title=title,
            subtitle=subtitle,
            padding=padding
        )
        
        styled_choices = []
        for choice in choices:
            if isinstance(choice, str):
                styled_choices.append(Choice(choice, value=choice))
            else:
                styled_choices.append(choice)
        
        try:
            result = questionary.checkbox(
                message=message,
                choices=styled_choices,
                default=default,
                style=PromptTheme.get_questionary_style(self.theme),
                qmark="◆",
                **kwargs,
            ).ask()
            
            if result is not None:
                count = len(result)
                print_gradient(f"▶ Selected {count} option(s): {', '.join(result)}", palette=self.theme)
            
            return result
            
        except (KeyboardInterrupt, EOFError):
            self._handle_cancellation("Selection")
            return None
    
    def select_multiple(
        self,
        title: str,
        subtitle: Optional[str] = None,
        padding: Optional[tuple[int, int]] = (1, 2),
        options: List[str] = None,
        instruction: str = "Select multiple options with Space",
    ) -> Optional[List[str]]:
        self._print_header(
            text=instruction, 
            title=title,
            subtitle=subtitle,
            padding=padding
        )
        
        choices = [Choice(opt, value=opt) for opt in options]
        
        try:
            return questionary.checkbox(
                message=f"{title}:",
                choices=choices,
                style=PromptTheme.get_questionary_style(self.theme),
                qmark="◆",
            ).ask()
            
        except (KeyboardInterrupt, EOFError):
            self._handle_cancellation("Multi-select")
            return None
    
    # NUMBER PROMPT
    def number(
        self,
        message: str,
        title: str = "◆ Number Input Required",
        subtitle: Optional[str] = None,
        padding: Optional[tuple[int, int]] = (1, 2),
        default: int = 0,
        minimum: Optional[int] = None,
        maximum: Optional[int] = None,
        instruction: str = "Enter a number",
        **kwargs,
    ) -> Optional[int]:
        """Create a styled number input prompt."""
        self._print_header(
            text=f"{message.splitlines()[0] if message else ''} ◆\n{instruction if instruction else ''}", 
            title=title,
            subtitle=subtitle,
            padding=padding
        )
        
        def validate_number(value: str) -> bool:
            try:
                num = int(value)
                if minimum is not None and num < minimum:
                    return False
                if maximum is not None and num > maximum:
                    return False
                return True
            except ValueError:
                return False
        
        try:
            result = questionary.text(
                message=message,
                default=str(default),
                style=PromptTheme.get_questionary_style(self.theme),
                qmark="◆",
                validate=validate_number,
                **kwargs,
            ).ask()
            
            if result:
                num_result = int(result)
                print_gradient(f"▶ Number: {num_result}", palette=self.theme)
                return num_result
            
            return None
            
        except (KeyboardInterrupt, EOFError):
            self._handle_cancellation("Number input")
            return None
    
    # CONVENIENCE FUNCTIONS
    def ask_choice(
        self,
        question: str,
        title: str,
        subtitle: Optional[str] = None,
        padding: Optional[tuple[int, int]] = (1, 2),
        options: List[str] = None,
        default: Optional[str] = None,
    ) -> Optional[str]:
        """Quick single choice selection."""
        return self.select(
            title=title,
            subtitle=subtitle,
            padding=padding,
            message=question,
            choices=options,
            default=default if default in options else None,
            instruction="Use arrows, Enter to select",
        )
    
    def ask_yes_no(
        self,
        question: str,
        default: bool = True,
    ) -> Optional[bool]:
        """Quick yes/no confirmation."""
        return self.confirm(
            message=question,
            default=default,
            instruction="Y for Yes, N for No",
        )
    
    def ask_text(
        self,
        question: str,
        default: str = "",
        required: bool = False,
    ) -> Optional[str]:
        """Quick text input."""
        validate = None if not required else Validators.not_empty
        return self.text(
            message=question,
            default=default,
            instruction="Type and press Enter",
            validate=validate,
        )


# Convenience function
def create_prompter(theme: str = "ocean", use_colors: bool = True) -> InteractivePrompter:
    """Create a new InteractivePrompter instance."""
    return InteractivePrompter(theme=theme, use_colors=use_colors)
       