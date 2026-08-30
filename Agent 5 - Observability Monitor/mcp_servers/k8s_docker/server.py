from fastapi import FastAPI

app = FastAPI(title='Kubernetes Docker MCP Stub')


@app.get('/tools')
def tools():
    return {
        'tools': [
            {'name': 'inspect_pod', 'description': 'Inspect Kubernetes pod state and events.'},
            {'name': 'docker_logs', 'description': 'Fetch container logs for an affected service.'},
        ]
    }
