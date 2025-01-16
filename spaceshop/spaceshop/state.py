import reflex as rx
from datetime import datetime
from pinecone import Pinecone, Index
from langchain_openai import OpenAIEmbeddings
from config import PINECONE_API_KEY, OPENAI_API_KEY
from openai import OpenAI
import asyncio
from langchain import hub
from langchain.schema import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

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
        "display": "flex",
        "flex_direction": "column",
        "color": TEXT_COLOR,
        "font_family": "Space Mono, monospace",
    },
    "title": {
        "color": GLOW_COLOR,
        "text_align": "center",
        "font_size": "2.5em",
        "margin_top": "1em",
        "text_shadow": f"0 0 10px {GLOW_COLOR}",
    },
    "subtitle": {
        "color": TEXT_COLOR,
        "text_align": "center",
        "font_size": "1.2em",
        "margin_bottom": "2em",
        "opacity": "0.8",
    },
    "chat_container": {
        "flex": "1",
        "overflow_y": "auto",
        "padding": "2em",
        "margin_bottom": "80px",  # Add space for input container
    },
    "input_container": {
        "position": "fixed",
        "bottom": "0",
        "left": "0",
        "width": "100%",
        "background": SPACE_BLUE,
        "padding": "1em",
        "border_top": f"1px solid {ACCENT_BLUE}",
        "z_index": "1000",
    },
    "input": {
        "width": "100%",
        "padding": "1em",
        "background": ACCENT_BLUE,
        "border": f"1px solid {GLOW_COLOR}",
        "border_radius": "5px",
        "color": TEXT_COLOR,
        "font_size": "1.2em",
        "min_height": "100px",  # Increased height
        "resize": "vertical",   # Allow vertical resizing
    },
    "button": {
        "background": GLOW_COLOR,
        "color": DARK_BLUE,
        "padding": "1em 2em",
        "border_radius": "5px",
        "margin_left": "1em",
        "_hover": {"opacity": 0.8},
    },
    "loading": {
        "position": "fixed",
        "top": "50%",
        "left": "50%",
        "transform": "translate(-50%, -50%)",
        "background": f"rgba(27, 38, 59, 0.9)",  # SPACE_BLUE with opacity
        "padding": "2em",
        "border_radius": "15px",
        "text_align": "center",
        "z_index": "2000",
        "backdrop_filter": "blur(4px)",
    }
}

class Message(rx.Base):
    text: str
    is_user: bool = False
    moon_name: str = ""
    source_url: str = ""

class State(rx.State):
    messages: list[Message] = []
    current_time: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    system_status: str = "ONLINE"
    processing: bool = False
    current_input: str = ""

    @rx.event(background=True)
    async def update_time_periodically(self):
        while True:
            async with self:
                self.current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            await asyncio.sleep(1)

    def format_response(self, results) -> str:
        if not results.matches:
            return "I couldn't find any relevant information about that in my database. Try asking about specific moons or their features!"

        # Group results by moon
        moon_info = {}
        for match in results.matches:
            moon_name = match.metadata['moon_name']
            if moon_name not in moon_info:
                moon_info[moon_name] = []
            moon_info[moon_name].append({
                'title': match.metadata['title'],
                'content': match.metadata['Document Content'],
                'source': match.metadata['source']
            })

        # Format response
        response = "🛸 Here's what I found about Jupiter's moons:\n\n"
        for moon, info_list in moon_info.items():
            response += f"About {moon}:\n"
            for info in info_list:
                enhanced_text = self.enhance_text_with_openai(
                    f"{info['title']}: {info['content']}"
                )
                response += f"• {enhanced_text}\n"
            response += "\n"

        return response

    def enhance_text_with_openai(self, text: str) -> str:
        client = OpenAI()

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a space expert providing concise, engaging information about Jupiter's moons. Keep responses brief but informative, focusing on the most interesting aspects. Avoid mentioning sources or references."
                    },
                    {
                        "role": "user", 
                        "content": f"Transform this information into a brief, engaging description:\n\n{text}"
                    }
                ],
                max_tokens=100,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error enhancing text with OpenAI: {e}")
            return text

    def query_database(self, query_text: str) -> str:
        try:
            print("Initializing components...")
            
            # Initialize embeddings with new syntax
            embeddings = OpenAIEmbeddings()
            
            # Initialize Pinecone
            pc = Pinecone(
                api_key=PINECONE_API_KEY,
                environment="gcp-starter"
            )
            index = pc.Index("jupiter-moons")
            
            # Create retriever function
            def retrieve_docs(query):
                query_embedding = embeddings.embed_query(query)
                results = index.query(
                    vector=query_embedding,
                    top_k=3,
                    include_metadata=True
                )
                return [
                    Document(
                        page_content=f"{match.metadata['moon_name']}: {match.metadata['Document Content']}",
                        metadata=match.metadata
                    )
                    for match in results.matches
                ]

            # Create prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful assistant that provides information about Jupiter's moons."),
                ("human", "Question: {question}"),
                ("human", "Context: {context}")
            ])

            # Initialize the LLM with new syntax
            llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.7,
            )

            # Create the chain
            chain = (
                {"context": retrieve_docs, "question": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser()
            )

            # Execute the chain
            return chain.invoke(query_text)

        except Exception as e:
            print(f"Detailed error in query_database: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"I encountered an error while searching the database: {str(e)}"

    def format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def handle_input_change(self, value: str):
        self.current_input = value

    async def handle_submit(self, key_event=None):
        # Check if this is a keyboard event and not Enter key
        if isinstance(key_event, dict) and key_event.get("key") != "Enter":
            return
        
        if not self.current_input.strip():
            return

        user_message = self.current_input
        self.messages.append(Message(
            text=user_message,
            is_user=True
        ))
        
        self.current_input = ""
        self.processing = True

        try:
            response = self.query_database(user_message)
            self.messages.append(Message(
                text=response,
                is_user=False
            ))
        except Exception as e:
            error_msg = f"I encountered an error while searching the database: {str(e)}"
            self.messages.append(Message(text=error_msg))

        self.processing = False
