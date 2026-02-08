
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app.constants import CUSTOMER_CATEGORIES
from app.data.providers.customers import customer_provider


class ShoppingCar(ttk.Frame):
    def __init__(self, parent, app, content):
        super().__init__(parent, width=350)
        self.app = app
        self.content = content

        self.setup_ui()
    
    def setup_ui(self):
        """Configure right panel interface"""
        
        # Header Section
        self.section_total_price()
        
        # Frame with scrollbar to shopping car items
        self.section_shopping_car_items()
        
        # Action Buttons
        self.action_buttons()


    def section_total_price(self):

        title = ttk.Label(
            self,
            text="🛒 CARRITO",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=10)
        
        # Total frame (above)
        self.frame_total = ttk.Frame(
            self,
            bootstyle="dark",
            relief="solid",
            borderwidth=2
        )
        self.frame_total.pack(fill=X, padx=10, pady=10)
        
        ttk.Label(
            self.frame_total,
            text="TOTAL",
            font=("Arial", 12),
            bootstyle="inverse-dark"
        ).pack(pady=(10, 0))
        
        self.lbl_total = ttk.Label(
            self.frame_total,
            text="$0.00",
            font=("Arial", 36, "bold"),
            bootstyle="inverse-dark"
        )
        self.lbl_total.pack(pady=(5, 10))


    def section_shopping_car_items(self):
        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.pack(fill=BOTH, expand=YES, padx=10)

        self._create_canvas()


    def _create_canvas(self):
        """Create or recreate the canvas with scrollbar"""

        # Canvas and scrollbar
        self.canvas = ttk.Canvas(self.canvas_frame, highlightthickness=0, borderwidth=0)
        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient=VERTICAL, command=self.canvas.yview)

        self.scrollable_frame = ttk.Frame(self.canvas)

        self.canvas_window = self.canvas.create_window(0, 0, window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Update scroll region properly
        def _on_frame_configure(event):
            # Get the bounding box of all content
            bbox = self.canvas.bbox("all")
            if bbox:
                # Only allow scrolling if content is taller than canvas
                canvas_height = self.canvas.winfo_height()
                content_height = bbox[3]  # bbox is (x1, y1, x2, y2)

                if content_height > canvas_height:
                    # Content is larger, allow scrolling
                    self.canvas.configure(scrollregion=bbox)
                else:
                    # Content is smaller, set scrollregion to canvas size to prevent scroll
                    self.canvas.configure(scrollregion=(0, 0, bbox[2], canvas_height))

        self.scrollable_frame.bind("<Configure>", _on_frame_configure)

        # Adjust scrollable_frame width to canvas
        def _on_canvas_configure(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)

            # Also update scrollregion when canvas resizes
            bbox = self.canvas.bbox("all")
            if bbox:
                canvas_height = event.height
                content_height = bbox[3]
                if content_height > canvas_height:
                    self.canvas.configure(scrollregion=bbox)
                else:
                    self.canvas.configure(scrollregion=(0, 0, bbox[2], canvas_height))

        self.canvas.bind("<Configure>", _on_canvas_configure)

        # Enable mouse wheel scrolling
        self.canvas.bind("<Enter>", lambda e: self._bind_mousewheel())
        self.canvas.bind("<Leave>", lambda e: self._unbind_mousewheel())

        self.canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.lbl_vacio = ttk.Label(
            self.scrollable_frame,
            text="Carrito vacío 🛒",
            font=("Arial", 20),
            bootstyle="secondary"
        )
        self.lbl_vacio.pack(pady=(0, 10))


    def action_buttons(self):
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=X, padx=10, pady=10)

        self.btn_charge = ttk.Button(
            btn_frame,
            text="💰 COBRAR",
            command=self.content.charge,
            bootstyle="success",
        )
        self.btn_charge.pack(fill=X, pady=5, ipady=12)
        
        self.btn_clean = ttk.Button(
            btn_frame,
            text="🗑️ Limpiar",
            command=self.content.clean_shopping_car,
            bootstyle="danger",
        )
        self.btn_clean.pack(fill=X, pady=5, ipady=8)

        info_frame = ttk.Frame(self)
        info_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        self.lbl_items = ttk.Label(
            info_frame,
            text="0 Productos",
            font=("Arial", 10),
            bootstyle="secondary"
        )
        self.lbl_items.pack()


    def refresh_shopping_car(self):

        # Destroy scrollable_frame, canvas and scrollbar completely
        if hasattr(self, 'scrollable_frame'):
            self.scrollable_frame.destroy()
        if hasattr(self, 'canvas'):
            self.canvas.destroy()
        if hasattr(self, 'scrollbar'):
            self.scrollbar.destroy()

        # Recreate canvas from scratch (scroll resets automatically)
        self._create_canvas()

        # Reset scroll to top after recreation
        self.canvas.yview_moveto(0)

        if not self.content.shopping_cart:
            self.lbl_total.config(text="$0.00")
            self.lbl_items.config(text="0 items")
            return

        # Remove the empty label
        self.lbl_vacio.destroy()

        for i, item in enumerate(self.content.shopping_cart):
            self.create_shopping_car_item(i, item)

        # update total
        total = self.content.get_total()
        self.lbl_total.config(text=f"${total:.2f}")

        # update contador
        total_items = sum(item['quantity'] for item in self.content.shopping_cart)
        self.lbl_items.config(text=f"{total_items} items")


    def create_shopping_car_item(self, index, item):

        item_frame = ttk.Frame(
            self.scrollable_frame,
            bootstyle="light",
            relief="solid",
            borderwidth=1
        )

        # First item has no top padding, rest have 5px top padding
        pady = (0, 5) if index == 0 else 5
        item_frame.pack(fill=X, expand=NO, pady=pady, padx=0)

        content_frame = ttk.Frame(item_frame)
        content_frame.pack(fill=X, expand=YES, padx=10, pady=10)

        header_frame = ttk.Frame(content_frame)
        header_frame.pack(fill=X, expand=YES)

        ttk.Label(
            header_frame,
            text=item['name'],
            font=("Arial", 11, "bold")
        ).pack(side=LEFT)

        ttk.Label(
            header_frame,
            text=f"x{item['quantity']}",
            font=("Arial", 10),
            bootstyle="secondary"
        ).pack(side=RIGHT)

        price_frame = ttk.Frame(content_frame)
        price_frame.pack(fill=X, expand=YES, pady=(5, 0))

        ttk.Label(
            price_frame,
            text=f"${item['price']:.2f} c/u",
            font=("Arial", 9),
            bootstyle="secondary"
        ).pack(side=LEFT)

        ttk.Label(
            price_frame,
            text=f"${item['subtotal']:.2f}",
            font=("Arial", 12, "bold"),
            bootstyle="success"
        ).pack(side=RIGHT)

        btn_eliminar = ttk.Button(
            content_frame,
            text="❌ Eliminar",
            command=lambda: self.content.delete_product_from_car(index),
            bootstyle="danger-outline"
        )
        btn_eliminar.pack(fill=X, pady=(8, 0))


    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        # Windows uses event.delta, Linux/Mac use event.num
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")


    def _bind_mousewheel(self):
        """Bind mouse wheel events when mouse enters canvas"""
        # Windows and MacOS
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        # Linux
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)


    def _unbind_mousewheel(self):
        """Unbind mouse wheel events when mouse leaves canvas"""
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def get_mostrador_customer_id(self):
        mostrador = customer_provider.get_by_category(CUSTOMER_CATEGORIES['Mostrador'])
        return mostrador.id if mostrador else None