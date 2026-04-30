import os
import customtkinter as ctk
from customtkinter import CTkImage
from tkinter import messagebox, simpledialog
from PIL import Image

from .fileops import load_image_paths, move_image, move_to_deleted_folder


class ImageSorterUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- 1. Main Window Setup ---
        self.title("CustomTkinter Image Sorter")
        self.geometry("1000x650")

        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "favicon.ico"))
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # State Variables
        self.image_paths = []
        self.current_index = 0
        self.destination_folders = {}
        self.destination_key_bindings = {}
        self.destination_frames = {}  # Store frames for each destination
        self.current_zoom = 1.0
        self.original_image = None  # Store original image for zoom
        self.min_zoom = 0.5
        self.max_zoom = 3.0

        # Grid configuration: Left expands, Right is fixed
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        self._build_ui()
        self._bind_keys()

    def _build_ui(self):
        # --- 2. Left Panel: Viewer & Navigation ---
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        self.image_label = ctk.CTkLabel(self.left_frame, text="No Image Loaded", font=("Arial", 18))
        self.image_label.grid(row=0, column=0, sticky="nsew")

        self.nav_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.nav_frame.grid(row=1, column=0, pady=10, sticky="ew")
        self.nav_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.btn_prev = ctk.CTkButton(self.nav_frame, text="⬅️ Previous", command=self.show_prev, state="disabled")
        self.btn_prev.grid(row=0, column=0, padx=10)

        self.btn_delete = ctk.CTkButton(
            self.nav_frame,
            text="🗑️ Delete",
            command=self.delete_current_image,
            state="disabled",
            fg_color="#e74c3c",
            hover_color="#c0392b",
        )
        self.btn_delete.grid(row=0, column=1, padx=10)

        self.nav_entry_frame = ctk.CTkFrame(self.nav_frame, fg_color="transparent")
        self.nav_entry_frame.grid(row=0, column=2, padx=10)
        
        self.nav_entry = ctk.CTkEntry(self.nav_entry_frame, width=60, font=("Arial", 12), justify="center")
        self.nav_entry.pack(side="left", padx=5)
        self.nav_entry.bind("<Return>", self.on_entry_navigate)
        
        self.nav_label = ctk.CTkLabel(self.nav_entry_frame, text="/ 0", font=("Arial", 14, "bold"))
        self.nav_label.pack(side="left", padx=5)

        self.btn_next = ctk.CTkButton(self.nav_frame, text="Next ➡️", command=self.show_next, state="disabled")
        self.btn_next.grid(row=0, column=3, padx=10)

        # --- 2b. Zoom Controls ---
        self.zoom_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.zoom_frame.grid(row=2, column=0, pady=5, sticky="ew")
        self.zoom_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.btn_zoom_out = ctk.CTkButton(self.zoom_frame, text="🔍−", command=self.zoom_out, state="disabled", width=60)
        self.btn_zoom_out.grid(row=0, column=0, padx=10)

        self.zoom_label = ctk.CTkLabel(self.zoom_frame, text="100%", font=("Arial", 12, "bold"))
        self.zoom_label.grid(row=0, column=1)

        self.btn_zoom_in = ctk.CTkButton(self.zoom_frame, text="🔍+", command=self.zoom_in, state="disabled", width=60)
        self.btn_zoom_in.grid(row=0, column=2, padx=10)

        self.btn_zoom_reset = ctk.CTkButton(self.zoom_frame, text="Reset", command=self.reset_zoom, state="disabled", width=80)
        self.btn_zoom_reset.grid(row=0, column=3, padx=10)

        # --- 3. Right Panel: Sorting Controls ---
        self.right_frame = ctk.CTkFrame(self, width=250)
        self.right_frame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="ns")

        self.btn_load_source = ctk.CTkButton(
            self.right_frame,
            text="1. Select Source Folder",
            command=self.load_source_folder,
            fg_color="#2b7b58",
            hover_color="#1e5c41",
        )
        self.btn_load_source.pack(pady=(20, 10), padx=20, fill="x")

        ctk.CTkFrame(self.right_frame, height=2, fg_color="gray").pack(fill="x", padx=20, pady=10)

        self.btn_add_dest = ctk.CTkButton(self.right_frame, text="2. Add Target Folder ➕", command=self.add_destination_folder)
        self.btn_add_dest.pack(pady=10, padx=20, fill="x")

        self.dest_scroll_frame = ctk.CTkScrollableFrame(self.right_frame, label_text="Move Current Image To:")
        self.dest_scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)

    def _bind_keys(self):
        self.bind_all("<Key>", self.on_key_press)
        self.bind("<Left>", lambda event: self.show_prev())
        self.bind("<Right>", lambda event: self.show_next())
        self.bind("<KP_Left>", lambda event: self.show_prev())
        self.bind("<KP_Right>", lambda event: self.show_next())
        self.bind("<Delete>", lambda event: self.delete_current_image())
        
        # Mouse wheel zoom (Windows: MouseWheel, Linux: Button-4/Button-5)
        self.bind("<MouseWheel>", self.on_mouse_wheel)
        self.bind("<Button-4>", self.on_mouse_wheel)
        self.bind("<Button-5>", self.on_mouse_wheel)
        
        # Also bind to image label for better UX
        self.image_label.bind("<MouseWheel>", self.on_mouse_wheel)
        self.image_label.bind("<Button-4>", self.on_mouse_wheel)
        self.image_label.bind("<Button-5>", self.on_mouse_wheel)

    def load_source_folder(self):
        folder_path = ctk.filedialog.askdirectory(title="Select Source Folder")
        if not folder_path:
            return

        self.image_paths = load_image_paths(folder_path)
        if self.image_paths:
            self.current_index = 0
            self.current_zoom = 1.0  # Reset zoom for new source folder
            self.update_ui_state(has_images=True)
            self.display_image()
        else:
            self.image_label.configure(text="No images found in folder", image=None)
            self.update_ui_state(has_images=False)

    def add_destination_folder(self):
        folder_path = ctk.filedialog.askdirectory(title="Select Target Folder")
        if not folder_path:
            return

        folder_name = os.path.basename(folder_path)
        if folder_path in self.destination_folders.values():
            return

        self.destination_folders[folder_name] = folder_path
        key = self.ask_for_key_binding()
        if key:
            self.destination_key_bindings[key] = folder_path
            button_text = f"📂 {folder_name} [{key.upper()}]"
        else:
            button_text = f"📂 {folder_name}"

        # Create a frame for the button and remove button
        frame = ctk.CTkFrame(self.dest_scroll_frame)
        frame.pack(pady=5, padx=10, fill="x")
        frame.grid_columnconfigure(0, weight=1)

        btn = ctk.CTkButton(
            frame,
            text=button_text,
            command=lambda p=folder_path: self.move_current_image(p),
        )
        btn.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        remove_btn = ctk.CTkButton(
            frame,
            text="❌",
            width=40,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=lambda p=folder_path: self.remove_destination(p),
        )
        remove_btn.grid(row=0, column=1)

        self.destination_frames[folder_path] = frame

    def move_current_image(self, target_path):
        if not self.image_paths:
            return

        current_file = self.image_paths[self.current_index]
        try:
            move_image(current_file, target_path)
            self.image_paths.pop(self.current_index)

            if not self.image_paths:
                self.image_label.configure(text="All Done! 🎉", image=None)
                self.update_ui_state(has_images=False)
            else:
                if self.current_index >= len(self.image_paths):
                    self.current_index = len(self.image_paths) - 1
                self.display_image()
        except Exception as exc:
            print(f"Error moving file: {exc}")

    def remove_destination(self, folder_path):
        # Find the folder name
        folder_name = None
        for name, path in self.destination_folders.items():
            if path == folder_path:
                folder_name = name
                break

        if folder_name:
            del self.destination_folders[folder_name]

        # Remove key binding if exists
        for key, path in list(self.destination_key_bindings.items()):
            if path == folder_path:
                del self.destination_key_bindings[key]
                break

        # Destroy the frame
        if folder_path in self.destination_frames:
            self.destination_frames[folder_path].destroy()
            del self.destination_frames[folder_path]

    def ask_for_key_binding(self):
        while True:
            key = simpledialog.askstring("Bind Key", "Enter one key to bind this destination button (optional):")
            if key is None:
                return None
            key = key.strip().lower()
            if not key:
                return None
            key = key[0]
            if key in self.destination_key_bindings:
                messagebox.showerror("Duplicate Key", f"The key '{key.upper()}' is already in use.")
                continue
            return key

    def on_key_press(self, event):
        key = event.keysym.lower()
        if key in self.destination_key_bindings:
            self.move_current_image(self.destination_key_bindings[key])

    def delete_current_image(self):
        if not self.image_paths:
            return

        current_file = self.image_paths[self.current_index]
        try:
            move_to_deleted_folder(current_file)
            self.image_paths.pop(self.current_index)

            if not self.image_paths:
                self.image_label.configure(text="All Done! 🎉", image=None)
                self.update_ui_state(has_images=False)
            else:
                if self.current_index >= len(self.image_paths):
                    self.current_index = len(self.image_paths) - 1
                self.display_image()
        except Exception as exc:
            print(f"Error moving file to Deleted folder: {exc}")

    def display_image(self):
        img_path = self.image_paths[self.current_index]
        pil_image = Image.open(img_path)
        
        # Convert RGBA to RGB for faster loading and lower memory usage
        if pil_image.mode in ('RGBA', 'LA', 'P'):
            pil_image = pil_image.convert('RGB')
        
        # Store original image for zoom functionality
        self.original_image = pil_image
        # Don't reset zoom here - it persists across images
        
        img_width, img_height = pil_image.size
        max_size = 550
        ratio = min(max_size / img_width, max_size / img_height)
        new_size = (int(img_width * ratio), int(img_height * ratio))
        
        # Resize immediately to reduce memory usage and load time
        pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)

        ctk_img = CTkImage(light_image=pil_image, dark_image=pil_image, size=new_size)
        self.image_label.configure(image=ctk_img, text="")
        self.nav_entry.delete(0, "end")
        self.nav_entry.insert(0, str(self.current_index + 1))
        self.nav_label.configure(text=f"/ {len(self.image_paths)}")
        self.refresh_zoomed_image()

    def update_zoom_label(self):
        """Update the zoom percentage label"""
        zoom_percent = int(self.current_zoom * 100)
        self.zoom_label.configure(text=f"{zoom_percent}%")

    def zoom_in(self):
        """Increase zoom level"""
        if self.original_image and self.current_zoom < self.max_zoom:
            self.current_zoom = min(self.current_zoom + 0.2, self.max_zoom)
            self.refresh_zoomed_image()

    def zoom_out(self):
        """Decrease zoom level"""
        if self.original_image and self.current_zoom > self.min_zoom:
            self.current_zoom = max(self.current_zoom - 0.2, self.min_zoom)
            self.refresh_zoomed_image()

    def reset_zoom(self):
        """Reset zoom to 100%"""
        if self.original_image:
            self.current_zoom = 1.0
            self.display_image()

    def refresh_zoomed_image(self):
        """Refresh the displayed image with current zoom level"""
        if not self.original_image:
            return
        
        pil_image = self.original_image.copy()
        
        # Calculate new size based on zoom
        base_width, base_height = pil_image.size
        max_size = 550
        base_ratio = min(max_size / base_width, max_size / base_height)
        new_width = int(base_width * base_ratio * self.current_zoom)
        new_height = int(base_height * base_ratio * self.current_zoom)
        
        # Resize with zoom
        pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        ctk_img = CTkImage(light_image=pil_image, dark_image=pil_image, size=(new_width, new_height))
        self.image_label.configure(image=ctk_img, text="")
        self.update_zoom_label()

    def on_mouse_wheel(self, event):
        """Handle mouse wheel zoom events"""
        if not self.image_paths:
            return
        
        # event.delta > 0 means scroll up (zoom in), < 0 means scroll down (zoom out)
        # For Button-4/Button-5: Button-4 is up, Button-5 is down
        if event.num == 4 or event.delta > 0:
            self.zoom_in()
        elif event.num == 5 or event.delta < 0:
            self.zoom_out()

    def show_prev(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.display_image()

    def show_next(self):
        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self.display_image()

    def on_entry_navigate(self, event=None):
        try:
            target_index = int(self.nav_entry.get()) - 1
            if 0 <= target_index < len(self.image_paths):
                self.current_index = target_index
                self.display_image()
            else:
                self.nav_entry.delete(0, "end")
                self.nav_entry.insert(0, str(self.current_index + 1))
                messagebox.showerror("Invalid Index", f"Please enter a number between 1 and {len(self.image_paths)}")
        except ValueError:
            self.nav_entry.delete(0, "end")
            self.nav_entry.insert(0, str(self.current_index + 1))
            messagebox.showerror("Invalid Input", "Please enter a valid number")

    def update_ui_state(self, has_images):
        state = "normal" if has_images else "disabled"
        self.btn_prev.configure(state=state)
        self.btn_next.configure(state=state)
        self.btn_delete.configure(state=state)
        self.nav_entry.configure(state=state)
        self.btn_zoom_in.configure(state=state)
        self.btn_zoom_out.configure(state=state)
        self.btn_zoom_reset.configure(state=state)
        if not has_images:
            self.nav_entry.delete(0, "end")
            self.nav_entry.insert(0, "0")
            self.nav_label.configure(text="/ 0")
