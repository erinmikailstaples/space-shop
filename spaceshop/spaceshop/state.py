import reflex as rx
from datetime import datetime
from pinecone import Pinecone, Index
from langchain.embeddings.openai import OpenAIEmbeddings
from config import PINECONE_API_KEY, OPENAI_API_KEY

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
    moon_name: str = ""
    source_url: str = ""

class State(rx.State):
    messages: list[Message] = []
    current_time: str = datetime.now().strftime("%H:%M:%S")
    system_status: str = "ONLINE"
    processing: bool = False
    current_input: str = ""

    def format_response(self, results) -> str:
        if not results.matches:
            return "I couldn't find any relevant information about that in my database. Try asking about specific moons or their features!"

        response = "🛸 Based on my analysis of Jupiter's moons:\n\n"
        for match in results.matches:
            metadata = match.metadata
            response += f"• About {metadata['moon_name']}: {metadata['title']}\n"
            response += f"{metadata['Document Content']}\n"
            response += f"Source: {metadata['source']}\n\n"
        
        return response

    def query_database(self, query_text: str) -> str:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index("jupiter-moons")
        embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
        
        query_embedding = embeddings.embed_query(query_text)
        
        results = index.query(
            vector=query_embedding,
            top_k=3,
            include_metadata=True
        )
        
        return self.format_response(results)

    def handle_input_change(self, value: str):
        self.current_input = value

    async def handle_submit(self, _):
        if not self.current_input.strip():
            return

        # Store the user's message
        user_message = self.current_input
        self.messages.append(Message(
            text=user_message,
            is_user=True
        ))
        
        # Clear input and show processing
        self.current_input = ""
        self.processing = True

        try:
            # Get response from database
            response = self.query_database(user_message)
            
            # Add system response
            self.messages.append(Message(
                text=response,
                is_user=False
            ))
        except Exception as e:
            error_msg = f"I encountered an error while searching the database: {str(e)}"
            self.messages.append(Message(text=error_msg))
        
        self.processing = False
