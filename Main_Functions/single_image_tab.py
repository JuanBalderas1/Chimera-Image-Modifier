import os
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image


# --------------------------------------------------
# Single Image Resize configuration
# --------------------------------------------------

PRESETS = {
    "Custom": None,
    "Thumbnail": (150, 150),
    "Medium": (800, 600),
    "HD": (1920, 1080),
}

DEFAULT_OUTPUT_FOLDER = "Modified Images"


# --------------------------------------------------
# Reusable base resize logic
# --------------------------------------------------

def resize_image(
    input_path,
    output_path,
    width,
    height,
    save_format,
    keep_ratio=False,
):
    """
    Resize and save an image.

    This function is intentionally module-level so sister modules,
    such as bulk_image_tab.py, can reuse the same resize logic.
    """

    with Image.open(input_path) as image:
        working_image = image.copy()

    if keep_ratio:
        working_image.thumbnail(
            (width, height),
            Image.Resampling.LANCZOS,
        )
        resized_image = working_image

    else:
        resized_image = working_image.resize(
            (width, height),
            Image.Resampling.LANCZOS,
        )

    # JPEG cannot preserve transparency or palette mode.
    if save_format == "JPEG" and resized_image.mode not in ("RGB", "L"):
        resized_image = resized_image.convert("RGB")

    resized_image.save(
        output_path,
        save_format,
    )


# --------------------------------------------------
# Single Image Resize tab
# --------------------------------------------------

class SingleImageTab(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        font_normal,
        font_small,
        font_bold,
        font_section,
        output_folder=DEFAULT_OUTPUT_FOLDER,
    ):
        super().__init__(
            parent,
            fg_color="transparent",
        )

        # Shared application fonts
        self.font_normal = font_normal
        self.font_small = font_small
        self.font_bold = font_bold
        self.font_section = font_section

        self.output_folder = output_folder

        # Prevent preview image garbage collection.
        self.preview_ctk_image = None

        self._create_variables()
        self._configure_workspace()
        self._build_interface()

    # ==================================================
    # Variables
    # ==================================================

    def _create_variables(self):
        self.input_path_var = tk.StringVar()
        self.output_name_var = tk.StringVar()

        self.width_var = tk.StringVar(value="800")
        self.height_var = tk.StringVar(value="600")

        self.format_var = tk.StringVar(value="JPEG")
        self.keep_ratio_var = tk.BooleanVar(value=False)
        self.preset_var = tk.StringVar(value="Custom")

    # ==================================================
    # Workspace
    # ==================================================

    def _configure_workspace(self):
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=1)

        self.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        self.grid_columnconfigure(
            0,
            weight=1,
            uniform="single_workspace",
        )
        self.grid_columnconfigure(
            1,
            weight=1,
            uniform="single_workspace",
        )
        self.grid_rowconfigure(0, weight=1)

    # ==================================================
    # Interface construction
    # ==================================================

    def _build_interface(self):
        self._build_controls_column()
        self._build_preview_column()

    def _build_controls_column(self):
        self.controls_column = ctk.CTkScrollableFrame(
            self,
            corner_radius=16,
            fg_color="transparent",
        )
        self.controls_column.grid(
            row=0,
            column=0,
            padx=(10, 8),
            pady=10,
            sticky="nsew",
        )
        self.controls_column.grid_columnconfigure(0, weight=1)

        self._build_input_card()
        self._build_resize_settings_card()
        self._build_output_card()

    def _build_input_card(self):
        self.input_card = self._create_card(
            self.controls_column,
            "1  Choose an image",
            0,
        )
        self.input_card.grid_columnconfigure(0, weight=1)

        self.input_label = self._label(
            self.input_card,
            "Input image",
        )
        self.input_label.grid(
            row=1,
            column=0,
            padx=18,
            pady=(6, 4),
            sticky="w",
        )

        self.input_entry = self._entry(
            self.input_card,
            self.input_path_var,
            placeholder="Select a JPG, JPEG, or PNG image",
        )
        self.input_entry.grid(
            row=2,
            column=0,
            padx=18,
            pady=(0, 10),
            sticky="ew",
        )

        self.browse_button = self._button(
            self.input_card,
            "Select Image",
            self.browse_input_file,
        )
        self.browse_button.grid(
            row=3,
            column=0,
            padx=18,
            pady=(0, 18),
            sticky="ew",
        )

    def _build_resize_settings_card(self):
        self.settings_card = self._create_card(
            self.controls_column,
            "2  Resize settings",
            1,
        )

        self.settings_card.grid_columnconfigure(0, weight=1)
        self.settings_card.grid_columnconfigure(1, weight=1)

        self._label(
            self.settings_card,
            "Preset",
        ).grid(
            row=1,
            column=0,
            padx=(18, 8),
            pady=(6, 4),
            sticky="w",
        )

        self._label(
            self.settings_card,
            "Format",
        ).grid(
            row=1,
            column=1,
            padx=(8, 18),
            pady=(6, 4),
            sticky="w",
        )

        self.preset_menu = self._option_menu(
            self.settings_card,
            self.preset_var,
            list(PRESETS.keys()),
            self.apply_preset,
        )
        self.preset_menu.grid(
            row=2,
            column=0,
            padx=(18, 8),
            pady=(0, 12),
            sticky="ew",
        )

        self.format_menu = self._option_menu(
            self.settings_card,
            self.format_var,
            ["JPEG", "PNG"],
        )
        self.format_menu.grid(
            row=2,
            column=1,
            padx=(8, 18),
            pady=(0, 12),
            sticky="ew",
        )

        self._label(
            self.settings_card,
            "Width (px)",
        ).grid(
            row=3,
            column=0,
            padx=(18, 8),
            pady=(2, 4),
            sticky="w",
        )

        self._label(
            self.settings_card,
            "Height (px)",
        ).grid(
            row=3,
            column=1,
            padx=(8, 18),
            pady=(2, 4),
            sticky="w",
        )

        self.width_entry = self._entry(
            self.settings_card,
            self.width_var,
        )
        self.width_entry.grid(
            row=4,
            column=0,
            padx=(18, 8),
            pady=(0, 12),
            sticky="ew",
        )

        self.height_entry = self._entry(
            self.settings_card,
            self.height_var,
        )
        self.height_entry.grid(
            row=4,
            column=1,
            padx=(8, 18),
            pady=(0, 12),
            sticky="ew",
        )

        self.ratio_checkbox = ctk.CTkCheckBox(
            self.settings_card,
            text="Maintain aspect ratio",
            variable=self.keep_ratio_var,
            font=self.font_normal,
            corner_radius=6,
        )
        self.ratio_checkbox.grid(
            row=5,
            column=0,
            columnspan=2,
            padx=18,
            pady=(2, 18),
            sticky="w",
        )

    def _build_output_card(self):
        self.output_card = self._create_card(
            self.controls_column,
            "3  Preview and save",
            2,
        )
        self.output_card.grid_columnconfigure(0, weight=1)

        self._label(
            self.output_card,
            "New image name (no extension)",
        ).grid(
            row=1,
            column=0,
            padx=18,
            pady=(6, 4),
            sticky="w",
        )

        self.output_entry = self._entry(
            self.output_card,
            self.output_name_var,
            placeholder="Example: vacation_photo_resized",
        )
        self.output_entry.grid(
            row=2,
            column=0,
            padx=18,
            pady=(0, 12),
            sticky="ew",
        )

        self.preview_button = self._button(
            self.output_card,
            "Preview Image",
            self.preview_image,
            secondary=True,
        )
        self.preview_button.grid(
            row=3,
            column=0,
            padx=18,
            pady=6,
            sticky="ew",
        )

        self.save_button = self._button(
            self.output_card,
            "Resize and Save Image",
            self.resize_and_save,
        )
        self.save_button.grid(
            row=4,
            column=0,
            padx=18,
            pady=6,
            sticky="ew",
        )

        self.save_note = ctk.CTkLabel(
            self.output_card,
            text=f"Saved images go to the '{self.output_folder}' folder.",
            font=self.font_small,
            wraplength=360,
        )
        self.save_note.grid(
            row=5,
            column=0,
            padx=18,
            pady=(8, 18),
        )

    def _build_preview_column(self):
        self.preview_card = ctk.CTkFrame(
            self,
            corner_radius=18,
            border_width=1,
        )
        self.preview_card.grid(
            row=0,
            column=1,
            padx=(8, 10),
            pady=10,
            sticky="nsew",
        )

        self.preview_card.grid_columnconfigure(0, weight=1)
        self.preview_card.grid_rowconfigure(1, weight=1)

        self.preview_heading = ctk.CTkLabel(
            self.preview_card,
            text="Image Preview",
            font=self.font_section,
        )
        self.preview_heading.grid(
            row=0,
            column=0,
            padx=18,
            pady=(16, 8),
            sticky="w",
        )

        self.preview_panel = ctk.CTkFrame(
            self.preview_card,
            corner_radius=16,
            border_width=1,
        )
        self.preview_panel.grid(
            row=1,
            column=0,
            padx=18,
            pady=(4, 18),
            sticky="nsew",
        )

        self.preview_panel.grid_columnconfigure(0, weight=1)
        self.preview_panel.grid_rowconfigure(0, weight=1)

        self.preview_label = ctk.CTkLabel(
            self.preview_panel,
            text="Your resized preview will appear here",
            font=self.font_normal,
            wraplength=420,
        )
        self.preview_label.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=16,
            pady=16,
        )

    # ==================================================
    # Widget helpers
    # ==================================================

    def _create_card(
        self,
        parent,
        heading,
        row,
        sticky="ew",
    ):
        card = ctk.CTkFrame(
            parent,
            corner_radius=18,
            border_width=1,
        )

        card.grid(
            row=row,
            column=0,
            padx=14,
            pady=9,
            sticky=sticky,
        )

        heading_label = ctk.CTkLabel(
            card,
            text=heading,
            font=self.font_section,
        )
        heading_label.grid(
            row=0,
            column=0,
            columnspan=4,
            padx=18,
            pady=(16, 8),
            sticky="w",
        )

        return card

    def _label(
        self,
        parent,
        text,
    ):
        return ctk.CTkLabel(
            parent,
            text=text,
            font=self.font_normal,
        )

    def _entry(
        self,
        parent,
        variable,
        placeholder="",
    ):
        return ctk.CTkEntry(
            parent,
            textvariable=variable,
            placeholder_text=placeholder,
            height=38,
            corner_radius=10,
            border_width=1,
            font=self.font_normal,
        )

    def _button(
        self,
        parent,
        text,
        command,
        width=150,
        secondary=False,
    ):
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

        # Used by Chimera's theme system.
        button._chimera_secondary = secondary

        return button

    def _option_menu(
        self,
        parent,
        variable,
        values,
        command=None,
        width=170,
    ):
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

    # ==================================================
    # Validation
    # ==================================================

    @staticmethod
    def parse_dimensions(
        width_text,
        height_text,
    ):
        """
        Validate resize dimensions.

        Kept public enough for bulk_image_tab.py to reuse if desired.
        """

        try:
            width = int(width_text)
            height = int(height_text)

        except ValueError as exc:
            raise ValueError(
                "Width and height must be whole numbers."
            ) from exc

        if width <= 0 or height <= 0:
            raise ValueError(
                "Width and height must be greater than zero."
            )

        return width, height

    # ==================================================
    # Preview processing
    # ==================================================

    @staticmethod
    def build_preview_image(
        input_path,
        width,
        height,
        keep_ratio,
        max_preview_width,
        max_preview_height,
    ):
        """
        Build a resized preview image.

        Bulk Image Resize can also reuse this helper later.
        """

        with Image.open(input_path) as image:
            preview_image = image.copy()

        if keep_ratio:
            preview_image.thumbnail(
                (width, height),
                Image.Resampling.LANCZOS,
            )

        else:
            preview_image = preview_image.resize(
                (width, height),
                Image.Resampling.LANCZOS,
            )

        preview_image.thumbnail(
            (
                max_preview_width,
                max_preview_height,
            ),
            Image.Resampling.LANCZOS,
        )

        return preview_image

    # ==================================================
    # User actions
    # ==================================================

    def browse_input_file(self):
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[
                (
                    "Image Files",
                    "*.jpg *.jpeg *.png",
                ),
                (
                    "All Files",
                    "*.*",
                ),
            ],
        )

        if file_path:
            self.input_path_var.set(file_path)

    def apply_preset(self, preset_name):
        dimensions = PRESETS.get(preset_name)

        if dimensions is None:
            return

        width, height = dimensions

        self.width_var.set(str(width))
        self.height_var.set(str(height))

    def preview_image(self):
        input_path = self.input_path_var.get().strip()

        if not input_path:
            messagebox.showerror(
                "Missing Input",
                "Please choose an input image.",
            )
            return

        try:
            width, height = self.parse_dimensions(
                self.width_var.get(),
                self.height_var.get(),
            )

            preview_image = self.build_preview_image(
                input_path=input_path,
                width=width,
                height=height,
                keep_ratio=self.keep_ratio_var.get(),
                max_preview_width=max(
                    250,
                    self.preview_panel.winfo_width() - 36,
                ),
                max_preview_height=max(
                    250,
                    self.preview_panel.winfo_height() - 36,
                ),
            )

            self.preview_ctk_image = ctk.CTkImage(
                light_image=preview_image,
                dark_image=preview_image,
                size=preview_image.size,
            )

            self.preview_label.configure(
                image=self.preview_ctk_image,
                text="",
            )

        except Exception as exc:
            messagebox.showerror(
                "Preview Error",
                f"Could not preview image:\n{exc}",
            )

    def resize_and_save(self):
        input_path = self.input_path_var.get().strip()
        output_name = self.output_name_var.get().strip()

        if not input_path:
            messagebox.showerror(
                "Missing Input",
                "Please choose an input image.",
            )
            return

        if not output_name:
            messagebox.showerror(
                "Missing Output Name",
                "Please enter an output image name.",
            )
            return

        try:
            width, height = self.parse_dimensions(
                self.width_var.get(),
                self.height_var.get(),
            )

        except ValueError as exc:
            messagebox.showerror(
                "Invalid Size",
                str(exc),
            )
            return

        os.makedirs(
            self.output_folder,
            exist_ok=True,
        )

        format_choice = self.format_var.get()

        if format_choice == "PNG":
            extension = ".png"
            save_format = "PNG"

        else:
            extension = ".jpg"
            save_format = "JPEG"

        output_path = os.path.join(
            self.output_folder,
            f"{output_name}{extension}",
        )

        try:
            resize_image(
                input_path=input_path,
                output_path=output_path,
                width=width,
                height=height,
                save_format=save_format,
                keep_ratio=self.keep_ratio_var.get(),
            )

            messagebox.showinfo(
                "Success",
                (
                    "Image resized and saved successfully!"
                    f"\n\nSaved to:\n{output_path}"
                ),
            )

        except Exception as exc:
            messagebox.showerror(
                "Error",
                f"Something went wrong:\n{exc}",
            )

    # ==================================================
    # Theme integration
    # ==================================================

    def apply_theme_overrides(self, theme):
        """
        Handle visual properties that require explicit tab-level
        theme updates.
        """

        self.preview_panel.configure(
            fg_color=theme["preview"],
            border_color=theme["border"],
        )

        self.save_note.configure(
            text_color=theme["muted"],
        )
        