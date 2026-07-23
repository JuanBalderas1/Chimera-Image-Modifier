import os
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk


# -----------------------------
# Application configuration
# -----------------------------
APP_NAME = "Chimera Image Modifier"
OUTPUT_FOLDER = "Modified Images"
SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png")

THEMES = {
    "Chimera Default": {
        "appearance": "Dark",
        "window": "#202124",
        "surface": "#2B2D31",
        "surface_alt": "#35383D",
        "preview": "#181A1D",
        "accent": "#F28C28",
        "accent_hover": "#FFAA4C",
        "text": "#D8D8D8",
        "muted": "#A7A7A7",
        "entry": "#17191C",
        "entry_border": "#55585E",
        "border": "#111214",
        "danger": "#B84A4A",
    },
    "Light Mode": {
        "appearance": "Light",
        "window": "#ECECEC",
        "surface": "#FFFFFF",
        "surface_alt": "#F1F1F1",
        "preview": "#E2E2E2",
        "accent": "#D96C00",
        "accent_hover": "#F28C28",
        "text": "#232323",
        "muted": "#666666",
        "entry": "#FFFFFF",
        "entry_border": "#B9B9B9",
        "border": "#C9C9C9",
        "danger": "#B23A3A",
    },
    "Dark Mode": {
        "appearance": "Dark",
        "window": "#121212",
        "surface": "#1D1D1D",
        "surface_alt": "#292929",
        "preview": "#0B0B0B",
        "accent": "#8F8F8F",
        "accent_hover": "#B5B5B5",
        "text": "#F0F0F0",
        "muted": "#A0A0A0",
        "entry": "#101010",
        "entry_border": "#4B4B4B",
        "border": "#050505",
        "danger": "#A33E3E",
    },
}

FONT_SIZES = {
    "Small": 12,
    "Medium": 14,
    "Large": 16,
}

PRESETS = {
    "Custom": None,
    "Thumbnail": (150, 150),
    "Medium": (800, 600),
    "HD": (1920, 1080),
}


# -----------------------------
# Core image logic
# -----------------------------
def resize_image(input_path, output_path, width, height, save_format, keep_ratio=False):
    with Image.open(input_path) as img:
        working_image = img.copy()

        if keep_ratio:
            working_image.thumbnail((width, height), Image.Resampling.LANCZOS)
            resized_img = working_image
        else:
            resized_img = working_image.resize(
                (width, height),
                Image.Resampling.LANCZOS,
            )

        # JPEG cannot save images with transparency or palette mode.
        if save_format == "JPEG" and resized_img.mode not in ("RGB", "L"):
            resized_img = resized_img.convert("RGB")

        resized_img.save(output_path, save_format)


class ChimeraImageModifier(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.current_theme_name = "Chimera Default"
        self.current_font_size_name = "Medium"
        self.current_theme = THEMES[self.current_theme_name]
        self.base_font_size = FONT_SIZES[self.current_font_size_name]

        ctk.set_appearance_mode(self.current_theme["appearance"])
        ctk.set_default_color_theme("blue")

        self.title(APP_NAME)
        self.geometry("1050x820")
        self.minsize(900, 720)
        self.resizable(True, True)
        self.configure(fg_color=self.current_theme["window"])

        self.preview_ctk_image = None
        self.bulk_preview_ctk_image = None

        # Transparency editor state
        self.transparency_source_image = None
        self.transparency_mask = None
        self.transparency_display_image = None
        self.transparency_tk_image = None
        self.transparency_scale = 1.0
        self.transparency_offset_x = 0
        self.transparency_offset_y = 0
        self.transparency_last_point = None
        self.transparency_tool = "Erase"
        self.transparency_zoom = 1.0
        self.transparency_fit_scale = 1.0
        self.transparency_undo_stack = []
        self.transparency_redo_stack = []
        self.transparency_stroke_snapshot = None
        self.transparency_history_limit = 30

        self._create_variables()
        self._create_fonts()
        self._build_interface()
        self.apply_theme()

    # -------------------------
    # Variables and fonts
    # -------------------------
    def _create_variables(self):
        self.input_path_var = tk.StringVar()
        self.output_name_var = tk.StringVar()
        self.single_width_var = tk.StringVar(value="800")
        self.single_height_var = tk.StringVar(value="600")
        self.single_format_var = tk.StringVar(value="JPEG")
        self.single_keep_ratio_var = tk.BooleanVar(value=False)
        self.single_preset_var = tk.StringVar(value="Custom")

        self.bulk_folder_path_var = tk.StringVar()
        self.bulk_output_name_var = tk.StringVar()
        self.bulk_width_var = tk.StringVar(value="800")
        self.bulk_height_var = tk.StringVar(value="600")
        self.bulk_format_var = tk.StringVar(value="JPEG")
        self.bulk_keep_ratio_var = tk.BooleanVar(value=False)
        self.bulk_preset_var = tk.StringVar(value="Custom")

        self.theme_var = tk.StringVar(value=self.current_theme_name)
        self.font_size_var = tk.StringVar(value=self.current_font_size_name)

        self.transparency_input_path_var = tk.StringVar()
        self.transparency_output_name_var = tk.StringVar(value="transparent_image")
        self.transparency_brush_size_var = tk.IntVar(value=40)
        self.transparency_tool_var = tk.StringVar(value="Erase")
        self.transparency_zoom_label_var = tk.StringVar(value="100%")

    def _create_fonts(self):
        size = self.base_font_size
        self.font_normal = ctk.CTkFont(family="Segoe UI", size=size)
        self.font_small = ctk.CTkFont(family="Segoe UI", size=max(10, size - 2))
        self.font_bold = ctk.CTkFont(family="Segoe UI", size=size, weight="bold")
        self.font_section = ctk.CTkFont(family="Segoe UI", size=size + 2, weight="bold")
        self.font_title = ctk.CTkFont(family="Segoe UI", size=size + 15, weight="bold")
        self.font_subtitle = ctk.CTkFont(family="Segoe UI", size=size, slant="italic")

    # -------------------------
    # Interface construction
    # -------------------------
    def _build_interface(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.header_frame = ctk.CTkFrame(self, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        # A subtle offset duplicate creates a black title outline/shadow effect.
        self.title_shadow = ctk.CTkLabel(
            self.header_frame,
            text=APP_NAME,
            font=self.font_title,
            text_color="#000000",
        )
        self.title_shadow.grid(row=0, column=0, padx=(33, 29), pady=(22, 0))

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=APP_NAME,
            font=self.font_title,
        )
        self.title_label.grid(row=0, column=0, padx=30, pady=(19, 0))

        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Resize, convert, and organize images with precision.",
            font=self.font_subtitle,
        )
        self.subtitle_label.grid(row=1, column=0, padx=30, pady=(2, 18))

        self.tabview = ctk.CTkTabview(
            self,
            corner_radius=18,
            border_width=1,
            segmented_button_selected_hover_color=None,
        )
        self.tabview.grid(row=1, column=0, padx=24, pady=(0, 24), sticky="nsew")
        self.tabview.add("Single Image Resize")
        self.tabview.add("Bulk Image Resize")
        self.tabview.add("Transparency Editor")
        self.tabview.add("Personal Settings")
        self.tabview.set("Single Image Resize")

        self.single_tab = self.tabview.tab("Single Image Resize")
        self.bulk_tab = self.tabview.tab("Bulk Image Resize")
        self.transparency_tab = self.tabview.tab("Transparency Editor")
        self.settings_tab = self.tabview.tab("Personal Settings")

        self._build_single_tab()
        self._build_bulk_tab()
        self._build_transparency_tab()
        self._build_settings_tab()
        self._update_history_buttons()

    def _build_single_tab(self):
        tab = self.single_tab
        tab.grid_columnconfigure(0, weight=1, uniform="single_workspace")
        tab.grid_columnconfigure(1, weight=1, uniform="single_workspace")
        tab.grid_rowconfigure(0, weight=1)

        self.single_controls_column = ctk.CTkScrollableFrame(
            tab,
            corner_radius=16,
            fg_color="transparent",
        )
        self.single_controls_column.grid(
            row=0, column=0, padx=(10, 8), pady=10, sticky="nsew"
        )
        self.single_controls_column.grid_columnconfigure(0, weight=1)

        self.single_input_card = self._create_card(
            self.single_controls_column, "1  Choose an image", 0
        )
        self.single_input_card.grid_columnconfigure(0, weight=1)

        self.single_input_label = self._label(self.single_input_card, "Input image")
        self.single_input_label.grid(row=1, column=0, padx=18, pady=(6, 4), sticky="w")

        self.single_input_entry = self._entry(
            self.single_input_card,
            self.input_path_var,
            placeholder="Select a JPG, JPEG, or PNG image",
        )
        self.single_input_entry.grid(row=2, column=0, padx=18, pady=(0, 10), sticky="ew")

        self.single_browse_button = self._button(
            self.single_input_card,
            "Select Image",
            self.browse_input_file,
        )
        self.single_browse_button.grid(row=3, column=0, padx=18, pady=(0, 18), sticky="ew")

        self.single_settings_card = self._create_card(
            self.single_controls_column, "2  Resize settings", 1
        )
        self.single_settings_card.grid_columnconfigure(0, weight=1)
        self.single_settings_card.grid_columnconfigure(1, weight=1)

        self._label(self.single_settings_card, "Preset").grid(
            row=1, column=0, padx=(18, 8), pady=(6, 4), sticky="w"
        )
        self._label(self.single_settings_card, "Format").grid(
            row=1, column=1, padx=(8, 18), pady=(6, 4), sticky="w"
        )

        self.single_preset_menu = self._option_menu(
            self.single_settings_card,
            self.single_preset_var,
            list(PRESETS.keys()),
            self.apply_single_preset,
        )
        self.single_preset_menu.grid(row=2, column=0, padx=(18, 8), pady=(0, 12), sticky="ew")

        self.single_format_menu = self._option_menu(
            self.single_settings_card,
            self.single_format_var,
            ["JPEG", "PNG"],
        )
        self.single_format_menu.grid(row=2, column=1, padx=(8, 18), pady=(0, 12), sticky="ew")

        self._label(self.single_settings_card, "Width (px)").grid(
            row=3, column=0, padx=(18, 8), pady=(2, 4), sticky="w"
        )
        self._label(self.single_settings_card, "Height (px)").grid(
            row=3, column=1, padx=(8, 18), pady=(2, 4), sticky="w"
        )

        self.single_width_entry = self._entry(self.single_settings_card, self.single_width_var)
        self.single_width_entry.grid(row=4, column=0, padx=(18, 8), pady=(0, 12), sticky="ew")
        self.single_height_entry = self._entry(self.single_settings_card, self.single_height_var)
        self.single_height_entry.grid(row=4, column=1, padx=(8, 18), pady=(0, 12), sticky="ew")

        self.single_ratio_checkbox = ctk.CTkCheckBox(
            self.single_settings_card,
            text="Maintain aspect ratio",
            variable=self.single_keep_ratio_var,
            font=self.font_normal,
            corner_radius=6,
        )
        self.single_ratio_checkbox.grid(
            row=5, column=0, columnspan=2, padx=18, pady=(2, 18), sticky="w"
        )

        self.single_output_card = self._create_card(
            self.single_controls_column, "3  Preview and save", 2
        )
        self.single_output_card.grid_columnconfigure(0, weight=1)

        self._label(self.single_output_card, "New image name (no extension)").grid(
            row=1, column=0, padx=18, pady=(6, 4), sticky="w"
        )
        self.single_output_entry = self._entry(
            self.single_output_card,
            self.output_name_var,
            placeholder="Example: vacation_photo_resized",
        )
        self.single_output_entry.grid(row=2, column=0, padx=18, pady=(0, 12), sticky="ew")

        self.single_preview_button = self._button(
            self.single_output_card,
            "Preview Image",
            self.preview_single_image,
            secondary=True,
        )
        self.single_preview_button.grid(row=3, column=0, padx=18, pady=6, sticky="ew")

        self.single_save_button = self._button(
            self.single_output_card,
            "Resize and Save Image",
            self.resize_and_save_clicked,
        )
        self.single_save_button.grid(row=4, column=0, padx=18, pady=6, sticky="ew")

        self.single_save_note = ctk.CTkLabel(
            self.single_output_card,
            text=f"Saved images go to the '{OUTPUT_FOLDER}' folder.",
            font=self.font_small,
            wraplength=360,
        )
        self.single_save_note.grid(row=5, column=0, padx=18, pady=(8, 18))

        self.single_preview_card = ctk.CTkFrame(tab, corner_radius=18, border_width=1)
        self.single_preview_card.grid(
            row=0, column=1, padx=(8, 10), pady=10, sticky="nsew"
        )
        self.single_preview_card.grid_columnconfigure(0, weight=1)
        self.single_preview_card.grid_rowconfigure(1, weight=1)

        self.single_preview_heading = ctk.CTkLabel(
            self.single_preview_card,
            text="Image Preview",
            font=self.font_section,
        )
        self.single_preview_heading.grid(row=0, column=0, padx=18, pady=(16, 8), sticky="w")

        self.single_preview_panel = ctk.CTkFrame(
            self.single_preview_card,
            corner_radius=16,
            border_width=1,
        )
        self.single_preview_panel.grid(row=1, column=0, padx=18, pady=(4, 18), sticky="nsew")
        self.single_preview_panel.grid_columnconfigure(0, weight=1)
        self.single_preview_panel.grid_rowconfigure(0, weight=1)

        self.preview_label = ctk.CTkLabel(
            self.single_preview_panel,
            text="Your resized preview will appear here",
            font=self.font_normal,
            wraplength=420,
        )
        self.preview_label.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)

    def _build_bulk_tab(self):
        tab = self.bulk_tab
        tab.grid_columnconfigure(0, weight=1, uniform="bulk_workspace")
        tab.grid_columnconfigure(1, weight=1, uniform="bulk_workspace")
        tab.grid_rowconfigure(0, weight=1)

        self.bulk_controls_column = ctk.CTkScrollableFrame(
            tab,
            corner_radius=16,
            fg_color="transparent",
        )
        self.bulk_controls_column.grid(row=0, column=0, padx=(10, 8), pady=10, sticky="nsew")
        self.bulk_controls_column.grid_columnconfigure(0, weight=1)

        self.bulk_input_card = self._create_card(
            self.bulk_controls_column, "1  Choose an image folder", 0
        )
        self.bulk_input_card.grid_columnconfigure(0, weight=1)

        self._label(self.bulk_input_card, "Input folder").grid(
            row=1, column=0, padx=18, pady=(6, 4), sticky="w"
        )
        self.bulk_folder_entry = self._entry(
            self.bulk_input_card,
            self.bulk_folder_path_var,
            placeholder="Select a folder containing JPG, JPEG, or PNG images",
        )
        self.bulk_folder_entry.grid(row=2, column=0, padx=18, pady=(0, 10), sticky="ew")

        self.bulk_browse_button = self._button(
            self.bulk_input_card,
            "Select Folder",
            self.browse_bulk_folder,
        )
        self.bulk_browse_button.grid(row=3, column=0, padx=18, pady=(0, 18), sticky="ew")

        self.bulk_settings_card = self._create_card(
            self.bulk_controls_column, "2  Resize settings", 1
        )
        self.bulk_settings_card.grid_columnconfigure(0, weight=1)
        self.bulk_settings_card.grid_columnconfigure(1, weight=1)

        self._label(self.bulk_settings_card, "Preset").grid(
            row=1, column=0, padx=(18, 8), pady=(6, 4), sticky="w"
        )
        self._label(self.bulk_settings_card, "Format").grid(
            row=1, column=1, padx=(8, 18), pady=(6, 4), sticky="w"
        )

        self.bulk_preset_menu = self._option_menu(
            self.bulk_settings_card,
            self.bulk_preset_var,
            list(PRESETS.keys()),
            self.apply_bulk_preset,
        )
        self.bulk_preset_menu.grid(row=2, column=0, padx=(18, 8), pady=(0, 12), sticky="ew")

        self.bulk_format_menu = self._option_menu(
            self.bulk_settings_card,
            self.bulk_format_var,
            ["JPEG", "PNG"],
        )
        self.bulk_format_menu.grid(row=2, column=1, padx=(8, 18), pady=(0, 12), sticky="ew")

        self._label(self.bulk_settings_card, "Width (px)").grid(
            row=3, column=0, padx=(18, 8), pady=(2, 4), sticky="w"
        )
        self._label(self.bulk_settings_card, "Height (px)").grid(
            row=3, column=1, padx=(8, 18), pady=(2, 4), sticky="w"
        )

        self.bulk_width_entry = self._entry(self.bulk_settings_card, self.bulk_width_var)
        self.bulk_width_entry.grid(row=4, column=0, padx=(18, 8), pady=(0, 12), sticky="ew")
        self.bulk_height_entry = self._entry(self.bulk_settings_card, self.bulk_height_var)
        self.bulk_height_entry.grid(row=4, column=1, padx=(8, 18), pady=(0, 12), sticky="ew")

        self.bulk_ratio_checkbox = ctk.CTkCheckBox(
            self.bulk_settings_card,
            text="Maintain aspect ratio",
            variable=self.bulk_keep_ratio_var,
            font=self.font_normal,
            corner_radius=6,
        )
        self.bulk_ratio_checkbox.grid(
            row=5, column=0, columnspan=2, padx=18, pady=(2, 18), sticky="w"
        )

        self.bulk_output_card = self._create_card(
            self.bulk_controls_column, "3  Preview and save", 2
        )
        self.bulk_output_card.grid_columnconfigure(0, weight=1)

        self._label(self.bulk_output_card, "Base image name (no extension)").grid(
            row=1, column=0, padx=18, pady=(6, 4), sticky="w"
        )
        self.bulk_output_entry = self._entry(
            self.bulk_output_card,
            self.bulk_output_name_var,
            placeholder="Example: resized_image",
        )
        self.bulk_output_entry.grid(row=2, column=0, padx=18, pady=(0, 12), sticky="ew")

        self.bulk_preview_button = self._button(
            self.bulk_output_card,
            "Preview First Image",
            self.preview_bulk_image,
            secondary=True,
        )
        self.bulk_preview_button.grid(row=3, column=0, padx=18, pady=6, sticky="ew")

        self.bulk_save_button = self._button(
            self.bulk_output_card,
            "Resize and Save Images",
            self.bulk_resize_clicked,
        )
        self.bulk_save_button.grid(row=4, column=0, padx=18, pady=6, sticky="ew")

        self.bulk_save_note = ctk.CTkLabel(
            self.bulk_output_card,
            text=f"Saved images go to the '{OUTPUT_FOLDER}' folder.",
            font=self.font_small,
            wraplength=360,
        )
        self.bulk_save_note.grid(row=5, column=0, padx=18, pady=(8, 18))

        self.bulk_preview_card = ctk.CTkFrame(tab, corner_radius=18, border_width=1)
        self.bulk_preview_card.grid(row=0, column=1, padx=(8, 10), pady=10, sticky="nsew")
        self.bulk_preview_card.grid_columnconfigure(0, weight=1)
        self.bulk_preview_card.grid_rowconfigure(1, weight=1)

        self.bulk_preview_heading = ctk.CTkLabel(
            self.bulk_preview_card,
            text="Folder Preview",
            font=self.font_section,
        )
        self.bulk_preview_heading.grid(row=0, column=0, padx=18, pady=(16, 8), sticky="w")

        self.bulk_preview_panel = ctk.CTkFrame(
            self.bulk_preview_card,
            corner_radius=16,
            border_width=1,
        )
        self.bulk_preview_panel.grid(row=1, column=0, padx=18, pady=(4, 18), sticky="nsew")
        self.bulk_preview_panel.grid_columnconfigure(0, weight=1)
        self.bulk_preview_panel.grid_rowconfigure(0, weight=1)

        self.bulk_preview_label = ctk.CTkLabel(
            self.bulk_preview_panel,
            text="The first supported image in the folder will appear here",
            font=self.font_normal,
            wraplength=420,
        )
        self.bulk_preview_label.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)


    def _build_transparency_tab(self):
        tab = self.transparency_tab
        tab.grid_columnconfigure(0, weight=0)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        self.transparency_controls = ctk.CTkScrollableFrame(
            tab,
            width=360,
            corner_radius=16,
            fg_color="transparent",
        )
        self.transparency_controls.grid(
            row=0, column=0, padx=(10, 8), pady=10, sticky="nsw"
        )
        self.transparency_controls.grid_columnconfigure(0, weight=1)

        input_card = self._create_card(
            self.transparency_controls, "1  Choose an image", 0
        )
        input_card.grid_columnconfigure(0, weight=1)

        self._label(input_card, "Source image").grid(
            row=1, column=0, padx=18, pady=(6, 4), sticky="w"
        )
        self.transparency_input_entry = self._entry(
            input_card,
            self.transparency_input_path_var,
            placeholder="Select a JPG, JPEG, or PNG image",
        )
        self.transparency_input_entry.grid(
            row=2, column=0, padx=18, pady=(0, 10), sticky="ew"
        )
        self.transparency_browse_button = self._button(
            input_card,
            "Load Image",
            self.browse_transparency_image,
        )
        self.transparency_browse_button.grid(
            row=3, column=0, padx=18, pady=(0, 18), sticky="ew"
        )

        brush_card = self._create_card(
            self.transparency_controls, "2  Paint transparency", 1
        )
        brush_card.grid_columnconfigure(0, weight=1)

        self.transparency_help = ctk.CTkLabel(
            brush_card,
            text=(
                "Choose Erase to remove pixels or Restore to paint them back. "
                "The checkerboard represents true transparency."
            ),
            font=self.font_small,
            justify="left",
            wraplength=300,
        )
        self.transparency_help.grid(
            row=1, column=0, padx=18, pady=(6, 12), sticky="w"
        )

        self._label(brush_card, "Brush mode").grid(
            row=2, column=0, padx=18, pady=(0, 4), sticky="w"
        )
        self.transparency_tool_menu = self._option_menu(
            brush_card,
            self.transparency_tool_var,
            ["Erase", "Restore"],
            self.on_transparency_tool_changed,
        )
        self.transparency_tool_menu.grid(
            row=3, column=0, padx=18, pady=(0, 12), sticky="ew"
        )

        self.transparency_brush_label = self._label(
            brush_card, "Brush size: 40 px"
        )
        self.transparency_brush_label.grid(
            row=4, column=0, padx=18, pady=(0, 4), sticky="w"
        )
        self.transparency_brush_slider = ctk.CTkSlider(
            brush_card,
            from_=5,
            to=200,
            number_of_steps=195,
            variable=self.transparency_brush_size_var,
            command=self.on_transparency_brush_changed,
        )
        self.transparency_brush_slider.grid(
            row=5, column=0, padx=18, pady=(0, 14), sticky="ew"
        )

        self.transparency_history_row = ctk.CTkFrame(brush_card, fg_color="transparent")
        self.transparency_history_row.grid(row=6, column=0, padx=18, pady=(0, 10), sticky="ew")
        self.transparency_history_row.grid_columnconfigure((0, 1), weight=1)
        self.transparency_undo_button = self._button(
            self.transparency_history_row, "Undo", self.undo_transparency, secondary=True
        )
        self.transparency_undo_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        self.transparency_redo_button = self._button(
            self.transparency_history_row, "Redo", self.redo_transparency, secondary=True
        )
        self.transparency_redo_button.grid(row=0, column=1, padx=(5, 0), sticky="ew")

        self.transparency_reset_button = self._button(
            brush_card,
            "Reset Removed Areas",
            self.reset_transparency_mask,
            secondary=True,
        )
        self.transparency_reset_button.grid(
            row=7, column=0, padx=18, pady=(0, 18), sticky="ew"
        )

        save_card = self._create_card(
            self.transparency_controls, "3  Save transparent PNG", 2
        )
        save_card.grid_columnconfigure(0, weight=1)

        self._label(save_card, "Output name (no extension)").grid(
            row=1, column=0, padx=18, pady=(6, 4), sticky="w"
        )
        self.transparency_output_entry = self._entry(
            save_card,
            self.transparency_output_name_var,
            placeholder="Example: logo_transparent",
        )
        self.transparency_output_entry.grid(
            row=2, column=0, padx=18, pady=(0, 12), sticky="ew"
        )
        self.transparency_save_button = self._button(
            save_card,
            "Save Transparent PNG",
            self.save_transparent_png,
        )
        self.transparency_save_button.grid(
            row=3, column=0, padx=18, pady=(0, 10), sticky="ew"
        )
        self.transparency_note = ctk.CTkLabel(
            save_card,
            text=f"Saved PNG files go to the '{OUTPUT_FOLDER}' folder.",
            font=self.font_small,
            wraplength=300,
        )
        self.transparency_note.grid(
            row=4, column=0, padx=18, pady=(0, 18)
        )

        self.transparency_editor_card = ctk.CTkFrame(
            tab, corner_radius=18, border_width=1
        )
        self.transparency_editor_card.grid(
            row=0, column=1, padx=(8, 10), pady=10, sticky="nsew"
        )
        self.transparency_editor_card.grid_columnconfigure(0, weight=1)
        self.transparency_editor_card.grid_rowconfigure(2, weight=1)

        self.transparency_heading = ctk.CTkLabel(
            self.transparency_editor_card,
            text="Transparency Canvas",
            font=self.font_section,
        )
        self.transparency_heading.grid(
            row=0, column=0, padx=18, pady=(16, 8), sticky="w"
        )

        self.transparency_zoom_row = ctk.CTkFrame(
            self.transparency_editor_card, fg_color="transparent"
        )
        self.transparency_zoom_row.grid(row=1, column=0, padx=18, pady=(0, 6), sticky="ew")
        self.transparency_zoom_row.grid_columnconfigure(3, weight=1)
        self.zoom_out_button = self._button(
            self.transparency_zoom_row, "−", self.zoom_out_transparency, width=46, secondary=True
        )
        self.zoom_out_button.grid(row=0, column=0, padx=(0, 5))
        self.zoom_in_button = self._button(
            self.transparency_zoom_row, "+", self.zoom_in_transparency, width=46, secondary=True
        )
        self.zoom_in_button.grid(row=0, column=1, padx=5)
        self.zoom_fit_button = self._button(
            self.transparency_zoom_row, "Fit", self.fit_transparency_to_canvas, width=70, secondary=True
        )
        self.zoom_fit_button.grid(row=0, column=2, padx=5)
        self.transparency_zoom_label = ctk.CTkLabel(
            self.transparency_zoom_row,
            textvariable=self.transparency_zoom_label_var,
            font=self.font_normal,
        )
        self.transparency_zoom_label.grid(row=0, column=4, padx=(10, 0), sticky="e")

        self.transparency_canvas_frame = ctk.CTkFrame(
            self.transparency_editor_card,
            corner_radius=12,
            border_width=1,
        )
        self.transparency_canvas_frame.grid(
            row=2, column=0, padx=18, pady=(4, 18), sticky="nsew"
        )
        self.transparency_canvas_frame.grid_columnconfigure(0, weight=1)
        self.transparency_canvas_frame.grid_rowconfigure(0, weight=1)

        self.transparency_canvas = tk.Canvas(
            self.transparency_canvas_frame,
            highlightthickness=0,
            cursor="crosshair",
            xscrollincrement=1,
            yscrollincrement=1,
        )
        self.transparency_canvas.grid(row=0, column=0, sticky="nsew")

        self.transparency_v_scrollbar = ctk.CTkScrollbar(
            self.transparency_canvas_frame,
            orientation="vertical",
            command=self.transparency_canvas.yview,
        )
        self.transparency_v_scrollbar.grid(row=0, column=1, sticky="ns")

        self.transparency_h_scrollbar = ctk.CTkScrollbar(
            self.transparency_canvas_frame,
            orientation="horizontal",
            command=self.transparency_canvas.xview,
        )
        self.transparency_h_scrollbar.grid(row=1, column=0, sticky="ew")

        self.transparency_canvas.configure(
            xscrollcommand=self.transparency_h_scrollbar.set,
            yscrollcommand=self.transparency_v_scrollbar.set,
        )

        self.transparency_canvas.bind("<Configure>", self._on_transparency_canvas_resize)
        self.transparency_canvas.bind("<ButtonPress-1>", self._start_transparency_stroke)
        self.transparency_canvas.bind("<B1-Motion>", self._continue_transparency_stroke)
        self.transparency_canvas.bind("<ButtonRelease-1>", self._end_transparency_stroke)
        self.transparency_canvas.bind("<MouseWheel>", self._on_transparency_mousewheel)
        self.transparency_canvas.bind("<Shift-MouseWheel>", self._on_transparency_shift_mousewheel)
        self.transparency_canvas.bind("<Control-MouseWheel>", self._on_transparency_ctrl_mousewheel)
        self.bind_all("<Control-z>", lambda _event: self.undo_transparency())
        self.bind_all("<Control-y>", lambda _event: self.redo_transparency())

    def _build_settings_tab(self):
        tab = self.settings_tab
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(2, weight=1)

        self.settings_intro = ctk.CTkLabel(
            tab,
            text="Personalize your Chimera workspace",
            font=self.font_section,
        )
        self.settings_intro.grid(row=0, column=0, padx=26, pady=(24, 8), sticky="w")

        self.settings_description = ctk.CTkLabel(
            tab,
            text=(
                "Appearance changes apply immediately. More personal settings can be "
                "added here as the program grows."
            ),
            font=self.font_normal,
            justify="left",
            wraplength=760,
        )
        self.settings_description.grid(row=1, column=0, padx=26, pady=(0, 14), sticky="w")

        self.appearance_card = ctk.CTkFrame(tab, corner_radius=18, border_width=1)
        self.appearance_card.grid(row=2, column=0, padx=26, pady=10, sticky="new")
        self.appearance_card.grid_columnconfigure(1, weight=1)

        self.appearance_heading = ctk.CTkLabel(
            self.appearance_card,
            text="Appearance",
            font=self.font_section,
        )
        self.appearance_heading.grid(row=0, column=0, columnspan=2, padx=20, pady=(18, 14), sticky="w")

        self._label(self.appearance_card, "Color scheme").grid(
            row=1, column=0, padx=20, pady=10, sticky="w"
        )
        self.theme_menu = self._option_menu(
            self.appearance_card,
            self.theme_var,
            list(THEMES.keys()),
            self.on_theme_selected,
            width=230,
        )
        self.theme_menu.grid(row=1, column=1, padx=20, pady=10, sticky="e")

        self._label(self.appearance_card, "Text font size").grid(
            row=2, column=0, padx=20, pady=10, sticky="w"
        )
        self.font_size_menu = self._option_menu(
            self.appearance_card,
            self.font_size_var,
            list(FONT_SIZES.keys()),
            self.on_font_size_selected,
            width=230,
        )
        self.font_size_menu.grid(row=2, column=1, padx=20, pady=10, sticky="e")

        self.settings_button_row = ctk.CTkFrame(self.appearance_card, fg_color="transparent")
        self.settings_button_row.grid(row=3, column=0, columnspan=2, pady=(18, 20))

        self.restore_defaults_button = self._button(
            self.settings_button_row,
            "Restore Defaults",
            self.restore_default_settings,
            width=180,
            secondary=True,
        )
        self.restore_defaults_button.grid(row=0, column=0, padx=8)

        self.settings_status = ctk.CTkLabel(
            tab,
            text="Current profile: Chimera Default · Medium text",
            font=self.font_small,
        )
        self.settings_status.grid(row=3, column=0, padx=26, pady=16, sticky="w")

    # -------------------------
    # Widget helpers
    # -------------------------
    def _create_card(self, parent, heading, row, sticky="ew"):
        card = ctk.CTkFrame(parent, corner_radius=18, border_width=1)
        card.grid(row=row, column=0, padx=14, pady=9, sticky=sticky)
        heading_label = ctk.CTkLabel(card, text=heading, font=self.font_section)
        heading_label.grid(row=0, column=0, columnspan=4, padx=18, pady=(16, 8), sticky="w")
        return card

    def _label(self, parent, text):
        return ctk.CTkLabel(parent, text=text, font=self.font_normal)

    def _entry(self, parent, variable, placeholder=""):
        return ctk.CTkEntry(
            parent,
            textvariable=variable,
            placeholder_text=placeholder,
            height=38,
            corner_radius=10,
            border_width=1,
            font=self.font_normal,
        )

    def _button(self, parent, text, command, width=150, secondary=False):
        button = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            height=40,
            corner_radius=12,
            border_width=1 if secondary else 0,
            font=self.font_bold,
        )
        button._chimera_secondary = secondary
        return button

    def _option_menu(self, parent, variable, values, command=None, width=170):
        return ctk.CTkOptionMenu(
            parent,
            variable=variable,
            values=values,
            command=command,
            width=width,
            height=38,
            corner_radius=10,
            font=self.font_normal,
            dropdown_font=self.font_normal,
            dynamic_resizing=False,
        )

    # -------------------------
    # Theme and font controls
    # -------------------------
    def on_theme_selected(self, theme_name):
        self.current_theme_name = theme_name
        self.current_theme = THEMES[theme_name]
        ctk.set_appearance_mode(self.current_theme["appearance"])
        self.apply_theme()
        self._update_settings_status()

    def on_font_size_selected(self, size_name):
        self.current_font_size_name = size_name
        self.base_font_size = FONT_SIZES[size_name]
        self._update_font_objects()
        self._update_settings_status()

    def restore_default_settings(self):
        self.theme_var.set("Chimera Default")
        self.font_size_var.set("Medium")
        self.on_theme_selected("Chimera Default")
        self.on_font_size_selected("Medium")

    def _update_settings_status(self):
        self.settings_status.configure(
            text=(
                f"Current profile: {self.current_theme_name} · "
                f"{self.current_font_size_name} text"
            )
        )

    def _update_font_objects(self):
        size = self.base_font_size
        self.font_normal.configure(size=size)
        self.font_small.configure(size=max(10, size - 2))
        self.font_bold.configure(size=size)
        self.font_section.configure(size=size + 2)
        self.font_title.configure(size=size + 15)
        self.font_subtitle.configure(size=size)

    def apply_theme(self):
        t = self.current_theme
        self.configure(fg_color=t["window"])

        self.header_frame.configure(fg_color=t["window"])
        self.title_label.configure(text_color=t["text"])
        self.subtitle_label.configure(text_color=t["muted"])

        self.tabview.configure(
            fg_color=t["window"],
            border_color=t["border"],
            segmented_button_fg_color=t["surface_alt"],
            segmented_button_selected_color=t["accent"],
            segmented_button_selected_hover_color=t["accent_hover"],
            segmented_button_unselected_color=t["surface_alt"],
            segmented_button_unselected_hover_color=t["entry_border"],
            text_color=t["text"],
        )

        self._apply_theme_recursive(self)

        self.single_preview_panel.configure(fg_color=t["preview"], border_color=t["border"])
        self.bulk_preview_panel.configure(fg_color=t["preview"], border_color=t["border"])
        self.single_save_note.configure(text_color=t["muted"])
        self.bulk_save_note.configure(text_color=t["muted"])
        self.settings_description.configure(text_color=t["muted"])
        self.settings_status.configure(text_color=t["muted"])
        self.transparency_help.configure(text_color=t["muted"])
        self.transparency_note.configure(text_color=t["muted"])
        self.transparency_canvas.configure(bg=t["preview"])

    def _apply_theme_recursive(self, widget):
        t = self.current_theme

        for child in widget.winfo_children():
            try:
                if isinstance(child, ctk.CTkFrame):
                    if child.cget("fg_color") != "transparent":
                        child.configure(fg_color=t["surface"], border_color=t["border"])

                elif isinstance(child, ctk.CTkLabel):
                    if child is not self.title_shadow:
                        child.configure(text_color=t["text"])

                elif isinstance(child, ctk.CTkEntry):
                    child.configure(
                        fg_color=t["entry"],
                        border_color=t["entry_border"],
                        text_color=t["text"],
                        placeholder_text_color=t["muted"],
                    )

                elif isinstance(child, ctk.CTkButton):
                    if getattr(child, "_chimera_secondary", False):
                        child.configure(
                            fg_color=t["surface_alt"],
                            hover_color=t["entry_border"],
                            border_color=t["accent"],
                            text_color=t["text"],
                        )
                    else:
                        child.configure(
                            fg_color=t["accent"],
                            hover_color=t["accent_hover"],
                            text_color="#151515",
                        )

                elif isinstance(child, ctk.CTkOptionMenu):
                    child.configure(
                        fg_color=t["entry"],
                        button_color=t["accent"],
                        button_hover_color=t["accent_hover"],
                        dropdown_fg_color=t["surface_alt"],
                        dropdown_hover_color=t["accent"],
                        text_color=t["text"],
                        dropdown_text_color=t["text"],
                    )

                elif isinstance(child, ctk.CTkSlider):
                    child.configure(
                        fg_color=t["entry_border"],
                        progress_color=t["accent"],
                        button_color=t["accent"],
                        button_hover_color=t["accent_hover"],
                    )

                elif isinstance(child, ctk.CTkCheckBox):
                    child.configure(
                        fg_color=t["accent"],
                        hover_color=t["accent_hover"],
                        border_color=t["entry_border"],
                        text_color=t["text"],
                    )
            except (tk.TclError, ValueError):
                pass

            self._apply_theme_recursive(child)

    # -------------------------
    # Shared validation/helpers
    # -------------------------
    @staticmethod
    def _parse_dimensions(width_text, height_text):
        try:
            width = int(width_text)
            height = int(height_text)
        except ValueError as exc:
            raise ValueError("Width and height must be whole numbers.") from exc

        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be greater than zero.")

        return width, height

    @staticmethod
    def _find_first_supported_image(folder_path):
        for filename in sorted(os.listdir(folder_path)):
            if filename.lower().endswith(SUPPORTED_EXTENSIONS):
                return os.path.join(folder_path, filename)
        return None

    @staticmethod
    def _build_preview_image(
        input_path, width, height, keep_ratio, max_preview_width, max_preview_height
    ):
        with Image.open(input_path) as img:
            preview_img = img.copy()

        if keep_ratio:
            preview_img.thumbnail((width, height), Image.Resampling.LANCZOS)
        else:
            preview_img = preview_img.resize((width, height), Image.Resampling.LANCZOS)

        preview_img.thumbnail(
            (max_preview_width, max_preview_height),
            Image.Resampling.LANCZOS,
        )
        return preview_img

    # -------------------------
    # Single image actions
    # -------------------------
    def browse_input_file(self):
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[
                ("Image Files", "*.jpg *.jpeg *.png"),
                ("All Files", "*.*"),
            ],
        )
        if file_path:
            self.input_path_var.set(file_path)

    def apply_single_preset(self, preset):
        dimensions = PRESETS.get(preset)
        if dimensions:
            self.single_width_var.set(str(dimensions[0]))
            self.single_height_var.set(str(dimensions[1]))

    def preview_single_image(self):
        input_path = self.input_path_var.get().strip()
        if not input_path:
            messagebox.showerror("Missing Input", "Please choose an input image.")
            return

        try:
            width, height = self._parse_dimensions(
                self.single_width_var.get(),
                self.single_height_var.get(),
            )
            preview_img = self._build_preview_image(
                input_path,
                width,
                height,
                self.single_keep_ratio_var.get(),
                max(250, self.single_preview_panel.winfo_width() - 36),
                max(250, self.single_preview_panel.winfo_height() - 36),
            )
            self.preview_ctk_image = ctk.CTkImage(
                light_image=preview_img,
                dark_image=preview_img,
                size=preview_img.size,
            )
            self.preview_label.configure(image=self.preview_ctk_image, text="")
        except Exception as exc:
            messagebox.showerror("Preview Error", f"Could not preview image:\n{exc}")

    def resize_and_save_clicked(self):
        input_path = self.input_path_var.get().strip()
        output_name = self.output_name_var.get().strip()

        if not input_path:
            messagebox.showerror("Missing Input", "Please choose an input image.")
            return
        if not output_name:
            messagebox.showerror("Missing Output Name", "Please enter an output image name.")
            return

        try:
            width, height = self._parse_dimensions(
                self.single_width_var.get(),
                self.single_height_var.get(),
            )
        except ValueError as exc:
            messagebox.showerror("Invalid Size", str(exc))
            return

        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        format_choice = self.single_format_var.get()
        extension = ".png" if format_choice == "PNG" else ".jpg"
        save_format = "PNG" if format_choice == "PNG" else "JPEG"
        output_path = os.path.join(OUTPUT_FOLDER, f"{output_name}{extension}")

        try:
            resize_image(
                input_path,
                output_path,
                width,
                height,
                save_format,
                self.single_keep_ratio_var.get(),
            )
            messagebox.showinfo(
                "Success",
                f"Image resized and saved successfully!\n\nSaved to:\n{output_path}",
            )
        except Exception as exc:
            messagebox.showerror("Error", f"Something went wrong:\n{exc}")

    # -------------------------
    # Bulk image actions
    # -------------------------
    def browse_bulk_folder(self):
        folder_path = filedialog.askdirectory(title="Select folder with images")
        if folder_path:
            self.bulk_folder_path_var.set(folder_path)

    def apply_bulk_preset(self, preset):
        dimensions = PRESETS.get(preset)
        if dimensions:
            self.bulk_width_var.set(str(dimensions[0]))
            self.bulk_height_var.set(str(dimensions[1]))

    def preview_bulk_image(self):
        folder_path = self.bulk_folder_path_var.get().strip()
        if not folder_path:
            messagebox.showerror("Missing Folder", "Please select a folder.")
            return

        try:
            width, height = self._parse_dimensions(
                self.bulk_width_var.get(),
                self.bulk_height_var.get(),
            )
            first_image_path = self._find_first_supported_image(folder_path)
            if not first_image_path:
                messagebox.showerror(
                    "No Images Found",
                    "No JPG, JPEG, or PNG images were found in this folder.",
                )
                return

            preview_img = self._build_preview_image(
                first_image_path,
                width,
                height,
                self.bulk_keep_ratio_var.get(),
                max(250, self.bulk_preview_panel.winfo_width() - 36),
                max(250, self.bulk_preview_panel.winfo_height() - 36),
            )
            self.bulk_preview_ctk_image = ctk.CTkImage(
                light_image=preview_img,
                dark_image=preview_img,
                size=preview_img.size,
            )
            self.bulk_preview_label.configure(image=self.bulk_preview_ctk_image, text="")
        except Exception as exc:
            messagebox.showerror("Preview Error", f"Could not preview image:\n{exc}")

    def bulk_resize_clicked(self):
        folder_path = self.bulk_folder_path_var.get().strip()
        output_name = self.bulk_output_name_var.get().strip()

        if not folder_path:
            messagebox.showerror("Missing Folder", "Please select a folder.")
            return
        if not output_name:
            messagebox.showerror(
                "Missing Output Name",
                "Please enter a base output image name.",
            )
            return

        try:
            width, height = self._parse_dimensions(
                self.bulk_width_var.get(),
                self.bulk_height_var.get(),
            )
        except ValueError as exc:
            messagebox.showerror("Invalid Size", str(exc))
            return

        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        format_choice = self.bulk_format_var.get()
        extension = ".png" if format_choice == "PNG" else ".jpg"
        save_format = "PNG" if format_choice == "PNG" else "JPEG"

        count = 0
        try:
            for filename in sorted(os.listdir(folder_path)):
                if not filename.lower().endswith(SUPPORTED_EXTENSIONS):
                    continue

                count += 1
                input_path = os.path.join(folder_path, filename)
                output_path = os.path.join(
                    OUTPUT_FOLDER,
                    f"{output_name}_{count}{extension}",
                )
                resize_image(
                    input_path,
                    output_path,
                    width,
                    height,
                    save_format,
                    self.bulk_keep_ratio_var.get(),
                )

            if count == 0:
                messagebox.showwarning(
                    "No Images Found",
                    "No JPG, JPEG, or PNG images were found in this folder.",
                )
                return

            messagebox.showinfo(
                "Success",
                f"Bulk resize complete!\n\nImages resized: {count}",
            )
        except Exception as exc:
            messagebox.showerror("Error", f"Something went wrong:\n{exc}")



    # -------------------------
    # Transparency editor actions
    # -------------------------
    def browse_transparency_image(self):
        file_path = filedialog.askopenfilename(
            title="Select an image for transparency editing",
            filetypes=[
                ("Image Files", "*.jpg *.jpeg *.png"),
                ("All Files", "*.*"),
            ],
        )
        if not file_path:
            return

        try:
            with Image.open(file_path) as image:
                self.transparency_source_image = image.convert("RGBA")

            self.transparency_input_path_var.set(file_path)
            self.transparency_mask = Image.new(
                "L", self.transparency_source_image.size, 255
            )
            self.transparency_zoom = 1.0
            self.transparency_undo_stack.clear()
            self.transparency_redo_stack.clear()
            self._update_history_buttons()
            self._render_transparency_editor()
        except Exception as exc:
            messagebox.showerror(
                "Image Error", f"Could not load the selected image:\n{exc}"
            )

    def on_transparency_brush_changed(self, value):
        brush_size = int(float(value))
        self.transparency_brush_label.configure(
            text=f"Brush size: {brush_size} px"
        )

    def on_transparency_tool_changed(self, tool_name):
        self.transparency_tool = tool_name

    def _update_history_buttons(self):
        if hasattr(self, "transparency_undo_button"):
            self.transparency_undo_button.configure(
                state="normal" if self.transparency_undo_stack else "disabled"
            )
            self.transparency_redo_button.configure(
                state="normal" if self.transparency_redo_stack else "disabled"
            )

    def _push_transparency_history(self, snapshot):
        if snapshot is None:
            return
        self.transparency_undo_stack.append(snapshot)
        if len(self.transparency_undo_stack) > self.transparency_history_limit:
            self.transparency_undo_stack.pop(0)
        self.transparency_redo_stack.clear()
        self._update_history_buttons()

    def undo_transparency(self):
        if self.transparency_mask is None or not self.transparency_undo_stack:
            return
        self.transparency_redo_stack.append(self.transparency_mask.copy())
        self.transparency_mask = self.transparency_undo_stack.pop()
        self._update_history_buttons()
        self._render_transparency_editor()

    def redo_transparency(self):
        if self.transparency_mask is None or not self.transparency_redo_stack:
            return
        self.transparency_undo_stack.append(self.transparency_mask.copy())
        self.transparency_mask = self.transparency_redo_stack.pop()
        self._update_history_buttons()
        self._render_transparency_editor()

    def zoom_in_transparency(self):
        if self.transparency_source_image is None:
            return
        self.transparency_zoom = min(8.0, self.transparency_zoom * 1.25)
        self._render_transparency_editor()

    def zoom_out_transparency(self):
        if self.transparency_source_image is None:
            return
        self.transparency_zoom = max(0.25, self.transparency_zoom / 1.25)
        self._render_transparency_editor()

    def fit_transparency_to_canvas(self):
        self.transparency_zoom = 1.0
        self._render_transparency_editor()

    def reset_transparency_mask(self):
        if self.transparency_source_image is None:
            messagebox.showinfo(
                "No Image Loaded", "Load an image before resetting the mask."
            )
            return

        previous_mask = self.transparency_mask.copy()
        self.transparency_mask = Image.new(
            "L", self.transparency_source_image.size, 255
        )
        self._push_transparency_history(previous_mask)
        self._render_transparency_editor()

    def _on_transparency_mousewheel(self, event):
        # Standard wheel movement pans vertically through a zoomed image.
        direction = -1 if event.delta > 0 else 1
        self.transparency_canvas.yview_scroll(direction * 3, "units")
        return "break"

    def _on_transparency_shift_mousewheel(self, event):
        # Shift + wheel pans horizontally.
        direction = -1 if event.delta > 0 else 1
        self.transparency_canvas.xview_scroll(direction * 3, "units")
        return "break"

    def _on_transparency_ctrl_mousewheel(self, event):
        # Ctrl + wheel keeps convenient mouse-wheel zooming available.
        if event.delta > 0:
            self.zoom_in_transparency()
        elif event.delta < 0:
            self.zoom_out_transparency()
        return "break"

    def _on_transparency_canvas_resize(self, _event=None):
        if self.transparency_source_image is not None:
            self.after_idle(self._render_transparency_editor)
        else:
            self._draw_transparency_placeholder()

    def _draw_transparency_placeholder(self):
        canvas = self.transparency_canvas
        canvas.delete("all")
        width = max(1, canvas.winfo_width())
        height = max(1, canvas.winfo_height())
        canvas.create_text(
            width // 2,
            height // 2,
            text="Load an image to begin removing its background",
            fill=self.current_theme["muted"],
            font=("Segoe UI", self.base_font_size),
            width=max(200, width - 80),
            justify="center",
        )

    @staticmethod
    def _make_checkerboard(width, height, square=16):
        board = Image.new("RGBA", (width, height), (205, 205, 205, 255))
        draw = ImageDraw.Draw(board)
        alternate = (155, 155, 155, 255)
        for y in range(0, height, square):
            for x in range(0, width, square):
                if ((x // square) + (y // square)) % 2:
                    draw.rectangle(
                        (x, y, min(x + square, width), min(y + square, height)),
                        fill=alternate,
                    )
        return board

    def _render_transparency_editor(self):
        if self.transparency_source_image is None or self.transparency_mask is None:
            self._draw_transparency_placeholder()
            return

        canvas_width = max(100, self.transparency_canvas.winfo_width())
        canvas_height = max(100, self.transparency_canvas.winfo_height())
        source_width, source_height = self.transparency_source_image.size

        self.transparency_fit_scale = min(
            (canvas_width - 30) / source_width,
            (canvas_height - 30) / source_height,
        )
        self.transparency_fit_scale = max(0.01, self.transparency_fit_scale)
        self.transparency_scale = self.transparency_fit_scale * self.transparency_zoom
        self.transparency_zoom_label_var.set(f"{int(self.transparency_zoom * 100)}%")

        display_size = (
            max(1, int(source_width * self.transparency_scale)),
            max(1, int(source_height * self.transparency_scale)),
        )
        self.transparency_offset_x = max(0, (canvas_width - display_size[0]) // 2)
        self.transparency_offset_y = max(0, (canvas_height - display_size[1]) // 2)

        edited = self.transparency_source_image.copy()
        edited.putalpha(self.transparency_mask)
        resized = edited.resize(display_size, Image.Resampling.LANCZOS)
        checker = self._make_checkerboard(*display_size)
        checker.alpha_composite(resized)

        self.transparency_display_image = checker
        self.transparency_tk_image = ImageTk.PhotoImage(checker)
        self.transparency_canvas.delete("all")
        self.transparency_canvas.create_image(
            self.transparency_offset_x,
            self.transparency_offset_y,
            anchor="nw",
            image=self.transparency_tk_image,
        )

        content_width = max(canvas_width, self.transparency_offset_x + display_size[0])
        content_height = max(canvas_height, self.transparency_offset_y + display_size[1])
        self.transparency_canvas.configure(
            scrollregion=(0, 0, content_width, content_height)
        )

    def _canvas_to_image_point(self, canvas_x, canvas_y):
        if self.transparency_source_image is None:
            return None

        scrolled_x = self.transparency_canvas.canvasx(canvas_x)
        scrolled_y = self.transparency_canvas.canvasy(canvas_y)
        image_x = (scrolled_x - self.transparency_offset_x) / self.transparency_scale
        image_y = (scrolled_y - self.transparency_offset_y) / self.transparency_scale
        width, height = self.transparency_source_image.size

        if not (0 <= image_x < width and 0 <= image_y < height):
            return None
        return int(image_x), int(image_y)

    def _start_transparency_stroke(self, event):
        point = self._canvas_to_image_point(event.x, event.y)
        self.transparency_last_point = point
        if point is not None:
            self.transparency_stroke_snapshot = self.transparency_mask.copy()
            self._paint_transparency_line(point, point)

    def _continue_transparency_stroke(self, event):
        point = self._canvas_to_image_point(event.x, event.y)
        if point is None:
            return

        start = self.transparency_last_point or point
        self._paint_transparency_line(start, point)
        self.transparency_last_point = point

    def _end_transparency_stroke(self, _event):
        if self.transparency_stroke_snapshot is not None:
            self._push_transparency_history(self.transparency_stroke_snapshot)
        self.transparency_stroke_snapshot = None
        self.transparency_last_point = None

    def _paint_transparency_line(self, start, end):
        if self.transparency_mask is None:
            return

        draw = ImageDraw.Draw(self.transparency_mask)
        brush_size = max(1, int(self.transparency_brush_size_var.get()))
        radius = brush_size // 2
        fill_value = 255 if self.transparency_tool_var.get() == "Restore" else 0
        draw.line((start, end), fill=fill_value, width=brush_size)
        for x, y in (start, end):
            draw.ellipse(
                (x - radius, y - radius, x + radius, y + radius),
                fill=fill_value,
            )
        self._render_transparency_editor()

    def save_transparent_png(self):
        if self.transparency_source_image is None or self.transparency_mask is None:
            messagebox.showerror(
                "No Image Loaded", "Load and edit an image before saving."
            )
            return

        output_name = self.transparency_output_name_var.get().strip()
        if not output_name:
            messagebox.showerror(
                "Missing Output Name", "Please enter an output image name."
            )
            return

        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        output_path = os.path.join(OUTPUT_FOLDER, f"{output_name}.png")

        try:
            output_image = self.transparency_source_image.copy()
            output_image.putalpha(self.transparency_mask)
            output_image.save(output_path, "PNG")
            messagebox.showinfo(
                "Success",
                f"Transparent PNG saved successfully!\n\nSaved to:\n{output_path}",
            )
        except Exception as exc:
            messagebox.showerror(
                "Save Error", f"Could not save the transparent PNG:\n{exc}"
            )

if __name__ == "__main__":
    app = ChimeraImageModifier()
    app.mainloop()
