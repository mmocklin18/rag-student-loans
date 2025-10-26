import streamlit as st
from rag import qa_chain

st.title("Student Loan Q&A Assistant")

# Initialize session state for chat history if it doesn't exist
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Input box for user question
question = st.text_input("Ask a question about student loans:")

if question:
    result = qa_chain.invoke({"query": question})
    answer = result["result"]
    sources = result["source_documents"]
    
    # Display answer
    st.write("### Answer:")
    st.write(answer)
    
    # Display sources
    st.write("### Sources:")
    for i, doc in enumerate(sources):
        with st.expander(f"Source {i+1}: {doc.metadata['source']}"):
            st.write(doc.page_content)
    
    # Add to chat history
    st.session_state.chat_history.append({"question": question, "answer": answer})

# Display chat history
if st.session_state.chat_history:
    st.write("### Chat History:")
    for chat in reversed(st.session_state.chat_history):
        with st.expander(f"Q: {chat['question']}", expanded=False):
            st.write(chat["answer"])