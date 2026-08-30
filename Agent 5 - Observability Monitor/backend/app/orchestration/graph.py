from __future__ import annotations

from langgraph.graph import END, StateGraph

from app.orchestration.state import IncidentState
from app.schemas.common import IncidentSummary, Recommendation
from app.services.anomaly import AnomalyDetector
from app.services.history import HistoryService
from app.services.llm import VLLMClient

anomaly_detector = AnomalyDetector()
history_service = HistoryService()
llm_client = VLLMClient()


async def detect_anomaly(state: IncidentState) -> IncidentState:
    state['anomaly'] = anomaly_detector.detect(state.get('logs', []))
    return state


async def retrieve_context(state: IncidentState) -> IncidentState:
    service = state['service']
    logs = state.get('logs', [])
    evidence = history_service.find_similar_incidents(service, logs)
    evidence.extend(history_service.relevant_runbooks(service))
    state['evidence'] = evidence
    return state


async def reason_with_llm(state: IncidentState) -> IncidentState:
    anomaly = state.get('anomaly', {})
    logs = state.get('logs', [])[:20]
    evidence = state.get('evidence', [])
    system_prompt = (
        'You are an observability incident analyst. Produce a concise operational analysis, likely causes, next likely events, and recommended actions.'
    )
    user_prompt = f'''
Service: {state['service']}
Environment: {state['environment']}
Anomaly summary: {anomaly}
Recent logs: {[{'severity': l.severity, 'message': l.message} for l in logs]}
Historical context: {[{'title': e.title, 'content': e.content} for e in evidence]}
Return short prose suitable for operators.
'''
    try:
        state['llm_summary'] = await llm_client.complete(system_prompt, user_prompt)
    except Exception:
        state['llm_summary'] = (
            'Recent warning and error concentration suggests an elevated failure pattern. Check dependency health, deployment changes, and queue saturation.'
        )
    return state


async def recommend_actions(state: IncidentState) -> IncidentState:
    anomaly = state.get('anomaly', {})
    severity = anomaly.get('severity', 'INFO')
    recommendations = [
        Recommendation(
            title='Validate upstream dependencies',
            detail='Check whether the affected service has upstream timeout or connection issues.',
            confidence=0.82,
            requires_approval=False,
        ),
        Recommendation(
            title='Review recent deployment or config drift',
            detail='Compare the current release and config to the last known healthy state.',
            confidence=0.77,
            requires_approval=False,
        ),
    ]
    if severity in {'HIGH', 'CRITICAL'}:
        recommendations.append(
            Recommendation(
                title='Send operator alert',
                detail='Notify the on-call channel with evidence and recommended checks.',
                confidence=0.9,
                requires_approval=False,
            )
        )

    state['recommendations'] = recommendations
    state['summary'] = IncidentSummary(
        title=f"{state['service']} anomaly analysis",
        severity=severity,
        summary=state.get('llm_summary', 'No summary generated.'),
        likely_causes=[
            'Upstream dependency degradation',
            'Recent deployment or configuration change',
            'Traffic spike or queue saturation',
        ],
        what_may_happen_next=[
            'Error rate may continue rising if dependency health remains degraded.',
            'Latency and timeout volume may increase in the next 15 to 30 minutes.',
        ],
        recommendations=recommendations,
        evidence=state.get('evidence', []),
    )
    return state


def build_graph():
    graph = StateGraph(IncidentState)
    graph.add_node('detect_anomaly', detect_anomaly)
    graph.add_node('retrieve_context', retrieve_context)
    graph.add_node('reason_with_llm', reason_with_llm)
    graph.add_node('recommend_actions', recommend_actions)

    graph.set_entry_point('detect_anomaly')
    graph.add_edge('detect_anomaly', 'retrieve_context')
    graph.add_edge('retrieve_context', 'reason_with_llm')
    graph.add_edge('reason_with_llm', 'recommend_actions')
    graph.add_edge('recommend_actions', END)

    return graph.compile()
