
"""Groq-powered chatbot for the retirement simulator."""

import json
from urllib import request, error

import streamlit as st


GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def ask_groq(context, messages):
    """Ask Groq using simulator data and conversation history."""
    api_key = st.secrets["GROQ_API_KEY"]
    model = st.secrets.get("GROQ_MODEL", "llama-3.3-70b-versatile")

    system_prompt = (
        "You are a financial-planning assistant inside a retirement "
        "simulator. Explain calculations, inflation, retirement "
        "expenses and investment projections clearly. "
        "Use the supplied simulator data as the source of truth. "
        "Do not invent missing financial data or assume that "
        "unverified calculations are correct. "
        "Distinguish nominal values from inflation-adjusted values. "
        "All monetary amounts are in Indian rupees. "
        "Rates are stored as decimals, e.g. 0.05 means 5%. "
        "If information is unavailable, say so.\n\n"
        "Simulator data:\n"
        + json.dumps(context, ensure_ascii=False, default=str)
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            *messages[-12:],
        ],
        "temperature": 0.2,
        "max_tokens": 1000,
        "stream": False,
    }

    req = request.Request(
        GROQ_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "retirement-simulator/1.0",
        },
        method="POST",
    )

    with request.urlopen(req, timeout=60) as response:
        result = json.load(response)

    return result["choices"][0]["message"]["content"]


def render_chatbot_launcher(context):
    """Display the Groq chatbot within Streamlit."""
    context_key = json.dumps(context, sort_keys=True, default=str)

    if st.session_state.get("groq_context_key") != context_key:
        st.session_state["groq_context_key"] = context_key
        st.session_state["groq_chat_history"] = []

    with st.popover("💬 Ask Groq"):
        st.caption(
            f"Powered by Groq | "
            f"{st.secrets.get('GROQ_MODEL', 'llama-3.3-70b-versatile')}"
        )

        history = st.session_state["groq_chat_history"]

        for message in history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        with st.form("groq_chat_form", clear_on_submit=True):
            question = st.text_input(
                "Your question",
                placeholder="What are my inflation-adjusted expenses?",
            )
            send = st.form_submit_button("Send")

        if send and question.strip():
            user_message = {
                "role": "user",
                "content": question.strip(),
            }

            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        reply = ask_groq(
                            context,
                            history + [user_message],
                        )
                        st.markdown(reply)
                        history.extend([
                            user_message,
                            {"role": "assistant", "content": reply},
                        ])

                    except error.HTTPError as exc:
                        details = exc.read().decode("utf-8", errors="replace")
                        st.error(f"Groq API error {exc.code}: {details}")

                    except (error.URLError, TimeoutError, OSError) as exc:
                        st.error(f"Connection error: {exc}")

                    except (KeyError, ValueError, TypeError) as exc:
                        st.error(f"Invalid API response: {exc}")

        if st.button("Clear chat", key="groq_clear_chat"):
            st.session_state["groq_chat_history"] = []
            st.rerun()
