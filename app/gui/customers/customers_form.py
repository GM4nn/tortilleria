import os
import shutil
from datetime import datetime
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app.data.providers.customers import customer_provider


class CustomersForm(ttk.Frame):
    def __init__(self, parent, app, main_container):
        super().__init__(parent)

        self.app = app
        self.parent = parent
        self.provider = customer_provider
        self.main_container = main_container
        self.selected_customer_id = None

        self.setup_ui()


    def setup_ui(self):
        self.right_frame = ttk.Frame(self.main_container)
        self.right_frame.pack(side=RIGHT, fill=BOTH, padx=(10, 0))

        self.setup_form_section()
        self.setup_btn_actions()


    def setup_form_section(self):

        ttk.Label(
            self.right_frame,
            text="Gestión de Cliente",
            font=("Arial", 14, "bold")
        ).pack(pady=(0, 20))

        self.form_frame = ttk.Frame(self.right_frame)
        self.form_frame.pack(fill=BOTH, expand=YES)

        id_frame = ttk.Frame(self.form_frame)
        id_frame.pack(fill=X, pady=5)

        ttk.Label(id_frame, text="ID:", width=12).pack(side=LEFT)
        self.id_label = ttk.Label(
            id_frame,
            text="Nuevo",
            font=("Arial", 10, "bold"),
            bootstyle="info"
        )
        self.id_label.pack(side=LEFT)

        ttk.Label(self.form_frame, text="Nombre:").pack(anchor=W, pady=(10, 2))
        self.name_var = ttk.StringVar()
        self.name_entry = ttk.Entry(
            self.form_frame,
            textvariable=self.name_var,
            width=30
        )
        self.name_entry.pack(fill=X, pady=(0, 10))

        ttk.Label(self.form_frame, text="Teléfono:").pack(anchor=W, pady=(10, 2))
        self.phone_var = ttk.StringVar()
        self.phone_entry = ttk.Entry(
            self.form_frame,
            textvariable=self.phone_var,
            width=30
        )
        self.phone_entry.pack(fill=X, pady=(0, 10))

        ttk.Label(self.form_frame, text="Dirección:").pack(anchor=W, pady=(10, 2))
        self.direction_var = ttk.StringVar()
        self.direction_entry = ttk.Entry(
            self.form_frame,
            textvariable=self.direction_var,
            width=30
        )
        self.direction_entry.pack(fill=X, pady=(0, 10))

        ttk.Label(self.form_frame, text="Categoría:").pack(anchor=W, pady=(10, 2))
        self.category_var = ttk.StringVar()
        self.category_combo = ttk.Combobox(
            self.form_frame,
            textvariable=self.category_var,
            values=["Mostrador", "Comedor", "Tienda"],
            width=28,
            state="readonly"
        )
        self.category_combo.pack(fill=X, pady=(0, 10))
        self.category_combo.current(0)

        ttk.Label(self.form_frame, text="Foto del Cliente:").pack(anchor=W, pady=(10, 2))

        photo_frame = ttk.Frame(self.form_frame)
        photo_frame.pack(fill=X, pady=(0, 10))

        self.photo_var = ttk.StringVar()
        self.photo_entry = ttk.Entry(
            photo_frame,
            textvariable=self.photo_var,
            width=20,
            state="readonly"
        )
        self.photo_entry.pack(side=LEFT, fill=X, expand=YES, padx=(0, 5))

        ttk.Button(
            photo_frame,
            text="Cargar",
            command=self.load_image,
            bootstyle="info-outline",
            width=10
        ).pack(side=LEFT)

        ttk.Separator(self.form_frame, orient="horizontal").pack(fill=X, pady=(15, 10))

        self.preview_frame = ttk.Frame(self.form_frame)
        self.preview_frame.pack(fill=X, pady=(5, 10))

        self.image_label = ttk.Label(self.preview_frame, text="Sin imagen", cursor="hand2")
        self.image_label.pack()

        self.image_label.bind("<Double-Button-1>", self.show_full_image)

        self.current_image = None


    def setup_btn_actions(self):

        btn_container = ttk.Frame(self.form_frame)
        btn_container.pack(fill=X, pady=(10, 0))

        ttk.Button(
            btn_container,
            text="Nuevo",
            command=self.new_customer,
            bootstyle="success",
            width=20
        ).pack(fill=X, pady=5)

        ttk.Button(
            btn_container,
            text="Guardar",
            command=self.save_customer,
            bootstyle="primary",
            width=20
        ).pack(fill=X, pady=5)

        ttk.Button(
            btn_container,
            text="Eliminar",
            command=self.delete_customer,
            bootstyle="danger",
            width=20
        ).pack(fill=X, pady=5)

        ttk.Button(
            btn_container,
            text="Limpiar",
            command=self.clear_form,
            bootstyle="secondary-outline",
            width=20
        ).pack(fill=X, pady=5)


    def load_image(self):

        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen del cliente",
            filetypes=[
                ("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Todos los archivos", "*.*")
            ]
        )

        if file_path:

            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                ext = os.path.splitext(file_path)[1]
                new_filename = f"customer_{timestamp}{ext}"

                image_dir = os.path.join("app", "data", "customer_images")
                os.makedirs(image_dir, exist_ok=True)

                dest_path = os.path.join(image_dir, new_filename)
                shutil.copy2(file_path, dest_path)

                self.photo_var.set(dest_path)

                self.update_image_preview(dest_path)

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la imagen: {str(e)}")

    def update_image_preview(self, image_path):

        try:
            if image_path and os.path.exists(image_path):

                img = Image.open(image_path)
                img.thumbnail((150, 150), Image.Resampling.LANCZOS)

                photo = ImageTk.PhotoImage(img)

                self.current_image = photo
                self.image_label.config(image=photo, text="")
            else:

                self.current_image = None
                self.image_label.config(image="", text="Sin imagen")
        
        except Exception as e:
            
            self.current_image = None
            self.image_label.config(image="", text="Error al cargar imagen")
            
            print(f"Error al cargar imagen: {e}")

    def show_full_image(self, event=None):

        image_path = self.photo_var.get()

        if not image_path or not os.path.exists(image_path):
            messagebox.showinfo("Sin imagen", "No hay imagen para mostrar")
            return

        try:

            popup = ttk.Toplevel(self)
            popup.title("Vista de Imagen - Cliente")
            popup.geometry("800x600")

            popup.transient(self)
            popup.grab_set()

            main_frame = ttk.Frame(popup, padding=10)
            main_frame.pack(fill=BOTH, expand=YES)

            img = Image.open(image_path)

            max_width = 780
            max_height = 520

            # Calculate ratio
            img_width, img_height = img.size
            width_ratio = max_width / img_width
            height_ratio = max_height / img_height
            ratio = min(width_ratio, height_ratio)

            # Resize while maintaining proportion
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            photo = ImageTk.PhotoImage(img_resized)

            image_label = ttk.Label(main_frame, image=photo)
            image_label.image = photo
            image_label.pack(pady=10)

            info_text = f"Tamaño original: {img_width}x{img_height} px"
            ttk.Label(main_frame, text=info_text, font=("Arial", 9)).pack(pady=5)

            ttk.Button(
                main_frame,
                text="Cerrar",
                command=popup.destroy,
                bootstyle="secondary",
                width=15
            ).pack(pady=10)

            # Centry window
            popup.update_idletasks()
            width = popup.winfo_width()
            height = popup.winfo_height()
            x = (popup.winfo_screenwidth() // 2) - (width // 2)
            y = (popup.winfo_screenheight() // 2) - (height // 2)
            popup.geometry(f'{width}x{height}+{x}+{y}')

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo mostrar la imagen: {str(e)}")

    def new_customer(self):
        self.clear_form()
        self.name_entry.focus()


    def save_customer(self):

        name = self.name_var.get().strip()
        phone = self.phone_var.get().strip()
        direction = self.direction_var.get().strip()
        category = self.category_var.get().strip()
        photo = self.photo_var.get().strip()

        if not name:
            messagebox.showerror("Error", "El nombre del cliente es obligatorio")
            self.name_entry.focus()
            return
        
        if not category:
            messagebox.showerror("Error", "La categoria del cliente es obligatoria")
            self.name_entry.focus()
            return

        if self.selected_customer_id is None:

            success, result = self.provider.add(name, direction, category, photo, phone)

            if success:
                messagebox.showinfo("Éxito", "Cliente creado exitosamente")
                self.clear_form()

                if hasattr(self.parent, 'table_section'):
                    self.parent.table_section.load_customers()
            else:
                messagebox.showerror("Error", f"No se pudo crear el cliente: {result}")
        else:
            # Update existing customer
            success, result = self.provider.update(
                self.selected_customer_id, name, direction, category, photo, phone
            )
            if success:
                messagebox.showinfo("Éxito", "Cliente actualizado exitosamente")
                self.clear_form()

                if hasattr(self.parent, 'table_section'):
                    self.parent.table_section.load_customers()
            else:
                messagebox.showerror("Error", f"No se pudo actualizar el cliente: {result}")


    def delete_customer(self):

        if self.selected_customer_id is None:
            messagebox.showwarning("Advertencia", "Seleccione un cliente para eliminar")
            return

        confirm = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar al cliente '{self.name_var.get()}'?"
        )

        if not confirm:
            return

        success, result = self.provider.delete(self.selected_customer_id)

        if success:
            messagebox.showinfo("Éxito", "Cliente eliminado exitosamente")
            self.clear_form()

            if hasattr(self.parent, 'table_section'):
                self.parent.table_section.load_customers()
        else:
            messagebox.showerror("Error", f"No se pudo eliminar el cliente: {result}")


    def clear_form(self):

        self.selected_customer_id = None
        self.id_label.config(text="Nuevo")
        self.name_var.set("")
        self.phone_var.set("")
        self.direction_var.set("")
        self.category_var.set("Mostrador")
        self.photo_var.set("")

        # Limpiar vista previa de imagen
        self.current_image = None
        self.image_label.config(image="", text="Sin imagen")

        if hasattr(self.parent, 'table_section'):
            self.parent.table_section.clear_selection()
