
"""Local Qwen chatbot for the retirement simulator (Ollama backend)."""

import json
import os
from urllib import error, request

import streamlit as st


OLLAMA_URL = st.secrets["OLLAMA_URL"]
MODEL = st.secrets["OLLAMA_MODEL"]


def ask_qwen(context, messages):
    """Return Qwen's reply using app inputs and recent chat messages."""
    system_prompt = (
        "You are a financial-planning explainer inside a retirement simulator. "
        "Use the supplied simulator data as the source of truth for its inputs "
        "and outputs. Explain assumptions, inflation, and computations clearly. "
        "Do not invent missing asset, fund, withdrawal, or investment figures. "
        "If the data does not include a requested value, say it is not available. "
        "Do not present model-generated arithmetic as a verified simulator result. "
        "The simulation uses sampled inflation scenarios, not guaranteed outcomes. "
        "Amounts are in Indian rupees; rates are stored as decimals "
        "(0.04 means 4%).\n\nCurrent simulator data:\n"
        + json.dumps(context, ensure_ascii=False, sort_keys=True)
    )
    payload = {
        "model": MODEL,
        "messages": [{"role": "system", "content": system_prompt}] + messages[-12:],
        "stream": False,
        "think": False,
        "options": {"temperature": 0.2},
    }
    req = request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=120) as response:
        result = json.load(response)
    answer = result.get("message", {}).get("content", "").strip()
    if not answer:
        raise ValueError("Ollama returned no answer. Check the loaded model.")
    return answer


def render_chatbot_launcher(context):
    """Show an embedded Qwen chat launcher linked to current simulator inputs."""
    context_key = json.dumps(context, ensure_ascii=False, sort_keys=True)
    if st.session_state.get("qwen_context_key") != context_key:
        st.session_state["qwen_context_key"] = context_key
        st.session_state["qwen_chat_history"] = []

    with st.popover("💬 Ask Qwen"):
        st.caption(f"Local model: `{MODEL}` · Ollama")
        history = st.session_state["qwen_chat_history"]
        for message in history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        with st.form("qwen_chat_form", clear_on_submit=True):
            question = st.text_input(
                "Your question", placeholder="What will my expenses be at 60?"
            )
            send = st.form_submit_button("Send")

        if send and question.strip():
            user_message = {"role": "user", "content": question.strip()}
            history.append(user_message)
            with st.chat_message("user"):
                st.markdown(user_message["content"])
            with st.chat_message("assistant"):
                with st.spinner("Qwen is responding..."):
                    try:
                        reply = ask_qwen(context, history)
                    except error.HTTPError as exc:
                        st.error(
                            f"Ollama HTTP {exc.code}. Check that model `{MODEL}` "
                            "appears in `ollama list`."
                        )
                        return
                    except (error.URLError, TimeoutError, OSError) as exc:
                        st.error(
                            "Cannot reach the local Ollama server at "
                            f"{OLLAMA_URL}. Make sure Ollama is running. ({exc})"
                        )
                        return
                    except (ValueError, json.JSONDecodeError) as exc:
                        st.error(f"Invalid response from Ollama: {exc}")
                        return
                    st.markdown(reply)
                    history.append({"role": "assistant", "content": reply})

        if st.button("Clear chat", key="qwen_clear_chat"):
            st.session_state["qwen_chat_history"] = []
            st.rerun()
