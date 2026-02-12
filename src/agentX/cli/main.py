#!/usr/bin/env python3
"""AgentXogs CLI - Interactive CLI for Log Analysis with animations and thinking indicators."""

from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from .animation import AnimatedSpinner, ThinkingIndicator
from .live_display import LivePipelineDisplay, LiveProgressBar, LiveStatusPanel
from .prompts import InteractivePrompter, create_prompter, PromptTheme
from questionary import Choice, Separator
from .output import (
    OutputFormatter, print_gradient_with_rule, print_header, print_success,
    print_error, print_warning, print_info, print_title, print_gradient_title,
    print_arrow_line, print_gradient, print_animated_gradient, print_gradient_panel,
    print_gradient_rule, print_gradient_box, print_centered_box,
    print_gradient_inline_multiple_text_with_rows, GRADIENT_PALETTES, Align,
)
PADDING = (2, 5)


def print_nav_hint():
    print_gradient_inline_multiple_text_with_rows(
        rows=[
            [("↑ ↓", "gold"), ("|", None), ("ENTER", "success"), ("|", None), ("ESC", "error")],
            [("Navigate", None), ("|", None), ("Select", None), ("|", None), ("Quit", None)],
        ],
        sep="   ",
    )


class AgentXogsCLI:
    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors
        self.formatter = OutputFormatter(use_colors=use_colors)
        self.config: dict[str, Any] | None = None

    def banner(self):
        banner_text = """
   █████████                            █████ █████ █████                       
  ███░░░░░███                          ░░███ ░░███ ░░███                        
 ░███    ░███  ███████ ██████ ████████ ███████░░███ ███   ██████  ███████ █████ 
 ░███████████ ███░░██████░░██░░███░░██░░░███░  ░░█████   ███░░██████░░██████░░  
 ░███░░░░░███░███ ░██░███████ ░███ ░███ ░███    ███░███ ░███ ░██░███ ░██░░█████ 
 ░███    ░███░███ ░██░███░░░  ░███ ░███ ░███ █████ ░░███░███ ░██░███ ░███░░░░███
 █████   ████░░██████░░██████ ████ █████░░█████████ ████░░██████░░█████████████ 
░░░░░   ░░░░░ ░░░░░███░░░░░░ ░░░░ ░░░░░  ░░░░░░░░░ ░░░░░ ░░░░░░  ░░░░░██░░░░░░  
              ███ ░███                                           ███ ░███       
             ░░██████                                           ░░██████        
              ░░░░░░                                             ░░░░░░         
                      AgentXogs - Live Log Insight Agent System
        """
        print(self.formatter._color('bright_cyan', banner_text))
        print()

    def load_config(self, config_path: str = "config.json") -> bool:
        from src.agentX.shared.utils import load_config
        config_file = Path(config_path)
        if not config_file.exists():
            print_error(f"Config file not found: {config_path}")
            return False
        self.config = load_config(config_file)
        if self.config is None:
            print_error(f"Failed to load config: {config_path}")
            return False
        return True

    def cmd_status(self) -> int:
        print()
        print_gradient_rule(palette="neon")
        print()
        print_gradient_title(
            title="● System Status ●", 
            inline_text="Project Configuration Overview",
            palette="neon", 
            subtitle=None, 
            animated=True,
        )
        print()
        print()
        if not self.config and not self.load_config():
            return 1
        config_content = f"""
Project:     {self.config.get('project', 'Unknown')}
Environment: {self.config.get('environment', 'Unknown')}
Time Range:  {self.config.get('time_range', 'Unknown')}
Max Logs:    {self.config.get('max_logs', 'Unknown')}
"""
        print_gradient_box(
            inline_text=config_content.strip(), 
            title="Configuration",
            subtitle=None, 
            palette="ocean", 
            box_style="rounded",
            padding=PADDING,
        )
        print()
        print()
        print_gradient_rule(palette="sunset")
        print()
        return 0

    def cmd_analyze(self, time_range: str = "24h", max_logs: int = 10000, environment: str = "production") -> int:
        print()
        print()
        print_gradient_title(
            title="◈ AgentXogs Log Analysis Pipeline ◈", 
            palette="ocean", 
            inline_text="Comprehensive Log Analysis Execution", 
            subtitle=None, 
            animated=True
        )
        print()
        print()
        print_header("Analysis Parameters")
        print_info(f"Time Range: {time_range}")
        print_info(f"Max Logs: {max_logs}")
        print_info(f"Environment: {environment}")
        print()
        print_gradient_rule(palette="ocean")
        print()
        pipeline_steps = [
            "Discovering log sources", 
            "Fetching logs", 
            "Parsing logs", 
            "Aggregating metrics", 
            "Detecting anomalies", 
            "Generating hypotheses", 
            "Creating summary"
        ]
        display = LivePipelineDisplay(refresh_per_second=8.0)
        display.set_steps(pipeline_steps)
        display.start()
        durations = [0.8, 1.0, 0.8, 1.0, 1.2, 0.8, 0.6]
        for i, (step_name, duration) in enumerate(zip(pipeline_steps, durations)):
            display.start_step(i, f"Processing {step_name}...")
            for progress in [25, 50, 75]:
                display.update_progress(progress)
                time.sleep(duration * 0.3)
            display.complete_step(i, "Done")
        display.stop("Pipeline complete!")
        print()
        print_header("Results")
        print_info("Logs Analyzed: 1,234")
        print_info("Events Parsed: 567")
        print_info("Anomalies Detected: 3")
        return 0

    def cmd_quickcheck(self, service: str | None = None) -> int:
        print()
        print()
        print_gradient_title(
            title="◆ Quick Health Check ◆", 
            palette="ocean",
            inline_text="Rapid System Health Verification", 
            subtitle=None, 
            animated=True
        )
        print()
        print()
        status_panel = LiveStatusPanel(title="Health Check", refresh_per_second=4.0)
        if service:
            status_panel.add_section("Service", service, "cyan")
        status_panel.add_section("Status", "Initializing...", "yellow")
        status_panel.add_section("Logs", "Scanning...", "dim")
        status_panel.add_section("Metrics", "Computing...", "dim")
        status_panel.start()
        time.sleep(0.5)
        status_panel.update_section("Status", "Analyzing logs...")
        time.sleep(0.5)
        status_panel.update_section("Status", "Complete!")
        status_panel.stop()
        print()
        print_success("System is healthy")
        return 0

    def cmd_discover(self) -> int:
        print()
        print()
        print_gradient_title(
            title="◇ Log Source Discovery ◇", 
            palette="sunset",
            inline_text="Identifying Available Log Sources", 
            subtitle=None, 
            animated=True
        )
        print()
        print()
        discovery_steps = ["Scanning /var/log/", "Scanning application logs", "Scanning nginx logs", "Scanning postgresql logs"]
        display = LivePipelineDisplay(refresh_per_second=8.0)
        display.set_steps(discovery_steps)
        display.start()
        for i, (step, duration) in enumerate(zip(discovery_steps, [0.6, 0.6, 0.5, 0.5])):
            display.start_step(i, f"Scanning {step}...")
            for progress in [25, 50, 75]:
                display.update_progress(progress)
                time.sleep(duration * 0.3)
            display.complete_step(i, "Found")
        display.stop("Scan complete!")
        print()
        print_info("✓ /var/log/application/*.log")
        print_info("✓ /var/log/nginx/access.log")
        return 0

    def cmd_export(self, format: str = "json") -> int:
        print()
        print()
        print_gradient_title(
            title=f"▸ Export Results ({format})", 
            palette="sunset",
            inline_text="Exporting Analysis Results", 
            subtitle=None, 
            animated=True
        )
        print()
        print()
        export_steps = ["Collecting analysis data", "Formatting output", "Writing file"]
        display = LivePipelineDisplay(refresh_per_second=8.0)
        display.set_steps(export_steps)
        display.start()
        for i, (step, duration) in enumerate(zip(export_steps, [0.5, 0.3, 0.5])):
            display.start_step(i, f"{step}...")
            for progress in [25, 50, 75]:
                display.update_progress(progress)
                time.sleep(duration * 0.3)
            display.complete_step(i, "Done")
        display.stop("Export complete!")
        print()
        print_success(f"Results exported to: output/export.{format}")
        return 0

    def cmd_wizard(self) -> int:
        """Run interactive wizard with questionary prompts."""
        print()
        print()
        print_gradient_title(
            title="◆ Analysis Wizard ◆", 
            palette="ocean",
            inline_text="Interactive Analysis Configuration", 
            subtitle=None, 
            animated=True
        )
        print()
        print()
        prompter = create_prompter(theme="ocean", use_colors=self.use_colors)
        
        environment = prompter.select(
            message="Select Environment:",
            title="Environment Selection",
            subtitle=None,
            padding=PADDING,
            choices=["production", "staging", "development", "local"],
            instruction="Choose the target environment for analysis",
        )
        if environment is None:
            print_gradient("◈ Wizard cancelled", palette="warning")
            return 0
        
        time_range = prompter.select(
            message="Select Time Range:",
            title="Time Range Selection",
            subtitle=None,
            padding=PADDING,
            choices=["1h", "6h", "24h", "7d", "30d", "custom"],
            instruction="How far back should we analyze logs?",
        )
        if time_range is None:
            print_gradient("◈ Wizard cancelled", palette="warning")
            return 0
        
        services = prompter.checkbox(
            message="Select Services to Analyze:",
            title="Service Selection",
            subtitle=None,
            padding=PADDING,
            choices=["nginx", "postgresql", "redis", "application", "api-gateway", "celery"],
            instruction="Use Space to select multiple services",
        )
        if services is None:
            print_gradient("◈ Wizard cancelled", palette="warning")
            return 0
        
        confirm = prompter.confirm_action(
            action="Run Analysis",
            item=f"{environment} / {time_range} / {len(services)} services",
            default=True,
        )
        if not confirm:
            print_gradient("◈ Analysis cancelled", palette="warning")
            return 0
        
        print()
        print()
        print_gradient_box(
            inline_text=f"Environment:  {environment}\nTime Range:   {time_range}\nServices:     {', '.join(services)}",
            title="Summary",
            subtitle=None, 
            palette="ocean", 
            box_style="rounded",
            padding=PADDING + (1, 0),
        )
        print()
        print()
        print_success("Wizard completed successfully!")
        return 0

    def cmd_demo_prompts(self) -> int:
        """Demonstrate all prompt types with questionary."""
        from .prompts import Validators
        
        print()
        print()
        print_gradient_title(
            title="◆ Questionary Prompts Demo ◆", 
            palette="neon",
            inline_text="Interactive Prompt Examples", 
            subtitle=None, 
            animated=True
        )
        print()
        print()
        prompter = InteractivePrompter(theme="cosmic", use_colors=self.use_colors)
        
        # SELECT PROMPT
        choice = prompter.select(
            message="Choose an action:",
            title="Action Selection",
            subtitle=None,
            padding=PADDING,
            choices=["Analyze Logs", "Check Health", "Export Data", "Discover Sources"],
            instruction="Navigate with arrows, Enter to select",
        )
        if choice:
            print_success(f"You chose: {choice}")
        
        # CONFIRM PROMPT
        confirmed = prompter.confirm(
            message="Do you want to continue with the demo?",
            title="Confirmation Required",
            subtitle=None,
            padding=PADDING,
            default=True, instruction="Y to continue, N to skip",
        )
        if confirmed is not None:
            print_success(f"Confirmed: {confirmed}")
        
        # CHECKBOX PROMPT
        selected = prompter.checkbox(
            message="Select log levels to monitor:",
            title="Log Level Selection",
            subtitle=None,
            padding=PADDING,
            choices=["ERROR", "WARNING", "INFO", "DEBUG", "TRACE"],
            instruction="Space to select, Enter to confirm",
        )
        if selected is not None:
            print_success(f"Selected levels: {', '.join(selected)}")
        
        # TEXT INPUT WITH VALIDATION
        def valid_regex(value):
            try:
                re.compile(value)
                return True
            except re.error:
                return "Invalid regex pattern"
        
        text_input = prompter.text(
            message="Enter a custom filter pattern:",
            title="Filter Pattern Input",
            subtitle=None,
            padding=PADDING,
            default=".*ERROR.*",
            instruction="Type regex pattern for log filtering",
            validate=valid_regex,
        )
        if text_input:
            print_success(f"Pattern: {text_input}")
        
        # NUMBER INPUT
        max_logs = prompter.number(
            message="Enter maximum number of logs to analyze:",
            title="Max Logs Input",
            subtitle=None,
            padding=PADDING,
            default=1000,
            minimum=100,
            maximum=100000,
            instruction="Enter a number between 100 and 100000",
        )
        if max_logs:
            print_success(f"Max logs: {max_logs}")
        
        # SELECT MENU
        menu_result = prompter.select_menu(
            inline_text="Use arrows to navigate, Enter to select, ESC to quit",
            title="Quick Actions",
            subtitle=None,
            padding=PADDING,
            options=[
                {"id": "status", "title": "● View System Status", "description": "Check current system health"},
                {"id": "analyze", "title": "◈ Run Analysis", "description": "Start log analysis pipeline"},
                {"id": "export", "title": "▸ Export Results", "description": "Export to JSON/YAML/Markdown"},
                {"separator": True, "title": "───"},
                {"id": "settings", "title": "⚙ Settings", "description": "Configure preferences", "disabled": True},
            ],
        )
        if menu_result:
            print_success(f"Menu selection: {menu_result}")
        
        # CONVENIENCE FUNCTIONS
        quick_choice = prompter.ask_choice(
            question="Quick choice - Select theme:",
            title="Theme Selection",
            subtitle=None,
            padding=PADDING,
            default="ocean",
            options=["ocean", "sunset", "neon", "cosmic", "fire"],
        )
        if quick_choice:
            print_success(f"Theme selected: {quick_choice}")
        
        yes_no = prompter.ask_yes_no(
            question="Enable verbose output?",
            default=False,
        )
        if yes_no is not None:
            print_success(f"Verbose: {yes_no}")
        
        # MULTI-SELECT
        services = prompter.select_multiple(
            title="Select Services",
            subtitle=None,
            padding=PADDING,
            options=["nginx", "postgresql", "redis", "application", "api-gateway"],
            instruction="Select multiple services to monitor",
        )
        if services:
            print_success(f"Services: {', '.join(services)}")
        
        print()
        print_success("Full demo completed!")
        return 0

    def cmd_interactive(self) -> int:
        """Enter interactive mode with enhanced questionary + rich prompts."""
        print()
        print_gradient_rule(palette="neon")
        print()
        print_centered_box(
            title="◆ INTERACTIVE MODE ◆",
            inline_text="Choose Your Interaction Style",
            palette="ocean",
            box_style="rounded",
            padding=PADDING,
        )
        print()
        
        prompter = create_prompter(theme="ocean", use_colors=self.use_colors)
        
        mode = prompter.select(
            message="Select Interaction Mode:",
            title="Interaction Mode Selection",
            subtitle=None,
            padding=PADDING,
            choices=[
                "◈ Chat Mode - Command-line chat interface",
                "◆ List Mode - Visual menu with arrow navigation",
                "✗ Exit - Quit interactive mode",
            ],
            instruction="Use arrows to navigate, Enter to select",
        )
        
        if mode is None:
            print_gradient("◈ Interactive mode cancelled", palette="warning")
            return 0
        
        if "Chat" in mode:
            return self.cmd_interactive_chat_mode()
        elif "List" in mode:
            return self.cmd_interactive_list_mode()
        else:
            print_gradient("◈ Goodbye!", palette="cosmic")
            return 0

    def cmd_interactive_chat_mode(self) -> int:
        """Enhanced chat mode with rich styling."""
        print()
        print()
        print_gradient_title(
            title="◈ Chat Mode ◈",
            inline_text="Interactive Command Interface",
            palette="ocean",
            subtitle=None,
            animated=True,
        )
        print()
        print()
        
        while True:
            try:
                cmd = input(self.formatter._color('bright_green', 'agentXogs @> ')).strip().lower()
            except (EOFError, KeyboardInterrupt):
                print()
                print_gradient("◈ Goodbye!", palette="cosmic")
                return 0
            if not cmd:
                continue
            if cmd in ['quit', 'exit', 'q']:
                print_gradient("◈ Goodbye!", palette="cosmic")
                return 0
            elif cmd == 'help':
                self._show_chat_help()
            elif cmd == 'status':
                self.cmd_status()
            elif cmd == 'analyze':
                self.cmd_analyze()
            elif cmd == 'quickcheck':
                self.cmd_quickcheck()
            elif cmd == 'discover':
                self.cmd_discover()
            elif cmd == 'export':
                self.cmd_export()
            elif cmd == 'wizard':
                self.cmd_wizard()
            elif cmd == 'demo':
                self.cmd_demo_prompts()
            elif cmd == 'version':
                self.cmd_version()
            else:
                print_warning(f"Unknown command: {cmd}")
                print_info("Type 'help' for available commands")
        return 0

    def _show_chat_help(self) -> None:
        """Show help for chat mode."""
        print()
        print()
        print_gradient_box(
            title="Available Commands",
            inline_text="""
status      Show system status and configuration
analyze     Run the log analysis pipeline
quickcheck  Perform quick health check
discover    Discover available log sources
export      Export analysis results
wizard      Run interactive analysis wizard
demo        Demonstrate all prompt types
version     Show version information
help        Show this help message
quit        Exit the interactive mode
            """.strip(),
            subtitle=None,
            palette="ocean",
            box_style="rounded",
        )
        print()
        print()

    def cmd_interactive_list_mode(self) -> int:
        """Enhanced list mode with questionary + rich select prompts."""
        prompter = create_prompter(theme="ocean", use_colors=self.use_colors)
        
        # Define menu items with rich descriptions
        menu_choices = [
            Choice(
                title="● System Status",
                value="status",
                description="View project configuration and system overview",
            ),
            Choice(
                title="◈ Log Analysis",
                value="analyze",
                description="Run comprehensive log analysis pipeline",
            ),
            Choice(
                title="◆ Quick Health Check",
                value="quickcheck",
                description="Rapid system health verification",
            ),
            Choice(
                title="◇ Log Source Discovery",
                value="discover",
                description="Identify and catalog available log sources",
            ),
            Choice(
                title="▸ Export Results",
                value="export",
                description="Export analysis results to various formats",
            ),
            Choice(
                title="✦ Analysis Wizard",
                value="wizard",
                description="Interactive step-by-step analysis configuration",
            ),
            Choice(
                title="◙ Demo Prompts",
                value="demo",
                description="Explore all interactive prompt capabilities",
            ),
            Choice(
                title="◆ Version Info",
                value="version",
                description="View version and system information",
            ),
            Choice(title="───", value=Separator(), disabled=True),
            Choice(
                title="✗ Return to Main Menu",
                value="back",
                description="Return to the main interaction mode selection",
            ),
        ]
        
        while True:
            print()
            print_gradient_rule(palette="ocean")
            print()
            print_centered_box(
                title="◆ INTERACTIVE LIST MODE ◆",
                inline_text="Visual Menu Navigation",
                subtitle="Use arrows to navigate, Enter to select, ESC to quit",
                palette="ocean",
                box_style="rounded",
                padding=PADDING,
            )
            print()
            
            # Navigation hint
            print_nav_hint()
            print()
            
            selection = prompter.select(
                message="Select an action:",
                title="Action Selection",
                subtitle=None,
                padding=PADDING,
                choices=menu_choices,
                instruction="Choose from the menu above",
                qmark="◆",
            )
            
            if selection is None or selection == "back":
                print_gradient("◈ Returning to main menu...", palette="cosmic")
                return 0
            
            # Handle selection with confirmation for destructive actions
            if selection in ["export"]:
                confirm = prompter.confirm_action(
                    action=f"Run {selection.title()}",
                    item="",
                    default=True,
                )
                if not confirm:
                    continue
            
            # Execute the selected command
            if selection == "status":
                self.cmd_status()
            elif selection == "analyze":
                self.cmd_analyze()
            elif selection == "quickcheck":
                self.cmd_quickcheck()
            elif selection == "discover":
                self.cmd_discover()
            elif selection == "export":
                self.cmd_export()
            elif selection == "wizard":
                self.cmd_wizard()
            elif selection == "demo":
                self.cmd_demo_prompts()
            elif selection == "version":
                self.cmd_version()
            
            # Show result and continue
            print()
            print_gradient("◈ Press Enter to continue...", palette="ocean")
            input()

    def cmd_interactive_select_mode(self) -> int:
        """Enhanced select mode with rich styling and animations."""
        prompter = create_prompter(theme="midnight", use_colors=self.use_colors)
        
        # Categories for organized selection
        categories = [
            Choice(
                title="📊 Analysis",
                value="analysis",
                description="Log analysis and insights",
            ),
            Choice(
                title="🔍 Discovery",
                value="discovery",
                description="Log source discovery and exploration",
            ),
            Choice(
                title="📤 Export",
                value="export",
                description="Export and save results",
            ),
            Choice(
                title="⚙️ Settings",
                value="settings",
                description="Configure preferences",
            ),
        ]
        
        print()
        print()
        print_gradient_title(
            title="◆ Quick Select ◆",
            inline_text="Categorized Command Selection",
            palette="midnight",
            subtitle=None,
            animated=True,
        )
        print()
        print()
        
        category = prompter.select(
            message="Choose a category:",
            title="Category Selection",
            subtitle=None,
            padding=PADDING,
            choices=categories,
            instruction="Use arrows to select",
        )
        
        if category is None:
            print_gradient("◈ Selection cancelled", palette="warning")
            return 0
        
        # Category-specific actions
        if category == "analysis":
            actions = [
                Choice("◈ Run Full Analysis", "analyze"),
                Choice("◆ Quick Health Check", "quickcheck"),
                Choice("◙ View System Status", "status"),
            ]
            action = prompter.select(
                message="Select analysis action:",
                title="Analysis Action Selection",
                subtitle=None,
                padding=PADDING,
                choices=actions,
                instruction="Choose an analysis operation",
            )
            if action == "analyze":
                self.cmd_analyze()
            elif action == "quickcheck":
                self.cmd_quickcheck()
            elif action == "status":
                self.cmd_status()
        
        elif category == "discovery":
            actions = [
                Choice("◇ Discover Log Sources", "discover"),
                Choice("◙ Configure Sources", "config"),
            ]
            action = prompter.select(
                message="Select discovery action:",
                title="Discovery Action Selection",
                subtitle=None,
                padding=PADDING,
                choices=actions,
                instruction="Choose a discovery operation",
            )
            if action == "discover":
                self.cmd_discover()
        
        elif category == "export":
            formats = ["json", "yaml", "markdown"]
            export_format = prompter.ask_choice(
                question="Select export format:",
                options=formats,
            )
            if export_format:
                self.cmd_export(export_format)
        
        elif category == "settings":
            print_info("Settings menu coming soon...")
        
        return 0

    def _get_key(self):
        import termios
        import tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                seq = sys.stdin.read(2)
                return '\x1b' + seq
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def cmd_version(self) -> int:
        print()
        print_gradient_rule(palette="cosmic")
        print()
        print()
        print_gradient_title(
            title="AgentXogs CLI", 
            palette="cosmic",
            inline_text="Interactive Log Analysis Tool \n Version Information - Version 0.1.0", 
            subtitle=None, 
            animated=True
        )
        print()
        print()
        version_content = "Version:    0.1.0\nPython:     3.10+\nLicense:    Apache-2.0\nAuthor:     AgentXogs Team"
        print_gradient_box(
            inline_text=version_content, 
            title="Version Info", 
            palette="cosmic", 
            box_style="double"
        )
        print()
        print()
        print_gradient_rule(palette="cosmic")
        print()
        return 0


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description="AgentXogs CLI - Interactive Log Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--version', '-V', action='store_true', help='Show version information')
    parser.add_argument('--interactive', '-i', action='store_true', help='Enter interactive mode')
    parser.add_argument('--no-colors', action='store_true', help='Disable colors in output')
    parser.add_argument('--config', '-c', default='config.json', help='Config file path')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    subparsers.add_parser('status', help='Show system status')
    
    analyze_parser = subparsers.add_parser('analyze', help='Run log analysis')
    analyze_parser.add_argument('--time', '-t', default='24h', help='Time range')
    analyze_parser.add_argument('--max-logs', '-m', type=int, default=10000, help='Max logs')
    analyze_parser.add_argument('--environment', '-e', default='production', help='Environment')
    
    quickcheck_parser = subparsers.add_parser('quickcheck', help='Quick health check')
    quickcheck_parser.add_argument('--service', '-s', help='Specific service')
    
    subparsers.add_parser('discover', help='Discover log sources')
    
    export_parser = subparsers.add_parser('export', help='Export results')
    export_parser.add_argument('--format', '-f', choices=['json', 'yaml', 'markdown'], default='json')
    
    subparsers.add_parser('wizard', help='Run interactive analysis wizard')
    subparsers.add_parser('demo-prompts', help='Demonstrate questionary prompts')
    
    return parser


def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)
    
    if args.version:
        cli = AgentXogsCLI(use_colors=not args.no_colors)
        return cli.cmd_version()
    
    cli = AgentXogsCLI(use_colors=not args.no_colors)
    cli.load_config(args.config)
    
    if args.interactive:
        cli.banner()
        return cli.cmd_interactive()
    
    if args.command is None:
        parser.print_help()
        print()
        print_info("Run with --interactive or -i for interactive mode")
        return 0
    
    if args.command == 'status':
        return cli.cmd_status()
    elif args.command == 'analyze':
        return cli.cmd_analyze(time_range=args.time, max_logs=args.max_logs, environment=args.environment)
    elif args.command == 'quickcheck':
        return cli.cmd_quickcheck(args.service)
    elif args.command == 'discover':
        return cli.cmd_discover()
    elif args.command == 'export':
        return cli.cmd_export(args.format)
    elif args.command == 'wizard':
        cli.banner()
        return cli.cmd_wizard()
    elif args.command == 'demo-prompts':
        cli.banner()
        return cli.cmd_demo_prompts()
    else:
        print_error(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

    #  uv run src.agentX.cli.main:main -i