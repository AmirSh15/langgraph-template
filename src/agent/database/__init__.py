"""
This module initializes the database package and sets up the database connection.
"""

from .jira import load_mock_jira_database
__all__ = ["load_mock_jira_database"]