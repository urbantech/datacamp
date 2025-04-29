import json
from github import Github
import os

# Load GitHub token from environment variable
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
if not GITHUB_TOKEN:
    print("Please set the GITHUB_TOKEN environment variable")
    exit(1)

# Initialize GitHub client
g = Github(GITHUB_TOKEN)

# Get the repository
repo = g.get_repo('urbantech/datacamp')

# Load issues from JSON file
with open('issues.json', 'r') as f:
    issues_data = json.load(f)

# Create a milestone for Sprint 1
milestone = repo.create_milestone("BoomScraper Sprint 1", state="open", description="First sprint for BoomScraper project")

# Create issues
for issue in issues_data:
    try:
        # Prepare labels
        labels = issue.get('labels', [])
        
        # Create issue
        created_issue = repo.create_issue(
            title=issue['title'],
            body=issue['body'] + f"\n\n**Weight:** {issue.get('weight', 1)} points",
            labels=labels,
            milestone=milestone
        )
        print(f"Created issue: {created_issue.title}")
    except Exception as e:
        print(f"Error creating issue {issue['title']}: {e}")

print("Issue creation complete!")
