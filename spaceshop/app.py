import reflex as rx
from datetime import datetime
import random

# Styles for our space dashboard
DARK_BLUE = "#0d1b2a"
SPACE_BLUE = "#1b263b"
ACCENT_BLUE = "#415a77"
TEXT_COLOR = "#e0e1dd"
GLOW_COLOR = "#48cae4"

styles = {
    "dashboard": {
        "background": DARK_BLUE,
        "min_height": "100vh",
        "padding": "2em",
        "color": TEXT_COLOR,
        "font_family": "Space Mono, monospace",
    },
    "terminal": {
        "background": SPACE_BLUE,
        "border_radius": "10px",
        "padding": "2em",
        "box_shadow": f"0 0 20px {GLOW_COLOR}",
        "margin_bottom": "2em",
    },
    "input": {
        "width": "100%",
        "padding": "1em",
        "background": ACCENT_BLUE,
        "border": f"1px solid {GLOW_COLOR}",
        "border_radius": "5px",
        "color": TEXT_COLOR,
        "margin_top": "1em",
    },
    "header": {
        "color": GLOW_COLOR,
        "text_align": "center",
        "margin_bottom": "1em",
        "text_shadow": f"0 0 10px {GLOW_COLOR}",
    },
    "status": {
        "display": "flex",
        "justify_content": "space-between",
        "margin_bottom": "1em",
    }
}

class Message(rx.Base):
    text: str
    is_user: bool = False

class State(rx.State):
    messages: list[Message] = []
    current_time: str = datetime.now().strftime("%H:%M:%S")
    system_status: str = "ONLINE"
    
    def add_message(self, message: str, is_user: bool = False):
        self.messages.append(Message(text=message, is_user=is_user))
        
        if is_user:
            # Here we'll later add the actual query to Pinecone
            response = "Analyzing Jupiter's moons database... [Placeholder response]"
            self.add_message(response)

def index():
    return rx.box(
        rx.vstack(
            # Header
            rx.heading("JUPITER MOONS NAVIGATION SYSTEM", style=styles["header"]),
            
            # Status Bar
            rx.box(
                rx.hstack(
                    rx.text(f"System Status: {State.system_status}"),
                    rx.text(f"Stardate: {State.current_time}"),
                    rx.text("Location: Jupiter Orbital Zone"),
                ),
                style=styles["status"]
            ),
            
            # Main Terminal
            rx.box(
                rx.vstack(
                    *[
                        rx.box(
                            rx.text(
                                f"{'> ' if message.is_user else '🛸 '}{message.text}",
                                color=GLOW_COLOR if message.is_user else TEXT_COLOR,
                            ),
                            width="100%",
                        )
                        for message in State.messages
                    ],
                    align_items="start",
                ),
                style=styles["terminal"]
            ),
            
            # Input Area
            rx.input(
                placeholder="Query the Jupiter Moons Database...",
                on_submit=lambda value: State.add_message(value, is_user=True),
                style=styles["input"]
            ),
            
            spacing="4",
            width="100%",
            max_width="800px",
            margin="0 auto",
        ),
        style=styles["dashboard"]
    )

app = rx.App()
app.add_page(index)
