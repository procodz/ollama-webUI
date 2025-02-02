import streamlit as st
import requests
import json
import PyPDF2
import io
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_for_filename, TextLexer

def initialize_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'file_content' not in st.session_state:
        st.session_state.file_content = None
    if 'file_type' not in st.session_state:
        st.session_state.file_type = None

def read_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text, "pdf"

def read_code_file(uploaded_file):
    content = uploaded_file.getvalue().decode("utf-8")
    try:
        lexer = get_lexer_for_filename(uploaded_file.name)
        formatter = HtmlFormatter(style='monokai')
        highlighted = highlight(content, lexer, formatter)
        css = formatter.get_style_defs()
        return content, uploaded_file.name.split('.')[-1], highlighted, css
    except:
        return content, "text", content, ""

def read_file_content(uploaded_file):
    if uploaded_file.type == "application/pdf":
        content, file_type = read_pdf(uploaded_file)
        return content, file_type, content, ""
    else:
        return read_code_file(uploaded_file)

def stream_chat_with_ollama(messages, model="llama3.2"):
    url = "http://localhost:11434/api/chat"
    
    data = {
        "model": model,
        "messages": messages,
        "stream": True
    }
    
    try:
        response = requests.post(url, json=data, stream=True)
        response.raise_for_status()
        
        full_response = ""
        placeholder = st.empty()
        
        for line in response.iter_lines():
            if line:
                json_response = json.loads(line)
                if 'message' in json_response:
                    chunk = json_response['message']['content']
                    full_response += chunk
                    placeholder.markdown(full_response + "▌")
        
        placeholder.markdown(full_response)
        return full_response
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

def main():
    st.title("🦙 Ollama Chat Interface")
    
    initialize_session_state()
    
    with st.sidebar:
        st.header("Configuration")
        model = st.selectbox(
            "Select Model",
            ["llama3.2"],
            index=0
        )
        
        # File upload in sidebar
        st.header("File Upload")
        uploaded_file = st.file_uploader(
            "Upload a file to chat about",
            type=["txt", "pdf", "py", "js", "java", "cpp", "c", "html", "css", "json", "yaml", "sql", "sh", "r", "md"],
            help="Supported formats: Text, Code (Python, JavaScript, Java, C++, etc.), PDF"
        )
        
        if uploaded_file:
            content, file_type, highlighted_content, css = read_file_content(uploaded_file)
            st.session_state.file_content = content
            st.session_state.file_type = file_type
            st.success(f"File '{uploaded_file.name}' uploaded successfully!")
            
            # Add file content preview with syntax highlighting
            with st.expander("Preview File Content"):
                if css:  # If it's a code file with syntax highlighting
                    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
                    st.markdown(highlighted_content, unsafe_allow_html=True)
                else:
                    st.text(content[:1000] + "..." if len(content) > 1000 else content)
        
        if st.button("Clear Conversation"):
            st.session_state.messages = []
            st.session_state.file_content = None
            st.session_state.file_type = None
            st.rerun()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about the uploaded code or chat normally"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Prepare messages including file context if available
        ollama_messages = []
        
        if st.session_state.file_content:
            # Add file content as context in system message with file type information
            context_message = f"This is a {st.session_state.file_type.upper()} file:\n\n{st.session_state.file_content}\n\n"
            context_message += "Please analyze this code and answer any questions about it. If asked to suggest improvements, provide specific code examples."
            
            ollama_messages.append({
                "role": "system",
                "content": context_message
            })
        
        # Add conversation history
        ollama_messages.extend([
            {"role": msg["role"], "content": msg["content"]}
            for msg in st.session_state.messages
        ])
        
        # Display assistant response with streaming
        with st.chat_message("assistant"):
            response = stream_chat_with_ollama(ollama_messages, model)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()