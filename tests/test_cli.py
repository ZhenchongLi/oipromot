"""
Tests for CLI components.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.oipromot.cli.interactive import InteractiveCLI
from src.oipromot.cli.simple import SimpleCLI


class TestInteractiveCLI:
    """Test cases for InteractiveCLI."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.cli = InteractiveCLI()
    
    def test_cli_initialization(self):
        """Test CLI initializes properly."""
        assert self.cli.optimizer is not None
        assert hasattr(self.cli.optimizer, 'optimize_prompt')
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_quit_command(self, mock_print, mock_input):
        """Test quit command works."""
        mock_input.side_effect = ['/q']
        
        self.cli.run()
        
        # Should have printed goodbye message
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Goodbye" in call for call in calls)
    
    @patch('builtins.input')
    @patch('builtins.print') 
    def test_clear_command(self, mock_print, mock_input):
        """Test clear command works."""
        mock_input.side_effect = ['/c', '/q']
        
        self.cli.run()
        
        # Should have printed clear message
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("cleared" in call.lower() for call in calls)


class TestSimpleCLI:
    """Test cases for SimpleCLI."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.cli = SimpleCLI()
    
    def test_cli_initialization(self):
        """Test CLI initializes properly."""
        assert self.cli.deepseek is not None
    
    def test_mock_responses(self):
        """Test mock responses work correctly."""
        # Test known response
        result = self.cli._mock_response("make text bigger")
        assert "font size" in result.lower()
        
        # Test unknown input
        result = self.cli._mock_response("unknown command")
        assert "specific command needed" in result
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_simple_interaction(self, mock_print, mock_input):
        """Test simple interaction flow."""
        mock_input.side_effect = ['make text bigger', '/q']
        
        self.cli.run()
        
        # Should have processed the request and printed result
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("font" in call.lower() for call in calls)