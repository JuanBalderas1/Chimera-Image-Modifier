# --- Imports ---
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk


# --- Core Image Logic ---
def resize_image(input_path, output_path, width, height, save_format, keep_ratio=False):
    with Image.open(input_path) as img:
        if keep_ratio:
            img.thumbnail((width, height))
            resized_img = img
        else:
            resized_img = img.resize((width, height))

        resized_img.save(output_path, save_format)


# --- Single Image Functions ---
def browse_input_file():
    file_path = filedialog.askopenfilename(
        title="Select an image",
        filetypes=[
            ("Image Files", "*.jpg *.jpeg *.png"),
            ("All Files", "*.*")
        ]
    )

    if file_path:
        input_path_var.set(file_path)


def apply_single_preset(*args):
    preset = single_preset_var.get()

    if preset == "Thumbnail":
        single_width_var.set("150")
        single_height_var.set("150")
    elif preset == "Medium":
        single_width_var.set("800")
        single_height_var.set("600")
    elif preset == "HD":
        single_width_var.set("1920")
        single_height_var.set("1080")


def preview_single_image():
    input_path = input_path_var.get()
    width_text = single_width_var.get()
    height_text = single_height_var.get()
    keep_ratio = single_keep_ratio_var.get()

    if not input_path:
        messagebox.showerror("Missing Input", "Please choose an input image.")
        return

    try:
        width = int(width_text)
        height = int(height_text)
    except ValueError:
        messagebox.showerror("Invalid Size", "Width and height must be numbers.")
        return

    try:
        with Image.open(input_path) as img:
            if keep_ratio:
                preview_img = img.copy()
                preview_img.thumbnail((width, height))
            else:
                preview_img = img.resize((width, height))

            preview_img.thumbnail((350, 250))

            tk_preview_img = ImageTk.PhotoImage(preview_img)
            preview_label.config(image=tk_preview_img, text="")
            preview_label.image = tk_preview_img

    except Exception as e:
        messagebox.showerror("Preview Error", f"Could not preview image:\n{e}")


def resize_and_save_clicked():
    input_path = input_path_var.get()
    output_name = output_name_var.get()
    width_text = single_width_var.get()
    height_text = single_height_var.get()
    keep_ratio = single_keep_ratio_var.get()
    format_choice = single_format_var.get()

    if not input_path:
        messagebox.showerror("Missing Input", "Please choose an input image.")
        return

    if not output_name:
        messagebox.showerror("Missing Output Name", "Please enter an output image name.")
        return

    try:
        width = int(width_text)
        height = int(height_text)
    except ValueError:
        messagebox.showerror("Invalid Size", "Width and height must be numbers.")
        return

    os.makedirs("Resized Images", exist_ok=True)

    if format_choice == "PNG":
        output_path = f"Resized Images/{output_name}.png"
        save_format = "PNG"
    else:
        output_path = f"Resized Images/{output_name}.jpg"
        save_format = "JPEG"

    try:
        resize_image(input_path, output_path, width, height, save_format, keep_ratio)
        messagebox.showinfo(
            "Success",
            f"Image resized and saved successfully!\n\nSaved to:\n{output_path}"
        )
    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong:\n{e}")


# --- Bulk Image Functions ---
def browse_bulk_folder():
    folder_path = filedialog.askdirectory(title="Select folder with images")

    if folder_path:
        bulk_folder_path_var.set(folder_path)


def apply_bulk_preset(*args):
    preset = bulk_preset_var.get()

    if preset == "Thumbnail":
        bulk_width_var.set("150")
        bulk_height_var.set("150")
    elif preset == "Medium":
        bulk_width_var.set("800")
        bulk_height_var.set("600")
    elif preset == "HD":
        bulk_width_var.set("1920")
        bulk_height_var.set("1080")


def preview_bulk_image():
    folder_path = bulk_folder_path_var.get()
    width_text = bulk_width_var.get()
    height_text = bulk_height_var.get()
    keep_ratio = bulk_keep_ratio_var.get()

    if not folder_path:
        messagebox.showerror("Missing Folder", "Please select a folder.")
        return

    try:
        width = int(width_text)
        height = int(height_text)
    except ValueError:
        messagebox.showerror("Invalid Size", "Width and height must be numbers.")
        return

    try:
        first_image_path = None

        for filename in os.listdir(folder_path):
            if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                first_image_path = os.path.join(folder_path, filename)
                break

        if not first_image_path:
            messagebox.showerror("No Images Found", "No JPG or PNG images were found in this folder.")
            return

        with Image.open(first_image_path) as img:
            if keep_ratio:
                preview_img = img.copy()
                preview_img.thumbnail((width, height))
            else:
                preview_img = img.resize((width, height))

            preview_img.thumbnail((350, 250))

            tk_preview_img = ImageTk.PhotoImage(preview_img)
            bulk_preview_label.config(image=tk_preview_img, text="")
            bulk_preview_label.image = tk_preview_img

    except Exception as e:
        messagebox.showerror("Preview Error", f"Could not preview image:\n{e}")


def bulk_resize_clicked():
    folder_path = bulk_folder_path_var.get()
    output_name = bulk_output_name_var.get()
    width_text = bulk_width_var.get()
    height_text = bulk_height_var.get()
    keep_ratio = bulk_keep_ratio_var.get()
    format_choice = bulk_format_var.get()

    if not folder_path:
        messagebox.showerror("Missing Folder", "Please select a folder.")
        return

    if not output_name:
        messagebox.showerror("Missing Output Name", "Please enter a base output image name.")
        return

    try:
        width = int(width_text)
        height = int(height_text)
    except ValueError:
        messagebox.showerror("Invalid Size", "Width and height must be numbers.")
        return

    os.makedirs("Resized Images", exist_ok=True)

    if format_choice == "PNG":
        save_format = "PNG"
        extension = ".png"
    else:
        save_format = "JPEG"
        extension = ".jpg"

    count = 1

    try:
        for filename in os.listdir(folder_path):
            if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                input_path = os.path.join(folder_path, filename)
                output_path = os.path.join(
                    "Resized Images",
                    f"{output_name}_{count}{extension}"
                )

                resize_image(input_path, output_path, width, height, save_format, keep_ratio)
                count += 1

        messagebox.showinfo("Success", f"Bulk resize complete!\n\nImages resized: {count - 1}")

    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong:\n{e}")


# --- GUI Setup ---
root = tk.Tk()
root.title("Automatic Image Resizer")
root.geometry("600x800")
root.resizable(False, False)

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

single_tab = tk.Frame(notebook)
bulk_tab = tk.Frame(notebook)

notebook.add(single_tab, text="Single Image")
notebook.add(bulk_tab, text="Bulk Resize")


# --- Tkinter Variables: Single Image ---
input_path_var = tk.StringVar()
output_name_var = tk.StringVar()
single_width_var = tk.StringVar(value="800")
single_height_var = tk.StringVar(value="600")
single_format_var = tk.StringVar(value="JPEG")
single_keep_ratio_var = tk.BooleanVar(value=False)
single_preset_var = tk.StringVar(value="Custom")


# --- Tkinter Variables: Bulk Image ---
bulk_folder_path_var = tk.StringVar()
bulk_output_name_var = tk.StringVar()
bulk_width_var = tk.StringVar(value="800")
bulk_height_var = tk.StringVar(value="600")
bulk_format_var = tk.StringVar(value="JPEG")
bulk_keep_ratio_var = tk.BooleanVar(value=False)
bulk_preset_var = tk.StringVar(value="Custom")


# --- Variable Traces ---
single_preset_var.trace_add("write", apply_single_preset)
bulk_preset_var.trace_add("write", apply_bulk_preset)


# --- Single Image Tab Layout ---
single_main_frame = tk.Frame(single_tab)
single_main_frame.pack(padx=20, pady=15, fill="both", expand=True)


# Step 1: Choose Image
single_input_frame = tk.LabelFrame(
    single_main_frame,
    text="Step 1: Choose Image",
    padx=10,
    pady=10
)
single_input_frame.pack(fill="x", pady=8)

tk.Label(single_input_frame, text="Input Image:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
tk.Entry(single_input_frame, textvariable=input_path_var, width=55).grid(row=0, column=1, padx=5, pady=5)
tk.Button(single_input_frame, text="Select Image", command=browse_input_file).grid(row=0, column=2, padx=5, pady=5)


# Step 2: Resize Settings
single_settings_frame = tk.LabelFrame(
    single_main_frame,
    text="Step 2: Resize Settings",
    padx=10,
    pady=10
)
single_settings_frame.columnconfigure(0, weight=1)
single_settings_frame.columnconfigure(1, weight=1)
single_settings_frame.columnconfigure(2, weight=1)
single_settings_frame.columnconfigure(3, weight=1)
single_settings_frame.pack(fill="x", pady=8)

tk.Label(single_settings_frame, text="Preset:").grid(row=0, column=0, padx=5, pady=5)
tk.OptionMenu(single_settings_frame, single_preset_var, "Custom", "Thumbnail", "Medium", "HD").grid(row=0, column=1, padx=5, pady=5)

tk.Label(single_settings_frame, text="Format:").grid(row=0, column=2, padx=5, pady=5)
tk.OptionMenu(single_settings_frame, single_format_var, "JPEG", "PNG").grid(row=0, column=3, padx=5, pady=5)

tk.Label(single_settings_frame, text="Width:").grid(row=1, column=0, padx=5, pady=5)
tk.Entry(single_settings_frame, textvariable=single_width_var, width=10).grid(row=1, column=1, padx=5, pady=5)

tk.Label(single_settings_frame, text="Height:").grid(row=1, column=2, padx=5, pady=5)
tk.Entry(single_settings_frame, textvariable=single_height_var, width=10).grid(row=1, column=3, padx=5, pady=5)

tk.Checkbutton(
    single_settings_frame,
    text="Maintain aspect ratio. (May override selected dimensions)",
    variable=single_keep_ratio_var
).grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky="w")


# Step 3: Preview and Save
single_preview_frame = tk.LabelFrame(
    single_main_frame,
    text="Step 3: Preview and Save",
    padx=10,
    pady=10
)
single_preview_frame.columnconfigure(0, weight=1)
single_preview_frame.columnconfigure(1, weight=1)
single_preview_frame.pack(fill="x", pady=8)

tk.Label(single_preview_frame, text="New Image Name (no extension):").grid(
    row=0, column=0, padx=5, pady=5, sticky="e"
)

tk.Entry(single_preview_frame, textvariable=output_name_var, width=30).grid(
    row=0, column=1, padx=5, pady=5, sticky="w"
)

preview_frame = tk.Frame(
    single_preview_frame,
    width=350,
    height=250,
    bg="#d9d9d9",
    relief="solid",
    borderwidth=1
)
preview_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=10)
preview_frame.grid_propagate(False)

preview_label = tk.Label(
    preview_frame,
    text="Preview will appear here",
    bg="#d9d9d9"
)
preview_label.place(relx=0.5, rely=0.5, anchor="center")

single_button_frame = tk.Frame(single_preview_frame)
single_button_frame.grid(row=2, column=0, columnspan=2, pady=10)

tk.Button(
    single_button_frame,
    text="Preview Image",
    command=preview_single_image,
    width=18
).grid(row=0, column=0, padx=10)

tk.Button(
    single_button_frame,
    text="Resize and Save Image",
    command=resize_and_save_clicked,
    width=22
).grid(row=0, column=1, padx=10)

tk.Label(
    single_preview_frame,
    text="Saved images go to the 'Resized Images' folder.",
    fg="gray"
).grid(row=3, column=0, columnspan=2, pady=5)


# --- Bulk Image Tab Layout ---
bulk_main_frame = tk.Frame(bulk_tab)
bulk_main_frame.pack(padx=20, pady=15, fill="both", expand=True)


# Step 1: Choose Folder
bulk_input_frame = tk.LabelFrame(
    bulk_main_frame,
    text="Step 1: Choose Folder",
    padx=10,
    pady=10
)
bulk_input_frame.pack(fill="x", pady=8)

tk.Label(bulk_input_frame, text="Input Folder:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
tk.Entry(bulk_input_frame, textvariable=bulk_folder_path_var, width=55).grid(row=0, column=1, padx=5, pady=5)
tk.Button(bulk_input_frame, text="Select Folder", command=browse_bulk_folder).grid(row=0, column=2, padx=5, pady=5)


# Step 2: Resize Settings
bulk_settings_frame = tk.LabelFrame(
    bulk_main_frame,
    text="Step 2: Resize Settings",
    padx=10,
    pady=10
)
bulk_settings_frame.columnconfigure(0, weight=1)
bulk_settings_frame.columnconfigure(1, weight=1)
bulk_settings_frame.columnconfigure(2, weight=1)
bulk_settings_frame.columnconfigure(3, weight=1)
bulk_settings_frame.pack(fill="x", pady=8)

tk.Label(bulk_settings_frame, text="Preset:").grid(row=0, column=0, padx=5, pady=5)
tk.OptionMenu(bulk_settings_frame, bulk_preset_var, "Custom", "Thumbnail", "Medium", "HD").grid(row=0, column=1, padx=5, pady=5)

tk.Label(bulk_settings_frame, text="Format:").grid(row=0, column=2, padx=5, pady=5)
tk.OptionMenu(bulk_settings_frame, bulk_format_var, "JPEG", "PNG").grid(row=0, column=3, padx=5, pady=5)

tk.Label(bulk_settings_frame, text="Width:").grid(row=1, column=0, padx=5, pady=5)
tk.Entry(bulk_settings_frame, textvariable=bulk_width_var, width=10).grid(row=1, column=1, padx=5, pady=5)

tk.Label(bulk_settings_frame, text="Height:").grid(row=1, column=2, padx=5, pady=5)
tk.Entry(bulk_settings_frame, textvariable=bulk_height_var, width=10).grid(row=1, column=3, padx=5, pady=5)

tk.Checkbutton(
    bulk_settings_frame,
    text="Maintain aspect ratio. (May override selected dimensions)",
    variable=bulk_keep_ratio_var
).grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky="w")


# Step 3: Preview and Save
bulk_preview_frame_outer = tk.LabelFrame(
    bulk_main_frame,
    text="Step 3: Preview and Save",
    padx=10,
    pady=10
)
bulk_preview_frame_outer.columnconfigure(0, weight=1)
bulk_preview_frame_outer.columnconfigure(1, weight=1)
bulk_preview_frame_outer.pack(fill="x", pady=8)

tk.Label(bulk_preview_frame_outer, text="Base Image Name (no extension):").grid(
    row=0, column=0, padx=5, pady=5, sticky="e"
)

tk.Entry(bulk_preview_frame_outer, textvariable=bulk_output_name_var, width=30).grid(
    row=0, column=1, padx=5, pady=5, sticky="w"
)

bulk_preview_frame = tk.Frame(
    bulk_preview_frame_outer,
    width=350,
    height=250,
    bg="#d9d9d9",
    relief="solid",
    borderwidth=1
)
bulk_preview_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=10)
bulk_preview_frame.grid_propagate(False)

bulk_preview_label = tk.Label(
    bulk_preview_frame,
    text="First image preview will appear here",
    bg="#d9d9d9"
)
bulk_preview_label.place(relx=0.5, rely=0.5, anchor="center")

bulk_button_frame = tk.Frame(bulk_preview_frame_outer)
bulk_button_frame.grid(row=2, column=0, columnspan=2, pady=10)

tk.Button(
    bulk_button_frame,
    text="Preview First Image",
    command=preview_bulk_image,
    width=18
).grid(row=0, column=0, padx=10)

tk.Button(
    bulk_button_frame,
    text="Resize and Save Images",
    command=bulk_resize_clicked,
    width=22
).grid(row=0, column=1, padx=10)

tk.Label(
    bulk_preview_frame_outer,
    text="Saved images go to the 'Resized Images' folder.",
    fg="gray"
).grid(row=3, column=0, columnspan=2, pady=5)


# --- Run App ---
root.mainloop()