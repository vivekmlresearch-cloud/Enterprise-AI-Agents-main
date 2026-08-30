from fastapi import FastAPI

app = FastAPI(title='Logs MCP Stub')


@app.get('/tools')
def tools():
    return {
        'tools': [
            {'name': 'query_logs', 'description': 'Query ClickHouse for logs by service, severity, and time range.'},
            {'name': 'compare_baseline', 'description': 'Compare current error levels to historical baseline.'},
        ]
    }
