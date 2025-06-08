# --- Helper classes to mimic Jira's object structure ---
class MockStatus:
    """A mock for the status object in a Jira issue."""
    def __init__(self, name):
        self.name = name

class MockFields:
    """A mock for the fields object in a Jira issue."""
    def __init__(self, summary, status):
        self.summary = summary
        self.status = MockStatus(status)

class MockIssue:
    """A mock for a Jira issue object."""
    def __init__(self, key, summary, status):
        self.key = key
        self.fields = MockFields(summary, status)

# --- Mock Database with synthetic Jira issues ---
def load_mock_jira_database():
    """Load a mock database of Jira issues."""
    mock_database = {
        "PROJ": [
            MockIssue("PROJ-1", "Fix login button bug on the main page", "To Do"),
            MockIssue("PROJ-2", "Implement new feature for user profiles", "In Progress"),
            MockIssue("PROJ-3", "Update documentation for the public API", "Done"),
        ],
        "WEB": [
            MockIssue("WEB-101", "Redesign the entire landing page", "In Progress"),
            MockIssue("WEB-102", "Fix mobile responsiveness issues", "Done"),
        ],
        "DATA": [
            MockIssue("DATA-42", "Create new sales performance dashboard", "In Review"),
        ]
    }
    return mock_database
