"""LangGraph definition for meal plan generation."""

from sqlalchemy.ext.asyncio import AsyncSession
from langgraph.graph import END, StateGraph

from app.planner.nodes import (
    create_derive_artifacts,
    create_generate_draft,
    create_load_context,
    create_persist_plan,
    create_repair_plan,
    create_retrieve_seeds,
    create_search_recipes_node,
    create_validate_plan,
)
from app.planner.state import PlannerState


def should_repair(state) -> str:
    """Conditional edge: repair if validation failed and attempts < 2."""
    # Handle both dict and PlannerState
    if hasattr(state, "validation_passed"):
        validation_passed = state.validation_passed
        repair_attempts = state.repair_attempts
    else:
        validation_passed = state.get("validation_passed", False)
        repair_attempts = state.get("repair_attempts", 0)
    
    if not validation_passed and repair_attempts < 2:
        return "repair"
    elif validation_passed:
        return "continue"
    else:
        return "fail"


def create_planner_graph(session: AsyncSession) -> StateGraph:
    """Create the meal plan generation graph.

    Args:
        session: Database session to use in nodes

    Returns:
        Compiled LangGraph StateGraph
    """
    # Create graph with dict state (PlannerState as schema)
    workflow = StateGraph(PlannerState)

    # Create node functions with session bound
    workflow.add_node("load_context", create_load_context(session))
    workflow.add_node("retrieve_seeds", create_retrieve_seeds(session))
    workflow.add_node("search_recipes", create_search_recipes_node(session))
    workflow.add_node("generate_draft", create_generate_draft(session))
    workflow.add_node("validate_plan", create_validate_plan(session))
    workflow.add_node("repair_plan", create_repair_plan(session))
    workflow.add_node("derive_artifacts", create_derive_artifacts(session))
    workflow.add_node("persist_plan", create_persist_plan(session))

    # Set entry point
    workflow.set_entry_point("load_context")

    # Add edges
    workflow.add_edge("load_context", "retrieve_seeds")
    workflow.add_edge("retrieve_seeds", "search_recipes")
    workflow.add_edge("search_recipes", "generate_draft")
    workflow.add_edge("generate_draft", "validate_plan")

    # Conditional edge from validate_plan
    workflow.add_conditional_edges(
        "validate_plan",
        should_repair,
        {
            "repair": "repair_plan",
            "continue": "derive_artifacts",
            "fail": END,
        },
    )

    # Repair loop back to validate
    workflow.add_edge("repair_plan", "validate_plan")

    # Success path
    workflow.add_edge("derive_artifacts", "persist_plan")
    workflow.add_edge("persist_plan", END)

    # Compile graph
    return workflow.compile()

