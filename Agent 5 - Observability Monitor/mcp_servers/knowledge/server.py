from fastapi import FastAPI

app = FastAPI(title='Knowledge MCP Stub')


@app.get('/resources')
def resources():
    return {
        'resources': [
            {'name': 'runbooks', 'description': 'Operational runbooks and remediation steps.'},
            {'name': 'incident_memory', 'description': 'Historical incident summaries and postmortems.'},
        ]
    }
