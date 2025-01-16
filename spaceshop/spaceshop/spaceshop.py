import reflex as rx
from datetime import datetime
from pinecone import Index
from langchain_community.embeddings import OpenAIEmbeddings
from config import PINECONE_API_KEY, OPENAI_API_KEY

# Import our existing styles
from .state import (
    DARK_BLUE, SPACE_BLUE, ACCENT_BLUE, TEXT_COLOR, GLOW_COLOR,
    styles, Message, State
)

def index() -> rx.Component:
    return rx.box(
        # Chat messages display
        rx.box(
            rx.vstack(
                rx.foreach(
                    State.messages,
                    lambda message: rx.box(
                        rx.text(
                            rx.cond(
                                message.is_user,
                                f"You: {message.text}",
                                f"🛸 AI: {message.text}"
                            ),
                            color=rx.cond(message.is_user, GLOW_COLOR, TEXT_COLOR),
                        ),
                        width="100%",
                        padding="1em",
                        border_radius="8px",
                        background=rx.cond(message.is_user, ACCENT_BLUE, SPACE_BLUE),
                        margin_bottom="1em",
                    )
                ),
                align_items="start",
                width="100%",
                height="100%",
            ),
            style=styles["chat_container"]
        ),
        
        # Input area
        rx.box(
            rx.hstack(
                rx.input(
                    value=State.current_input,
                    placeholder="Ask about Jupiter's moons...",
                    on_change=State.handle_input_change,
                    on_key_down=State.handle_submit,
                    is_disabled=State.processing,
                    style=styles["input"]
                ),
                rx.button(
                    "Send",
                    on_click=State.handle_submit,
                    is_disabled=State.processing,
                    style=styles["button"]
                ),
                width="100%",
                max_width="1200px",
                margin="0 auto",
            ),
            style=styles["input_container"]
        ),
        style=styles["dashboard"]
    )

# Add state and page to the app
app = rx.App()
app.add_page(index)
