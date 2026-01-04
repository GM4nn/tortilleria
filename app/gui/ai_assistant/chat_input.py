"""
AI Assistant Module - Chat Input Area
Contains quick questions and input field
"""
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk_boot
from ttkbootstrap.constants import *

from app.constants import QUICK_QUESTIONS


class ChatInput(ttk.Frame):

    def __init__(self, parent, on_send_callback, on_quick_question_callback):
        super().__init__(parent)
        self.configure(style='TFrame')

        # Callbacks
        self.on_send_callback = on_send_callback
        self.on_quick_question_callback = on_quick_question_callback

        # State
        self.is_processing = False

        self.create_widgets()

    def create_widgets(self):
        """Create the input widgets"""

        # Quick questions
        quick_frame = ttk.Labelframe(
            self,
            text="Preguntas Rápidas",
            padding=10
        )
        quick_frame.pack(fill=tk.X, pady=(0, 15))

        for i, question in enumerate(QUICK_QUESTIONS):
            btn = ttk_boot.Button(
                quick_frame,
                text=question,
                bootstyle="info-outline",
                command=lambda q=question: self.use_quick_question(q)
            )
            btn.pack(side=tk.LEFT, padx=5) if i < 2 else btn.pack(side=tk.LEFT, padx=5, pady=(5, 0))

        # Input area
        input_frame = ttk.Frame(self)
        input_frame.pack(fill=tk.X)

        # Question input
        self.question_entry = ttk.Entry(
            input_frame,
            font=("Segoe UI", 11)
        )
        self.question_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.question_entry.bind("<Return>", lambda e: self.send_question())

        # Send button
        self.send_button = ttk_boot.Button(
            input_frame,
            text="Preguntar",
            bootstyle="success",
            command=self.send_question,
            width=12
        )
        self.send_button.pack(side=tk.LEFT)

        # Clear button
        clear_button = ttk_boot.Button(
            input_frame,
            text="Limpiar",
            bootstyle="secondary-outline",
            command=self.clear_input,
            width=10
        )
        clear_button.pack(side=tk.LEFT, padx=(5, 0))

    def use_quick_question(self, question: str):

        self.question_entry.delete(0, tk.END)
        self.question_entry.insert(0, question)

        if self.on_quick_question_callback:
            self.on_quick_question_callback(question)

    def send_question(self):
        question = self.question_entry.get().strip()

        if not question:
            return

        if self.on_send_callback:
            self.on_send_callback(question)

    def clear_input(self):
        self.question_entry.delete(0, tk.END)

    def get_question(self):
        """Get current question text"""
        return self.question_entry.get().strip()

    def set_processing(self, is_processing: bool):
        self.is_processing = is_processing
        if is_processing:
            self.send_button.config(state=tk.DISABLED, text="Pensando...")
        else:
            self.send_button.config(state=tk.NORMAL, text="Preguntar")
