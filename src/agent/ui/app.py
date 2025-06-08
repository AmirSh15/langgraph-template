# ---  Streamlit User Interface ---

import streamlit as st
from agent.graph.graph import load_jira_graph
from langchain_core.messages import HumanMessage

def init_session_state():
    """Initialize chat history in session state."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

def display_chat_history():
    """Display chat messages from history on app rerun."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def handle_user_input(app):
    """Handle user input and agent response."""
    if prompt := st.chat_input("What would you like to know?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get the response from the LangGraph agent
        with st.spinner("Thinking..."):
            inputs = {"messages": [HumanMessage(content=prompt)]}
            response = app.invoke(inputs)
            bot_response = response["messages"][-1].content

        # Add bot response to chat history
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        # Display bot response
        with st.chat_message("assistant"):
            st.markdown(bot_response)

def main():
    st.title("Jira Assistant Chatbot 🤖 (Mock Mode)")
    st.write("I can help you search for issues in a mock Jira database. Try asking 'show me all issues in project PROJ'")

    app = load_jira_graph()
    init_session_state()
    display_chat_history()
    handle_user_input(app)

if __name__ == "__main__":
    main()
