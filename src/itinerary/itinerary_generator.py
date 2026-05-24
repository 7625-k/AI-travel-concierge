import os

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = None

def get_client():
    global client
    if client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            try:
                import streamlit as st
                if "GROQ_API_KEY" in st.secrets:
                    api_key = st.secrets["GROQ_API_KEY"]
            except Exception:
                pass
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not set. Please set the GROQ_API_KEY environment variable "
                "or configure it in your Streamlit secrets."
            )
        client = Groq(api_key=api_key)
    return client


def generate_itinerary(destination, days):

    prompt = f"""
    Create a {days}-day itinerary for {destination}.
    """

    completion = get_client().chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return completion.choices[0].message.content