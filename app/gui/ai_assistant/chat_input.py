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

    def __init__(self, parent, on_send_question_callback):
        super().__init__(parent)
        self.configure(style='TFrame')

        # Callbacks
        self.on_send_question_callback = on_send_question_callback

        # State
        self.is_processing = False

        self.create_widgets()

    def create_widgets(self):
        """Create the input widgets"""

        self.display_quick_questions()
        self.display_input_question()


    def display_quick_questions(self):

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


    def display_input_question(self):

        input_frame = tk.Frame(
            self,
            highlightbackground="#495057",
            highlightthickness=1,
            highlightcolor="#495057",
            bg="#f8f9fa",
            padx=5,
            pady=5
        )
        input_frame.pack(fill=tk.X)

        # Question input
        self.placeholder_text = "Escribe tu pregunta aquí..."
        self.question_entry = ttk.Entry(
            input_frame,
            font=("Segoe UI", 11),
            foreground="#999999"
        )
        self.question_entry.insert(0, self.placeholder_text)
        self.question_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.question_entry.bind("<Return>", lambda e: self.send_question())
        self.question_entry.bind("<FocusIn>", self._on_focus_in)
        self.question_entry.bind("<FocusOut>", self._on_focus_out)

        # Send button
        self.send_button = ttk_boot.Button(
            input_frame,
            text="Preguntar",
            bootstyle="success",
            command=self.send_question,
            width=12
        )
        self.send_button.pack(side=tk.LEFT)


    def use_quick_question(self, question: str):
        self.question_entry.delete(0, tk.END)
        self.question_entry.configure(foreground="")
        self.question_entry.insert(0, question)
        self.send_question()

    def send_question(self):
        question = self.question_entry.get().strip()

        if not question:
            return

        if self.on_send_question_callback:
            self.on_send_question_callback(question)

    def clear_input(self):
        self.question_entry.delete(0, tk.END)
        self._show_placeholder()

    def get_question(self):
        """Get current question text"""
        text = self.question_entry.get().strip()
        if text == self.placeholder_text:
            return ""
        return text

    def _on_focus_in(self, event):
        if self.question_entry.get() == self.placeholder_text:
            self.question_entry.delete(0, tk.END)
            self.question_entry.configure(foreground="")

    def _on_focus_out(self, event):
        if not self.question_entry.get().strip():
            self._show_placeholder()

    def _show_placeholder(self):
        self.question_entry.delete(0, tk.END)
        self.question_entry.configure(foreground="#999999")
        self.question_entry.insert(0, self.placeholder_text)

    def set_processing(self, is_processing: bool):
        self.is_processing = is_processing
        
        if is_processing:
            self.send_button.config(state=tk.DISABLED, text="Pensando...")
            self.question_entry.config(state=tk.DISABLED)
        else:
            self.send_button.config(state=tk.NORMAL, text="Preguntar")
            self.question_entry.config(state=tk.NORMAL)
