from datetime import datetime
from tkinter import ttk
import tkinter as tk


class ChatDisplay(ttk.Frame):
    """Chat display area with title and messages"""

    def __init__(self, parent):
        super().__init__(parent)
        self.configure(style='TFrame')
        self.pending_sql_queries = []  # Track SQL for next button
        self.create_widgets()

    def create_widgets(self):
        """Create the display widgets"""

        # header
        self.header()

        # chat container
        self.chat_container()

    def header(self):

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

    def chat_container(self):

        # Chat area with canvas and scrollbar
        chat_frame = ttk.Frame(self)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Canvas for chat messages
        self.canvas = tk.Canvas(
            chat_frame,
            bg="#f8f9fa",
            highlightthickness=1,
            highlightbackground="#495057",
            highlightcolor="#495057"
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

    def update_status_check_api_ai(self, status: dict):
        """Update the status indicator based on API status"""

        color_status, msg_status = status

        self.status_indicator.config(foreground=color_status)
        self.status_label.config(text=msg_status)

    def add_message(self, sender: dict, message: str):
        """Add a message to the chat display with bubble styling"""

        timestamp = datetime.now().strftime("%H:%M")
        # Container for message alignment
        msg_container = tk.Frame(self.scrollable_frame, bg="#f8f9fa")
        msg_container.pack(fill=tk.X, padx=10, pady=5)

        # Bubble frame
        bubble_frame = tk.Frame(
            msg_container,
            bg=sender["bg"],
            relief=tk.RAISED,
            bd=sender["bd"],
            highlightbackground=sender["highlightbackground"],
            highlightthickness=sender["highlightthickness"]
        )
        bubble_frame.pack(
            side=tk.RIGHT if sender["side"] == "right" else tk.LEFT,
            anchor=sender["anchor"],
            padx=sender["padx"]
        )

        header_label = tk.Label(
            bubble_frame,
            text=f"{sender['header_icon']} {sender['sender']}  •  {timestamp}",
            font=("Segoe UI", 9, "bold"),
            bg=sender["bg"],
            fg=sender["header_fg"]
        )
        header_label.pack(anchor="w", padx=15, pady=(10, 5))

        # Message text
        msg_label = tk.Label(
            bubble_frame,
            text=message,
            font=("Segoe UI", 11),
            bg=sender["bg"],
            fg=sender["fg"],
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
