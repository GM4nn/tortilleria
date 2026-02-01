"""
AI Assistant Module - Main Content
Provides a chat interface to ask business questions
"""
import tkinter as tk
from tkinter import ttk
import threading

from app.constants import ASISTANT_SENDER, ERROR_SENDER, YOU_SENDER
from app.services.ai_assistant_mcp import ai_assistant_mcp
from app.data.providers.ia import ia_provider
from app.gui.ai_assistant.chat_display import ChatDisplay
from app.gui.ai_assistant.chat_input import ChatInput
from app import api_key


class AIAssistantContent(ttk.Frame):
    """AI Assistant chat interface"""

    def __init__(self, parent):
        super().__init__(parent)
        self.configure(style='TFrame')

        # State
        self.is_processing = False
        self.api_key_visible = False

        self.create_widgets()
        self.load_api_key()
        self.check_claude_on_startup()

    def create_widgets(self):
        """Create the chat interface"""

        # Main container
        main_container = ttk.Frame(self, padding=20)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Config Api Key AI
        self.config_api_ai(main_container)

        # Chat display component (title, status, messages)
        self.display = ChatDisplay(main_container)
        self.display.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Chat input component (quick questions, input field)
        self.input = ChatInput(
            main_container,
            on_send_question_callback=self.send_question
        )
        self.input.pack(fill=tk.X)


    def config_api_ai(self, main_container):

        # Top bar with config button
        top_bar = ttk.Frame(main_container)
        top_bar.pack(fill=tk.X, pady=(0, 10))

        # Config button (gear icon)
        self.config_btn = ttk.Button(
            top_bar,
            text="⚙️",
            width=3,
            command=self.toggle_api_key_input
        )
        self.config_btn.pack(side=tk.RIGHT)

        # API Key input frame (initially hidden)
        self.api_key_frame = ttk.Frame(main_container)

        ttk.Label(self.api_key_frame, text="Clave para el asistente:").pack(side=tk.LEFT, padx=(0, 5))

        self.api_key_entry = ttk.Entry(self.api_key_frame, width=40, show="*")
        self.api_key_entry.pack(side=tk.LEFT, padx=5)
        self.api_key_entry.bind("<Return>", lambda e: self.save_api_key())

        ttk.Button(
            self.api_key_frame,
            text="Guardar",
            command=self.save_api_key
        ).pack(side=tk.LEFT, padx=5)


    def toggle_api_key_input(self):

        """Show/hide API key input field"""

        if self.api_key_visible:
            self.api_key_frame.pack_forget()
            self.api_key_visible = False
        else:
            self.api_key_frame.pack(fill=tk.X, pady=(15, 0))
            self.api_key_entry.focus()
            self.api_key_visible = True


    def load_api_key(self):
        """Load API key from database on startup"""
        saved_key = ia_provider.get_api_key()
        if saved_key:
            api_key.API_KEY = saved_key

    def save_api_key(self):
        """Save the API key to database and global variable"""

        key = self.api_key_entry.get().strip()
        if key:

            api_key.API_KEY = key
            ia_provider.save_api_key(key)

            self.api_key_frame.pack_forget()
            self.api_key_visible = False
            self.api_key_entry.delete(0, tk.END)
            self.display.add_system_message("✅ API Key configurada correctamente")
            self.check_claude_on_startup()

    def check_claude_on_startup(self):
        
        def check():

            # Use MCP status check
            status = ai_assistant_mcp.check_status()
            self.after(0, self.display.update_status_check_api_ai, status)

        thread = threading.Thread(target=check, daemon=True)
        thread.start()

    def send_question(self, question: str = None):

        if question is None:
            question = self.input.get_question()

        if not question:
            return

        if self.is_processing:
            self.display.add_system_message("⏳ Esperando respuesta anterior...")
            return

        self.input.clear_input()

        self.display.add_message(YOU_SENDER, question)

        self.is_processing = True
        self.input.set_processing(True)

        # Process in background thread
        def process():
            try:

                result = ai_assistant_mcp.ask(question)
                
                # MCP returns dict with response and sql_queries
                if isinstance(result, dict):
                    response_text = result.get("response", "Error desconocido")

                    if result.get("success", False):
                        self.after(0, self.display_response, response_text)
                    else:
                        self.after(0, self.display_error, response_text)
                else:
                    self.after(0, self.display_response, result)
            
            except Exception as e:
                self.after(0, self.display_error, str(e))

        thread = threading.Thread(target=process, daemon=True)
        thread.start()

    def display_response(self, response: str):

        self.display.add_message(ASISTANT_SENDER, response)

        self.is_processing = False
        self.input.set_processing(False)

    def display_error(self, error: str):
        
        self.display.add_message(ERROR_SENDER, error)
        self.is_processing = False
        self.input.set_processing(False)
