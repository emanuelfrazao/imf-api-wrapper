import pytest
from src.wrapper import IMFWrapper

def test_initialization():
    """Test the initialization of the wrapper class."""
    imf = IMFWrapper()
    assert imf.datasets is not None