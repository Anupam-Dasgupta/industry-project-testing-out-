
import time
import streamlit as st
from google import genai
from chatbot.system_prompt import get_system_prompt


def get_ai_response(context, messages):
    """
    Generate an AI response using Google's Gemini API.

    Parameters
    ----------
    context : dict
        Current simulator parameters and calculated results.

    messages : list
        Conversation history containing role and content.

    Returns
    -------
    str
        Gemini's response.
    """

    # 1. Check API configuration
    try:
        api_key = st.secrets["GEMINI_API_KEY"]

        if not api_key:
            raise ValueError("Gemini API key is empty.")

        model_name = st.secrets.get(
            "GEMINI_MODEL",
            "gemini-2.5-flash"
        )

    except KeyError as e:
        raise RuntimeError(
            "GEMINI_API_KEY is missing from .streamlit/secrets.toml."
        ) from e

    except Exception as e:
        raise RuntimeError(
            f"Could not load Gemini configuration: {e}"
        ) from e

    # 2. Initialize Gemini
    try:
        client = genai.Client(api_key=api_key)

    except Exception as e:
        raise RuntimeError(
            f"Could not initialize Gemini client: {e}"
        ) from e

    # 3. Prepare system prompt
    system_prompt = get_system_prompt(context)

    # 4. Convert conversation history
    conversation = []

    for message in messages:
        role = (
            "user"
            if message["role"] == "user"
            else "model"
        )

        content = message.get("content", "")

        if content.strip():
            conversation.append({
                "role": role,
                "parts": [{"text": content}]
            })

    if not conversation:
        raise RuntimeError("No valid conversation messages found.")

    # 5. Generate response with retry handling
    max_attempts = 3

    for attempt in range(max_attempts):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=conversation,
                config={
                    "system_instruction": system_prompt,
                    "temperature": 0.7,
                }
            )

            if not response or not response.text:
                raise RuntimeError(
                    "Gemini returned an empty response. Please try again."
                )

            return response.text.strip()

        except Exception as e:
            error_message = str(e).lower()

            temporary_error = any(
                code in error_message
                for code in [
                    "429",
                    "500",
                    "502",
                    "503",
                    "504",
                    "resource_exhausted",
                    "unavailable",
                    "internal",
                    "deadline_exceeded",
                ]
            )

            if temporary_error and attempt < max_attempts - 1:
                time.sleep(2 ** attempt)
                continue

            if "429" in error_message or "resource_exhausted" in error_message:
                raise RuntimeError(
                    "Gemini API rate limit reached. "
                    "Please wait a little before trying again."
                ) from e

            if any(code in error_message for code in ["503", "unavailable"]):
                raise RuntimeError(
                    "Gemini is temporarily experiencing high demand. "
                    "Please wait a minute and try again."
                ) from e

            if "404" in error_message or "not found" in error_message:
                raise RuntimeError(
                    f"The Gemini model '{model_name}' could not be found. "
                    "Check the model name in .streamlit/secrets.toml."
                ) from e

            raise RuntimeError(
                f"Gemini response generation failed: {str(e)}"
            ) from e

    raise RuntimeError(
        "Gemini could not generate a response after multiple attempts."
    )
