"""
Interactive CLI interface for prompt optimization.
"""

import asyncio
from .base import BaseCLI
from ..ai.prompt_optimizer import PromptOptimizer
from ..core.logging import get_logger


class InteractiveCLI(BaseCLI):
    """Interactive command-line interface for Office prompt optimization."""
    
    def __init__(self):
        super().__init__()
        self.optimizer = PromptOptimizer()
        self.logger = get_logger(__name__)
    
    def run(self) -> None:
        """Main interactive loop."""
        self.display_welcome(
            "Interactive Office Optimizer",
            "I'll help optimize your Word/Excel requests through conversation!"
        )
        
        current_model = self.optimizer.model_types[self.optimizer.target_model_type]["name"]
        self.display_info(f"Target Model: {current_model}")
        self.display_info("Commands: /q=quit, /e=exit, /c=clear, /t=template, /l=list, /mb=big model, /ms=small model\n")
        
        while True:
            try:
                user_input = self.get_user_input("📝 Your request: ")
                
                if self._is_exit_command(user_input):
                    self.display_success("Goodbye!")
                    break
                
                if self._is_clear_command(user_input):
                    response = self.optimizer.clear_conversation()
                    self.display_success(response)
                    continue

                if self._is_list_command(user_input):
                    response = self.optimizer.list_templates()
                    self.display_info(response)
                    continue

                if self._is_template_command(user_input):
                    template_name = self.get_user_input("📄 Template name: ")
                    prompt_input = self.get_user_input("📝 Your request: ")
                    response = asyncio.run(self.optimizer.process_with_template(prompt_input, template_name))
                    formatted_response = response.replace('\\n', '\n')
                    print(f"🤖 {formatted_response}\n")
                    continue
                
                if not user_input:
                    continue
                
                self.display_info("🤔 Processing...")
                response = asyncio.run(self.optimizer.optimize_prompt(user_input))
                # Replace escaped newlines with actual newlines for better display
                formatted_response = response.replace('\\n', '\n')
                print(f"🤖 {formatted_response}\n")
                
            except KeyboardInterrupt:
                self.display_success("Goodbye!")
                break
            except Exception as e:
                self.display_error(str(e))
                self.logger.error(f"Error in interactive CLI: {e}")
    
    def _is_exit_command(self, user_input: str) -> bool:
        """Check if user input is an exit command."""
        return user_input.lower() in ['/q', '/quit', '/e', '/exit']
    
    def _is_clear_command(self, user_input: str) -> bool:
        """Check if user input is a clear command."""
        return user_input.lower() in ['/c', '/clear']

    def _is_template_command(self, user_input: str) -> bool:
        """Check if user input is a template command."""
        return user_input.lower() in ['/t', '/template']

    def _is_list_command(self, user_input: str) -> bool:
        """Check if user input is a list command."""
        return user_input.lower() in ['/l', '/list']