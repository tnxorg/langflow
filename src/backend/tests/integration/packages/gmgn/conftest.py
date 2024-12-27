import pytest
import sys
import os

# Add the package directory to the Python path
package_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../"))
sys.path.insert(0, package_dir)

# Override any conflicting fixtures from the main conftest
@pytest.fixture(autouse=True)
def override_langflow_fixtures():
    """Override any LangFlow fixtures to prevent them from running"""
    pass 