import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app.gui.navigation import Navigation
from app.data.providers.inventory import inventory_provider
from app.data.providers.customers import customer_provider


class TortilleriaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tortillería Tierra Del Campo")
        self.root.geometry("1200x700")
        self.root.iconphoto(True, ttk.PhotoImage(file="tortilleria_logo.png"))
        
        # Main Container
        main_container = ttk.Frame(root)
        main_container.pack(fill=BOTH, expand=YES)
        
        # Left Navigation Buttons
        self.navigation = Navigation(main_container, self)
        self.navigation.pack(side=LEFT, fill=Y)

        # Main content
        self.content = None
        self.content_container = ttk.Frame(main_container)
        self.content_container.pack(side=LEFT, fill=BOTH, expand=YES)

        # Default View Products
        self.navigation.change_view("sales")


def main():
    # Initialize default products if database is empty
    inventory_provider._add_default_products()

    # Initialize generic Mostrador customer (hidden from user)
    customer_provider._create_generic_mostrador_customer()

    root = ttk.Window(themename="flatly")
    TortilleriaApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()