import sys

import requests

# Test URL: n8n only answers it after you click "Execute workflow" in the editor, and only once.
# After activating the workflow, switch to the production URL:
#   http://localhost:5678/webhook/search
WEBHOOK_URL = "http://localhost:5678/webhook-test/search"


def trigger(topic):
    print(f"Sending topic to n8n: {topic!r}")
    try:
        response = requests.post(WEBHOOK_URL, json={"topic": topic}, timeout=30)
    except requests.exceptions.ConnectionError:
        print("Could not connect. Is n8n running, and is WEBHOOK_URL correct?")
        return 1

    if response.status_code == 200:
        print("Accepted. The workflow is running; a Google Doc named after the topic")
        print("will fill in over the next several minutes.")
        return 0

    print(f"n8n returned {response.status_code}: {response.text}")
    return 1


if __name__ == "__main__":
    topic = " ".join(sys.argv[1:]).strip() or input("Enter a research topic: ").strip()
    if not topic:
        print("Topic cannot be empty.")
        sys.exit(1)
    sys.exit(trigger(topic))
