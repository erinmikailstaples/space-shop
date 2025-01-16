import reflex as rx
from datetime import datetime
from pinecone import Pinecone, Index
from langchain_openai import OpenAIEmbeddings
from config import PINECONE_API_KEY, OPENAI_API_KEY
from openai import OpenAI

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
        "max_height": "80vh",
        "overflow_y": "auto",
    },
    "input": {
        "width": "100%",
        "padding": "1em",
        "background": ACCENT_BLUE,
        "border": f"1px solid {GLOW_COLOR}",
        "border_radius": "5px",
        "color": TEXT_COLOR,
        "margin_top": "1em",
        "margin_bottom": "2em",
        "font_size": "1.2em", 
        "height": "3em", 
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
            moon_name = metadata.get('moon_name', 'Unknown Moon')
            title = metadata.get('title', 'No Title Available')
            document_content = metadata.get('Document Content', 'No Content Available')
            source = metadata.get('source', 'No Source Available')

            # Construct the text to be enhanced
            text_to_enhance = f"About {moon_name}: {title}. {document_content}"
            
            # Call OpenAI API to enhance the text
            enhanced_text = self.enhance_text_with_openai(text_to_enhance)
            
            response += f"{enhanced_text}\n"
            response += f"Source: {source}\n\n"

        return response

    def enhance_text_with_openai(self, text: str) -> str:
        client = OpenAI(api_key=OPENAI_API_KEY)

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides clear, concise information about Jupiter's moons."},
                    {"role": "user", "content": f"Enhance the following text to make it more engaging and informative:\n\n{text}"}
                ],
                max_tokens=150,
                temperature=0.7
            )
            enhanced_text = response.choices[0].message.content.strip()
            return enhanced_text
        except Exception as e:
            print(f"Error enhancing text with OpenAI: {e}")
            return text

    def query_database(self, query_text: str) -> str:
        try:
            pc = Pinecone(api_key=PINECONE_API_KEY)
            index = pc.Index("jupiter-moons")
            embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
            
            query_embedding = embeddings.embed_query(query_text)
            
            results = index.query(
                vector=query_embedding,
                top_k=3,
                include_metadata=True
            )
            
            print("Query Results:", results)  # Debugging line
            
            return self.format_response(results)
        except Exception as e:
            print(f"Error querying database: {e}")
            return f"I encountered an error while searching the database: {str(e)}"

    def handle_input_change(self, value: str):
        self.current_input = value

    async def handle_submit(self):
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
