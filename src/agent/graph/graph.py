import streamlit as st
import os
import re
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from typing import TypedDict, Annotated, Sequence
import operator
from dotenv import load_dotenv

from agent.database.jira import load_mock_jira_database

# --- Environment Setup and Configuration ---
# Load environment variables from a .env file (recommended for storing secrets)
# Create a .env file in the same directory as this script with:
# OPENAI_API_KEY="your_openai_api_key"
load_dotenv()


# --- Define the Mock Jira Search Tool ---
@tool
def search_jira(jql_query: str):
    """
    Searches for issues in a MOCK Jira database using a simplified JQL query.
    Returns a list of issues with their key, summary, and status.
    Example queries: "project = PROJ", "project = WEB and status = 'In Progress'"
    """
    print(f"Executing MOCK search with JQL: {jql_query}")
    try:
        # This is a very simple parser, not a full JQL engine.
        # It looks for 'project = KEY' and an optional 'status = "Status"'
        project_match = re.search(r"project\s*=\s*['\"]?(\w+)['\"]?", jql_query, re.IGNORECASE)
        status_match = re.search(r"status\s*=\s*['\"]([^'\"]+)['\"]", jql_query, re.IGNORECASE)

        if not project_match:
            return "Mock search requires a 'project = <KEY>' clause in the JQL query. For example: 'project = PROJ'"

        project_key = project_match.group(1).upper()
        
        mock_database = load_mock_jira_database()
        
        if project_key not in mock_database:
            return f"Mock project '{project_key}' not found. Available projects are: {', '.join(mock_database.keys())}"
            
        issues = mock_database[project_key]

        if status_match:
            status_to_find = status_match.group(1)
            issues = [issue for issue in issues if issue.fields.status.name.lower() == status_to_find.lower()]

        if not issues:
            return "No issues found for the given query in the mock database."

        # Format the output to be more readable
        results = []
        for issue in issues:
            results.append(
                f"- {issue.key}: {issue.fields.summary} (Status: {issue.fields.status.name})"
            )
        return "\n".join(results)
    except Exception as e:
        return f"An error occurred in the mock search tool: {e}"

# --- LangGraph Agent State Definition ---

class AgentState(TypedDict):
    """
    Represents the state of our agent.
    
    Attributes:
        messages: A sequence of messages in the conversation.
    """
    messages: Annotated[Sequence[HumanMessage | AIMessage | ToolMessage], operator.add]

# --- LangGraph Nodes ---

def agent(state: AgentState):
    """
    The main agent node that decides what to do next.
    It can either call a tool or respond to the user.
    """
    messages = state["messages"]
    
    # Initialize the OpenAI model
    # Make sure your OPENAI_API_KEY is set in your environment
    llm = ChatOpenAI(model="gpt-4o")

    # Bind the Jira search tool to the language model
    # This allows the model to decide when to use the tool
    response = llm.invoke(messages, tools=[search_jira])
    return {"messages": [response]}

# Create a ToolNode for our Jira search tool
# This node will execute the tool when called by the agent
tool_node = ToolNode([search_jira])

def should_continue(state: AgentState):
    """
    Determines whether to continue with another tool call or to end the turn.
    """
    if isinstance(state["messages"][-1], AIMessage) and not state["messages"][-1].tool_calls:
        return "end"
    else:
        return "continue"

# --- LangGraph Graph Definition ---

def load_jira_graph():
    """
    Loads the LangGraph workflow for the agent.
    This function sets up the state graph with the agent and tool nodes.
    """
    # Create a new StateGraph with our AgentState
    workflow = StateGraph(AgentState)

    # Add the agent and tool nodes to the graph
    workflow.add_node("agent", agent)
    workflow.add_node("tool", tool_node)

    # Define the conditional edges for the graph
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "tool",
            "end": END,
        },
    )

    # Add an edge from the tool node back to the agent node
    # This allows the agent to process the results of the tool call
    workflow.add_edge("tool", "agent")

    # Set the entry point of the graph to be the agent node
    workflow.set_entry_point("agent")

    # Compile the graph into a runnable application
    app = workflow.compile()

    return app


if __name__ == "__main__":
    # If this script is run directly, we can test the graph loading
    app = load_jira_graph()
    
    # Print the graph structure for debugging
    app.get_graph().draw_ascii()
    
    
