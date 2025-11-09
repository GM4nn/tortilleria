import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app.data.db import DatabaseManager
from app.gui.navigation import Navigation


class TortilleriaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Tortillería - POS")
        self.root.geometry("1200x700")
        
        # Init DB
        self.db = DatabaseManager()
        
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
        self.navigation.change_view("products")


def main():
    root = ttk.Window(themename="flatly")
    TortilleriaApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()