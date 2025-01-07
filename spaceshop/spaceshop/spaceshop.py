import reflex as rx
from datetime import datetime
from pinecone import Index
from langchain_openai import OpenAIEmbeddings
from config import PINECONE_API_KEY, OPENAI_API_KEY

# Import our existing styles
from .state import (
    DARK_BLUE, SPACE_BLUE, ACCENT_BLUE, TEXT_COLOR, GLOW_COLOR,
    styles, Message, State
)

def index() -> rx.Component:
    return rx.box(
        rx.vstack(
            # Header
            rx.heading("JUPITER MOONS NAVIGATION SYSTEM", style=styles["header"]),
            
            # Status Bar
            rx.box(
                rx.hstack(
                    rx.text(f"System Status: {State.system_status}"),
                    rx.text(f"Stardate: {State.current_time}"),
                ),
                style=styles["status"]
            ),
            
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
                            margin_bottom="0.5em",
                        )
                    ),
                    align_items="start",
                    width="100%",
                    overflow_y="auto",
                    max_height="60vh",
                ),
                style=styles["terminal"]
            ),
            
            # Input area
            rx.hstack(
                rx.input(
                    value=State.current_input,
                    placeholder="Ask about Jupiter's moons...",
                    on_change=State.handle_input_change,
                    is_disabled=State.processing,
                    style=styles["input"]
                ),
                rx.button(
                    "Send",
                    on_click=State.handle_submit,
                    is_disabled=State.processing,
                    background=GLOW_COLOR,
                    color=DARK_BLUE,
                    _hover={"opacity": 0.8}
                ),
            ),
            rx.cond(State.processing, rx.spinner(), None),
            
            spacing="4",
            width="100%",
            max_width="800px",
            margin="0 auto",
        ),
        style=styles["dashboard"]
    )

# Add state and page to the app
app = rx.App()
app.add_page(index)
