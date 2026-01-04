"""
AI Assistant Module - Chat Display Area
Contains title, status indicator and message display
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime


class ChatDisplay(ttk.Frame):
    """Chat display area with title and messages"""

    def __init__(self, parent):
        super().__init__(parent)
        self.configure(style='TFrame')
        self.pending_sql_queries = []  # Track SQL for next button
        self.create_widgets()

    def create_widgets(self):
        """Create the display widgets"""

        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = ttk.Label(
            header_frame,
            text="🤖 Asistente Inteligente",
            font=("Segoe UI", 20, "bold")
        )
        title_label.pack(side=tk.LEFT)

        # Status indicator
        self.status_frame = ttk.Frame(header_frame)
        self.status_frame.pack(side=tk.RIGHT)

        self.status_indicator = ttk.Label(
            self.status_frame,
            text="●",
            font=("Segoe UI", 16),
            foreground="gray"
        )
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 5))

        self.status_label = ttk.Label(
            self.status_frame,
            text="Verificando...",
            font=("Segoe UI", 10)
        )
        self.status_label.pack(side=tk.LEFT)

        # Subtitle with mode indicator
        subtitle_frame = ttk.Frame(self)
        subtitle_frame.pack(fill=tk.X, pady=(0, 10))

        subtitle = ttk.Label(
            subtitle_frame,
            text="Pregunta sobre ventas, gastos, productos, clientes y proveedores",
            font=("Segoe UI", 11),
            foreground="gray"
        )
        subtitle.pack(side=tk.LEFT)

        # Mode indicator
        self.mode_label = ttk.Label(
            subtitle_frame,
            text="[Modo: SQL Directo ✓]",
            font=("Segoe UI", 9, "bold"),
            foreground="#28a745"
        )
        self.mode_label.pack(side=tk.RIGHT, padx=(10, 0))

        # Chat area with canvas and scrollbar
        chat_frame = ttk.Frame(self)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Canvas for chat messages
        self.canvas = tk.Canvas(
            chat_frame,
            bg="#f8f9fa",
            highlightthickness=0
        )
        self.scrollbar = ttk.Scrollbar(chat_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f8f9fa")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", tags="frame")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind canvas width to scrollable frame
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Enable mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_canvas_configure(self, event):
        """Update scrollable frame width when canvas is resized"""
        canvas_width = event.width
        self.canvas.itemconfig("frame", width=canvas_width)

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _scroll_to_bottom(self):
        """Scroll to the bottom of the chat"""
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def update_status(self, status: dict):
        """Update the status indicator based on API status"""

        status_type = status.get("status", "error")

        if status_type == "ready":
            self.status_indicator.config(foreground="#28a745")  # Green
            self.status_label.config(text="Listo")

        elif status_type == "invalid_key":
            self.status_indicator.config(foreground="#dc3545")  # Red
            self.status_label.config(text="Error")

        else:
            self.status_indicator.config(foreground="#6c757d")  # Gray
            self.status_label.config(text="Error")

    def add_message(self, sender: str, message: str, tag: str):
        """Add a message to the chat display with bubble styling"""
        
        timestamp = datetime.now().strftime("%H:%M")

        # Container for message alignment
        msg_container = tk.Frame(self.scrollable_frame, bg="#f8f9fa")
        msg_container.pack(fill=tk.X, padx=10, pady=5)

        # Message bubble frame
        if tag == "user":

            # User messages on the right with blue background
            bubble_frame = tk.Frame(
                msg_container,
                bg="#0066cc",
                relief=tk.RAISED,
                bd=1,
                highlightbackground="#0052a3",
                highlightthickness=1
            )
            bubble_frame.pack(side=tk.RIGHT, anchor="e", padx=(100, 5))

            # Timestamp
            time_label = tk.Label(
                bubble_frame,
                text=timestamp,
                font=("Segoe UI", 8),
                bg="#0066cc",
                fg="#e6f2ff"
            )
            time_label.pack(anchor="e", padx=15, pady=(10, 2))

            # Message text
            msg_label = tk.Label(
                bubble_frame,
                text=message,
                font=("Segoe UI", 11),
                bg="#0066cc",
                fg="white",
                wraplength=400,
                justify=tk.LEFT
            )
            msg_label.pack(anchor="w", padx=15, pady=(0, 10))

        elif tag == "assistant":

            # Assistant messages on the left with light gray background
            bubble_frame = tk.Frame(
                msg_container,
                bg="white",
                relief=tk.RAISED,
                bd=1,
                highlightbackground="#dee2e6",
                highlightthickness=1
            )
            bubble_frame.pack(side=tk.LEFT, anchor="w", padx=(5, 100))

            # Sender + Timestamp
            header_label = tk.Label(
                bubble_frame,
                text=f"🤖 {sender}  •  {timestamp}",
                font=("Segoe UI", 9, "bold"),
                bg="white",
                fg="#28a745"
            )
            header_label.pack(anchor="w", padx=15, pady=(10, 5))

            # Message text
            msg_label = tk.Label(
                bubble_frame,
                text=message,
                font=("Segoe UI", 11),
                bg="white",
                fg="#212529",
                wraplength=400,
                justify=tk.LEFT
            )
            msg_label.pack(anchor="w", padx=15, pady=(0, 10))

        elif tag == "error":
            # Error messages on the left with red background
            bubble_frame = tk.Frame(
                msg_container,
                bg="#f8d7da",
                relief=tk.RAISED,
                bd=1,
                highlightbackground="#dc3545",
                highlightthickness=1
            )
            bubble_frame.pack(side=tk.LEFT, anchor="w", padx=(5, 100))

            header_label = tk.Label(
                bubble_frame,
                text=f"❌ {sender}  •  {timestamp}",
                font=("Segoe UI", 9, "bold"),
                bg="#f8d7da",
                fg="#dc3545"
            )
            header_label.pack(anchor="w", padx=15, pady=(10, 5))

            msg_label = tk.Label(
                bubble_frame,
                text=message,
                font=("Segoe UI", 11),
                bg="#f8d7da",
                fg="#721c24",
                wraplength=400,
                justify=tk.LEFT
            )
            msg_label.pack(anchor="w", padx=15, pady=(0, 10))

        self._scroll_to_bottom()

    def add_system_message(self, message: str):        
        msg_container = tk.Frame(self.scrollable_frame, bg="#f8f9fa")
        msg_container.pack(fill=tk.X, padx=10, pady=5)

        system_label = tk.Label(
            msg_container,
            text=message,
            font=("Segoe UI", 10, "italic"),
            bg="#f8f9fa",
            fg="#6c757d",
            wraplength=500,
            justify=tk.CENTER
        )
        system_label.pack(anchor="center")

        self._scroll_to_bottom()

    def add_sql_debug_button(self, sql_queries: list):

        msg_container = tk.Frame(self.scrollable_frame, bg="#f8f9fa")
        msg_container.pack(fill=tk.X, padx=10, pady=2)

        def show_sql():
            sql_text = "\n\n".join([f"Query {i+1}:\n{query}" for i, query in enumerate(sql_queries)])
            self.add_system_message(f"📝 SQL ejecutada:\n{sql_text}")

        sql_button = tk.Button(
            msg_container,
            text=f"[Ver SQL ejecutada ({len(sql_queries)} query{'s' if len(sql_queries) > 1 else ''})]",
            font=("Segoe UI", 9),
            fg="#0066cc",
            bg="#f8f9fa",
            relief=tk.FLAT,
            cursor="hand2",
            command=show_sql,
            bd=0,
            activeforeground="#0052a3",
            activebackground="#f8f9fa"
        )
        sql_button.pack(side=tk.LEFT, padx=(10, 0))

        self._scroll_to_bottom()

    def clear(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.add_system_message("Chat limpiado. ¡Haz una nueva pregunta!")
