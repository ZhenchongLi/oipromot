"""
Base CLI class for common functionality.
"""

from abc import ABC, abstractmethod
from ..core.logging import get_logger


class BaseCLI(ABC):
    """Base class for CLI interfaces."""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    @abstractmethod
    def run(self) -> None:
        """Run the CLI interface."""
        pass
    
    def display_welcome(self, title: str, description: str) -> None:
        """Display welcome message."""
        print(f"\n{'='*50}")
        print(f"  {title}")
        print(f"{'='*50}")
        print(f"{description}\n")
    
    def display_error(self, message: str) -> None:
        """Display error message."""
        print(f"❌ Error: {message}")
        self.logger.error(message)
    
    def display_success(self, message: str) -> None:
        """Display success message."""
        print(f"✅ {message}")
        self.logger.info(message)
    
    def display_info(self, message: str) -> None:
        """Display info message."""
        print(f"ℹ️  {message}")
        self.logger.info(message)
    
    def get_user_input(self, prompt: str) -> str:
        """Get user input with proper error handling."""
        try:
            return input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            raise KeyboardInterrupt("User interrupted input")
    
    def confirm_action(self, message: str) -> bool:
        """Ask user to confirm an action."""
        response = self.get_user_input(f"{message} (y/N): ").lower()
        return response in ['y', 'yes'] 