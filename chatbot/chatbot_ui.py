
import streamlit as st

from chatbot.chatbot_backend import get_ai_response


def render_chatbot_launcher(context):

    # --------------------------------------------------
    # 1. INITIALISE SESSION STATE
    # --------------------------------------------------

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    if "chatbot_open" not in st.session_state:
        st.session_state.chatbot_open = False

    # --------------------------------------------------
    # 2. FLOATING BUTTON STYLING
    # --------------------------------------------------

    st.markdown(
        """
        <style>
        div.st-key-open_ai_assistant {
            position: fixed;
            right: 28px;
            bottom: 28px;
            z-index: 999999;
        }

        div.st-key-open_ai_assistant button {
            border-radius: 30px;
            padding: 12px 22px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------
    # 3. FLOATING CHATBOT LAUNCHER
    # --------------------------------------------------

    if st.button(
        "💬 AI Assistant",
        key="open_ai_assistant",
        type="primary"
    ):
        st.session_state.chatbot_open = (
            not st.session_state.chatbot_open
        )

    # --------------------------------------------------
    # 4. CHATBOT DIALOG
    # --------------------------------------------------

    if st.session_state.chatbot_open:

        @st.dialog("AI Assistant", width="large")
        def chat_window():

            st.caption(
                "Ask me anything about the Retirement Expenditure Simulator."
            )

            # Header controls
            col1, col2 = st.columns([5, 1])

            with col1:
                st.caption("Your conversations are stored for this session.")

            with col2:
                if st.button("Clear", key="clear_chat"):
                    st.session_state.chat_messages = []
                    st.rerun()

            # Close dialog
            if st.button("Close chat", key="close_chat"):
                st.session_state.chatbot_open = False
                st.rerun()

            st.divider()

            # --------------------------------------------------
            # 5. DISPLAY CONVERSATION HISTORY
            # --------------------------------------------------

            for message in st.session_state.chat_messages:

                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # --------------------------------------------------
            # 6. CHAT INPUT
            # --------------------------------------------------

            user_input = st.chat_input(
                "Ask something about your retirement simulator..."
            )

            if user_input:

                # Save user message
                st.session_state.chat_messages.append({
                    "role": "user",
                    "content": user_input
                })

                # Display thinking indicator
                with st.spinner("Thinking..."):

                    try:
                        answer = get_ai_response(
                            context,
                            st.session_state.chat_messages
                        )

                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": answer
                        })

                    except Exception as e:

                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": (
                                "I couldn't generate a response.\n\n"
                                f"**Error:** {str(e)}"
                            )
                        })

                # Refresh dialog to show the latest messages
                st.rerun()

        chat_window()
