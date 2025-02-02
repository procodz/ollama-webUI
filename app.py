import streamlit as st
import subprocess

# Streamlit app title
st.title("Ollama LLM Web UI 🦙")

# Add a description with enhanced formatting
st.markdown(
    """
    <div style='background-color: #f9f9f9; padding: 20px; border-radius: 15px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);'>
        <h4 style='font-family: "Segoe UI", sans-serif; color: #333;'>Welcome to the Ollama LLM Web UI!</h4>
        <p style='font-family: "Segoe UI", sans-serif; color: #555;'>Enter your prompt below and click <strong>Generate Response</strong> to get insights from the <code>llama3.2</code> model.</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# Initialize session state for conversation history
if "conversation" not in st.session_state:
    st.session_state["conversation"] = []

# Input text box for the user prompt with enhanced styling
prompt = st.text_area(
    "🔍 Enter your prompt here:", 
    height=150, 
    placeholder="e.g., Explain quantum computing in simple terms.",
    max_chars=1000,
    key="prompt_input"
)

# Create two columns for buttons (Generate Response and Clear Input)
col1, col2 = st.columns([2, 1])

# Button to generate a response
with col1:
    if st.button("Generate Response 🚀", key="generate_response"):
        if not prompt:
            st.error("Please enter a prompt!")
        else:
            with st.spinner("Generating response... 🌐"):
                try:
                    # Append user prompt to the conversation history
                    st.session_state["conversation"].append({"role": "user", "text": prompt})

                    # Collect the full conversation for context
                    context = "\n".join([f"User: {msg['text']}" if msg['role'] == "user" else f"Model: {msg['text']}"
                                         for msg in st.session_state["conversation"]])

                    # Generate model response
                    result = subprocess.run(
                        ['ollama', 'run', 'llama3.2', context],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode != 0:
                        st.error(f"Error: {result.stderr}")
                    else:
                        response = result.stdout.strip()
                        st.session_state["conversation"].append({"role": "model", "text": response})

                        # Display the full conversation
                        st.markdown("### Conversation History")
                        for message in st.session_state["conversation"]:
                            role = "**User:**" if message["role"] == "user" else "**Model:**"
                            st.markdown(
                                f"""<div style='background-color: #eaf7ff; padding: 12px 15px; border-radius: 8px; margin-bottom: 12px;'>
                                <strong style="color: #333;">{role}</strong> <span style='color: #333;'>{message['text']}</span>
                                </div>""", 
                                unsafe_allow_html=True
                            )

                except Exception as e:
                    st.error(f"An error occurred: {e}")

# Button to clear the input and conversation history
with col2:
    if st.button("Clear Input ❌", key="clear_input"):
        st.session_state["conversation"] = []
        st.session_state["prompt_input"] = ""  # Clear input field
        st.experimental_rerun()

# Add a divider for visual separation
st.markdown("<hr style='border: 1px solid #eaeaea;'>", unsafe_allow_html=True)

# Add a footer with subtle UI styling
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        text-align: center;
        padding: 15px;
        background-color: #f1f1f1;
        font-size: 14px;
        color: #333;
        border-top: 1px solid #eaeaea;
    }
    .block-container { max-width: 1200px; }
    pre { white-space: pre-wrap; word-wrap: break-word; }
    </style>
    <div class="footer">
        💖 Made with <strong>Streamlit</strong> and <strong>Ollama</strong>
    </div>
    """, 
    unsafe_allow_html=True
)
