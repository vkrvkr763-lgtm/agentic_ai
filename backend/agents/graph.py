
from langgraph.graph import StateGraph, START, END

from backend.agents.state import GAARDState
from backend.agents.routing_agent import routing_agent
from backend.agents.notification_agent import notification_agent
from backend.agents.image_quality_agent import image_quality_agent
from backend.agents.vision_agent import vision_agent
from backend.agents.decision_agent import (
    decision_agent,
    decide_after_quality_check
)


# Decision after routing
def notify_decision(state: GAARDState):
    if state.get("routing_status") == "routed":
        return "notify"
    return "end"


# Decision after AI validation
def route_decision(state: GAARDState) -> str:
    decision = state.get("decision")

    if decision == "approved":
        return "approved"
    if decision == "rejected":
        return "rejected"

    return "human_review"


# Create graph builder
builder = StateGraph(GAARDState)


# Register agents
builder.add_node("image_quality_agent", image_quality_agent)
builder.add_node("vision_agent", vision_agent)
builder.add_node("decision_agent", decision_agent)
builder.add_node("routing_agent", routing_agent)
builder.add_node("notification_agent", notification_agent)


# Starting point
builder.add_edge(START, "image_quality_agent")


# Image quality conditional routing
builder.add_conditional_edges(
    "image_quality_agent",
    decide_after_quality_check,
    {
        "analyze": "vision_agent",
        "retake": END,
        "error": END
    }
)


# Vision -> Decision
builder.add_edge("vision_agent", "decision_agent")


# Decision conditional routing
builder.add_conditional_edges(
    "decision_agent",
    route_decision,
    {
        "approved": "routing_agent",
        "rejected": END,
        "human_review": END
    }
)


# Routing -> Notification conditional routing
builder.add_conditional_edges(
    "routing_agent",
    notify_decision,
    {
        "notify": "notification_agent",
        "end": END
    }
)


# Notification -> End
builder.add_edge("notification_agent", END)


# Compile graph
gaard_graph = builder.compile()
