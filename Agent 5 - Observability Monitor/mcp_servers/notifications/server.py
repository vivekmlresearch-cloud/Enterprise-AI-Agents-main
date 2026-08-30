from fastapi import FastAPI

app = FastAPI(title='Notifications MCP Stub')


@app.get('/tools')
def tools():
    return {
        'tools': [
            {'name': 'send_email', 'description': 'Send incident summary email.'},
            {'name': 'post_slack', 'description': 'Post Slack incident notification.'},
            {'name': 'trigger_pagerduty', 'description': 'Open PagerDuty incident.'},
        ]
    }
