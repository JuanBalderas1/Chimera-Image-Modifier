import os
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageTk


DEFAULT_OUTPUT_FOLDER = "Modified Images"


class TransparencyTab(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        font_normal,
        font_small,
        font_bold,
        font_section,
        current_theme,
        base_font_size,
        output_folder=DEFAULT_OUTPUT_FOLDER,
    ):
        super().__init__(parent, fg_color="transparent")

        # --------------------------------------------------
        # Shared application resources
        # --------------------------------------------------

        self.font_normal = font_normal
        self.font_small = font_small
        self.font_bold = font_bold
        self.font_section = font_section

        self.current_theme = current_theme
        self.base_font_size = base_font_size
        self.output_folder = output_folder

        self._create_variables()
        self._create_editor_state()
        self._configure_workspace()
        self._build_interface()

        self._update_history_buttons()
        self._update_crop_buttons()
        self._draw_placeholder()

    # ==================================================
    # Variables
    # ==================================================

    def _create_variables(self):
        self.input_path_var = tk.StringVar()

        self.output_name_var = tk.StringVar(
            value="transparent_image"
        )

        self.brush_size_var = tk.IntVar(
            value=40
        )

        self.tool_var = tk.StringVar(
            value="Erase"
        )

        self.zoom_label_var = tk.StringVar(
            value="100%"
        )

        self.smoothing_var = tk.IntVar(
            value=2
        )

    # ==================================================
    # Editor state
    # ==================================================

    def _create_editor_state(self):
        self.source_image = None
        self.mask = None

        self.display_image = None
        self.tk_image = None

        self.scale = 1.0
        self.fit_scale = 1.0
        self.zoom = 1.0

        self.offset_x = 0
        self.offset_y = 0

        # Brush state
        self.last_point = None
        self.stroke_snapshot = None

        # History
        self.undo_stack = []
        self.redo_stack = []
        self.history_limit = 20

        # Crop state
        self.crop_mode = False
        self.crop_start = None
        self.crop_end = None

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
            weight=0,
        )

        self.grid_columnconfigure(
            1,
            weight=1,
        )

        self.grid_rowconfigure(
            0,
            weight=1,
        )

    # ==================================================
    # Interface construction
    # ==================================================

    def _build_interface(self):
        self._build_controls_column()
        self._build_editor_column()

    # ==================================================
    # Left controls
    # ==================================================

    def _build_controls_column(self):
        self.controls = ctk.CTkScrollableFrame(
            self,
            width=360,
            corner_radius=16,
            fg_color="transparent",
        )

        self.controls.grid(
            row=0,
            column=0,
            padx=(10, 8),
            pady=10,
            sticky="nsw",
        )

        self.controls.grid_columnconfigure(
            0,
            weight=1,
        )

        self._build_input_card()
        self._build_brush_card()
        self._build_image_tools_card()
        self._build_save_card()

    # --------------------------------------------------
    # 1. Image input
    # --------------------------------------------------

    def _build_input_card(self):
        self.input_card = self._create_card(
            self.controls,
            "1  Choose an image",
            0,
        )

        self.input_card.grid_columnconfigure(
            0,
            weight=1,
        )

        self._label(
            self.input_card,
            "Source image",
        ).grid(
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
            "Load Image",
            self.browse_image,
        )

        self.browse_button.grid(
            row=3,
            column=0,
            padx=18,
            pady=(0, 18),
            sticky="ew",
        )

    # --------------------------------------------------
    # 2. Transparency brush
    # --------------------------------------------------

    def _build_brush_card(self):
        self.brush_card = self._create_card(
            self.controls,
            "2  Paint transparency",
            1,
        )

        self.brush_card.grid_columnconfigure(
            0,
            weight=1,
        )

        self.help_label = ctk.CTkLabel(
            self.brush_card,
            text=(
                "Choose Erase to remove pixels or Restore to "
                "paint them back. The checkerboard represents "
                "true transparency."
            ),
            font=self.font_small,
            justify="left",
            wraplength=300,
        )

        self.help_label.grid(
            row=1,
            column=0,
            padx=18,
            pady=(6, 12),
            sticky="w",
        )

        self._label(
            self.brush_card,
            "Brush mode",
        ).grid(
            row=2,
            column=0,
            padx=18,
            pady=(0, 4),
            sticky="w",
        )

        self.tool_menu = self._option_menu(
            self.brush_card,
            self.tool_var,
            ["Erase", "Restore"],
        )

        self.tool_menu.grid(
            row=3,
            column=0,
            padx=18,
            pady=(0, 12),
            sticky="ew",
        )

        self.brush_label = self._label(
            self.brush_card,
            "Brush size: 40 px",
        )

        self.brush_label.grid(
            row=4,
            column=0,
            padx=18,
            pady=(0, 4),
            sticky="w",
        )

        self.brush_slider = ctk.CTkSlider(
            self.brush_card,
            from_=5,
            to=200,
            number_of_steps=195,
            variable=self.brush_size_var,
            command=self.on_brush_changed,
        )

        self.brush_slider.grid(
            row=5,
            column=0,
            padx=18,
            pady=(0, 14),
            sticky="ew",
        )

        self._build_history_controls()

        self.reset_button = self._button(
            self.brush_card,
            "Reset Removed Areas",
            self.reset_mask,
            secondary=True,
        )

        self.reset_button.grid(
            row=7,
            column=0,
            padx=18,
            pady=(0, 18),
            sticky="ew",
        )

    def _build_history_controls(self):
        self.history_row = ctk.CTkFrame(
            self.brush_card,
            fg_color="transparent",
        )

        self.history_row.grid(
            row=6,
            column=0,
            padx=18,
            pady=(0, 10),
            sticky="ew",
        )

        self.history_row.grid_columnconfigure(
            (0, 1),
            weight=1,
        )

        self.undo_button = self._button(
            self.history_row,
            "Undo",
            self.undo,
            secondary=True,
        )

        self.undo_button.grid(
            row=0,
            column=0,
            padx=(0, 5),
            sticky="ew",
        )

        self.redo_button = self._button(
            self.history_row,
            "Redo",
            self.redo,
            secondary=True,
        )

        self.redo_button.grid(
            row=0,
            column=1,
            padx=(5, 0),
            sticky="ew",
        )

    # --------------------------------------------------
    # 3. Image tools
    # --------------------------------------------------

    def _build_image_tools_card(self):
        self.image_tools_card = self._create_card(
            self.controls,
            "3  Image tools",
            2,
        )

        self.image_tools_card.grid_columnconfigure(
            0,
            weight=1,
        )

    # ------------------------------------------
    # Cropping
    # ------------------------------------------

        self._label(
            self.image_tools_card,
            "Crop",
        ).grid(
            row=1,
            column=0,
            padx=18,
            pady=(6, 4),
            sticky="w",
        )

        self.crop_help = ctk.CTkLabel(
            self.image_tools_card,
            text=(
                "Start Crop, then drag a rectangle directly "
                "over the image."
            ),
            font=self.font_small,
            justify="left",
            wraplength=300,
        )

        self.crop_help.grid(
            row=2,
            column=0,
            padx=18,
            pady=(0, 8),
            sticky="w",
        )

        self.start_crop_button = self._button(
            self.image_tools_card,
            "Start Crop",
            self.start_crop,
            secondary=True,
        )

        self.start_crop_button.grid(
            row=3,
            column=0,
            padx=18,
            pady=(0, 8),
            sticky="ew",
        )

        self.crop_action_row = ctk.CTkFrame(
            self.image_tools_card,
            fg_color="transparent",
        )

        self.crop_action_row.grid(
            row=4,
            column=0,
            padx=18,
            pady=(0, 12),
            sticky="ew",
        )

        self.crop_action_row.grid_columnconfigure(
            (0, 1),
            weight=1,
        )

        self.apply_crop_button = self._button(
            self.crop_action_row,
            "Apply Crop",
            self.apply_crop,
        )

        self.apply_crop_button.grid(
            row=0,
            column=0,
            padx=(0, 5),
            sticky="ew",
        )

        self.cancel_crop_button = self._button(
            self.crop_action_row,
            "Cancel",
            self.cancel_crop,
            secondary=True,
        )

        self.cancel_crop_button.grid(
            row=0,
            column=1,
            padx=(5, 0),
            sticky="ew",
        )

    # ------------------------------------------
    # Edge smoothing
    # ------------------------------------------

        self.smoothing_label = self._label(
            self.image_tools_card,
            "Edge smoothing: 2 px",
        )

        self.smoothing_label.grid(
            row=5,
            column=0,
            padx=18,
            pady=(2, 4),
            sticky="w",
        )

        self.smoothing_slider = ctk.CTkSlider(
            self.image_tools_card,
            from_=1,
            to=12,
            number_of_steps=11,
            variable=self.smoothing_var,
            command=self.on_smoothing_changed,
        )

        self.smoothing_slider.grid(
            row=6,
            column=0,
            padx=18,
            pady=(0, 8),
            sticky="ew",
        )

        self.smooth_button = self._button(
            self.image_tools_card,
            "Smooth Transparency Edges",
            self.smooth_edges,
            secondary=True,
        )

        self.smooth_button.grid(
            row=7,
            column=0,
            padx=18,
            pady=(0, 18),
            sticky="ew",
        )

    # --------------------------------------------------
    # 4. Save image
    # --------------------------------------------------

    def _build_save_card(self):
        self.save_card = self._create_card(
            self.controls,
            "4  Save transparent PNG",
            3,
        )

        self.save_card.grid_columnconfigure(
            0,
            weight=1,
        )

        self._label(
            self.save_card,
            "Output name (no extension)",
        ).grid(
            row=1,
            column=0,
            padx=18,
            pady=(6, 4),
            sticky="w",
        )

        self.output_entry = self._entry(
            self.save_card,
            self.output_name_var,
            placeholder="Example: logo_transparent",
        )

        self.output_entry.grid(
            row=2,
            column=0,
            padx=18,
            pady=(0, 12),
            sticky="ew",
        )

        self.save_button = self._button(
            self.save_card,
            "Save Transparent PNG",
            self.save_png,
        )

        self.save_button.grid(
            row=3,
            column=0,
            padx=18,
            pady=(0, 10),
            sticky="ew",
        )

        self.save_note = ctk.CTkLabel(
            self.save_card,
            text=(
                f"Saved PNG files go to the "
                f"'{self.output_folder}' folder."
            ),
            font=self.font_small,
            wraplength=300,
        )

        self.save_note.grid(
            row=4,
            column=0,
            padx=18,
            pady=(0, 18),
        )

    # ==================================================
    # Editor column
    # ==================================================

    def _build_editor_column(self):
        self.editor_card = ctk.CTkFrame(
            self,
            corner_radius=18,
            border_width=1,
        )

        self.editor_card.grid(
            row=0,
            column=1,
            padx=(8, 10),
            pady=10,
            sticky="nsew",
        )

        self.editor_card.grid_columnconfigure(
            0,
            weight=1,
        )

        self.editor_card.grid_rowconfigure(
            2,
            weight=1,
        )

        self.heading = ctk.CTkLabel(
            self.editor_card,
            text="Transparency Canvas",
            font=self.font_section,
        )

        self.heading.grid(
            row=0,
            column=0,
            padx=18,
            pady=(16, 8),
            sticky="w",
        )

        self._build_zoom_controls()
        self._build_canvas()

    # --------------------------------------------------
    # Zoom controls
    # --------------------------------------------------

    def _build_zoom_controls(self):
        self.zoom_row = ctk.CTkFrame(
            self.editor_card,
            fg_color="transparent",
        )

        self.zoom_row.grid(
            row=1,
            column=0,
            padx=18,
            pady=(0, 6),
            sticky="ew",
        )

        # Let the center stretch so the transform buttons
        # stay pushed to the far right. 
        self.zoom_row.grid_columnconfigure(
            3,
            weight=1,
        )

        self.zoom_out_button = self._button(
            self.zoom_row,
            "−",
            self.zoom_out,
            width=46,
            secondary=True,
        )

        self.zoom_out_button.grid(
            row=0,
            column=0,
            padx=(0, 5),
        )

        self.zoom_in_button = self._button(
            self.zoom_row,
            "+",
            self.zoom_in,
            width=46,
            secondary=True,
        )

        self.zoom_in_button.grid(
            row=0,
            column=1,
            padx=5,
        )

        self.zoom_in_button.grid(
            row=0,
            column=1,
            padx=5,
        )

        self.zoom_fit_button = self._button(
            self.zoom_row,
            "Fit",
            self.fit_to_canvas,
            width=60,
            secondary=True,
        )

        self.zoom_fit_button.grid(
            row=0,
            column=2,
            padx=5,
        )

    # ------------------------------------------
    # Image transforms - right side
    # ------------------------------------------

        self.rotate_left_button = self._button(
            self.zoom_row,
            "Rotate Left",
            self.rotate_left,
            width=82,
            secondary=True,
        )

        self.rotate_left_button.grid(
            row=0,
            column=4,
            padx=(10, 4),
        )

        self.rotate_right_button = self._button(
            self.zoom_row,
            "Rotate Right",
            self.rotate_right,
            width=88,
            secondary=True,
        )


        self.rotate_right_button.grid(
            row=0,
            column=5,
            padx=4,
        )

        self.flip_x_button = self._button(
            self.zoom_row,
            "X-Flip",
            self.flip_x_axis,
            width=62,
            secondary=True,
        )

        self.flip_x_button.grid(
            row=0,
            column=6,
            padx=4,
        )

        self.flip_y_button = self._button(
            self.zoom_row,
            "Y-Flip",
            self.flip_y_axis,
            width=62,
            secondary=True,
        )

        self.flip_y_button.grid(
            row=0,
            column=7,
            padx=(4, 0),
        )

        self.flip_y_button.grid(
            row=0,
            column=7,
            padx=(4, 0),
        )

    # ------------------------------------------
    # Zoom percentage
    # ------------------------------------------

        self.zoom_label = ctk.CTkLabel(
            self.zoom_row,
            textvariable=self.zoom_label_var,
            font=self.font_normal,
        )

        self.zoom_label.grid(
            row=0,
            column=8,
            padx=(10, 0),
            sticky="e",
        )

    # --------------------------------------------------
    # Canvas
    # --------------------------------------------------

    def _build_canvas(self):
        self.canvas_frame = ctk.CTkFrame(
            self.editor_card,
            corner_radius=12,
            border_width=1,
        )

        self.canvas_frame.grid(
            row=2,
            column=0,
            padx=18,
            pady=(4, 18),
            sticky="nsew",
        )

        self.canvas_frame.grid_columnconfigure(
            0,
            weight=1,
        )

        self.canvas_frame.grid_rowconfigure(
            0,
            weight=1,
        )

        self.canvas = tk.Canvas(
            self.canvas_frame,
            highlightthickness=0,
            cursor="crosshair",
            xscrollincrement=1,
            yscrollincrement=1,
        )

        self.canvas.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        self.vertical_scrollbar = ctk.CTkScrollbar(
            self.canvas_frame,
            orientation="vertical",
            command=self.canvas.yview,
        )

        self.vertical_scrollbar.grid(
            row=0,
            column=1,
            sticky="ns",
        )

        self.horizontal_scrollbar = ctk.CTkScrollbar(
            self.canvas_frame,
            orientation="horizontal",
            command=self.canvas.xview,
        )

        self.horizontal_scrollbar.grid(
            row=1,
            column=0,
            sticky="ew",
        )

        self.canvas.configure(
            xscrollcommand=self.horizontal_scrollbar.set,
            yscrollcommand=self.vertical_scrollbar.set,
        )

        self._bind_canvas_events()

    def _bind_canvas_events(self):
        self.canvas.bind(
            "<Configure>",
            self._on_canvas_resize,
        )

        self.canvas.bind(
            "<ButtonPress-1>",
            self._start_canvas_action,
        )

        self.canvas.bind(
            "<B1-Motion>",
            self._continue_canvas_action,
        )

        self.canvas.bind(
            "<ButtonRelease-1>",
            self._end_canvas_action,
        )

        self.canvas.bind(
            "<MouseWheel>",
            self._on_mousewheel,
        )

        self.canvas.bind(
            "<Shift-MouseWheel>",
            self._on_shift_mousewheel,
        )

        self.canvas.bind(
            "<Control-MouseWheel>",
            self._on_ctrl_mousewheel,
        )

        root = self.winfo_toplevel()

        root.bind(
            "<Control-z>",
            lambda _event: self.undo(),
        )

        root.bind(
            "<Control-y>",
            lambda _event: self.redo(),
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
    # Image loading
    # ==================================================

    def browse_image(self):
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
                self.source_image = image.convert("RGBA")

            self.input_path_var.set(
                file_path
            )

            self.mask = Image.new(
                "L",
                self.source_image.size,
                255,
            )

            self.zoom = 1.0

            self.undo_stack.clear()
            self.redo_stack.clear()

            self.cancel_crop(
                render=False
            )

            self._update_history_buttons()
            self._render_editor()

        except Exception as exc:
            messagebox.showerror(
                "Image Error",
                f"Could not load the selected image:\n{exc}",
            )

    # ==================================================
    # History
    # ==================================================

    def _capture_state(self):
        if (
            self.source_image is None
            or self.mask is None
        ):
            return None

        # source_image itself is never modified in-place.
        # Keeping its reference saves memory during brush edits.
        return (
            self.source_image,
            self.mask.copy(),
        )

    def _restore_state(
        self,
        state,
    ):
        if state is None:
            return

        self.source_image = state[0]
        self.mask = state[1].copy()

        self.zoom = 1.0

        self.cancel_crop(
            render=False
        )

    def _push_history(
        self,
        snapshot,
    ):
        if snapshot is None:
            return

        self.undo_stack.append(
            snapshot
        )

        if len(self.undo_stack) > self.history_limit:
            self.undo_stack.pop(0)

        self.redo_stack.clear()

        self._update_history_buttons()

    def _update_history_buttons(self):
        self.undo_button.configure(
            state=(
                "normal"
                if self.undo_stack
                else "disabled"
            )
        )

        self.redo_button.configure(
            state=(
                "normal"
                if self.redo_stack
                else "disabled"
            )
        )

    def undo(self):
        if not self.undo_stack:
            return

        current_state = self._capture_state()

        if current_state is not None:
            self.redo_stack.append(
                current_state
            )

        previous_state = self.undo_stack.pop()

        self._restore_state(
            previous_state
        )

        self._update_history_buttons()
        self._render_editor()

    def redo(self):
        if not self.redo_stack:
            return

        current_state = self._capture_state()

        if current_state is not None:
            self.undo_stack.append(
                current_state
            )

        next_state = self.redo_stack.pop()

        self._restore_state(
            next_state
        )

        self._update_history_buttons()
        self._render_editor()

    # ==================================================
    # Brush controls
    # ==================================================

    def on_brush_changed(
        self,
        value,
    ):
        brush_size = int(
            float(value)
        )

        self.brush_label.configure(
            text=f"Brush size: {brush_size} px"
        )

    def reset_mask(self):
        if self.source_image is None:
            messagebox.showinfo(
                "No Image Loaded",
                "Load an image before resetting the mask.",
            )
            return

        self._push_history(
            self._capture_state()
        )

        self.mask = Image.new(
            "L",
            self.source_image.size,
            255,
        )

        self._render_editor()

    # ==================================================
    # Rotation
    # ==================================================

    def rotate_left(self):
        if not self._require_image():
            return

        self._push_history(
            self._capture_state()
        )

        self.source_image = self.source_image.transpose(
            Image.Transpose.ROTATE_90
        )

        self.mask = self.mask.transpose(
            Image.Transpose.ROTATE_90
        )

        self.cancel_crop(
            render=False
        )

        self._render_editor()

    def rotate_right(self):
        if not self._require_image():
            return

        self._push_history(
            self._capture_state()
        )

        self.source_image = self.source_image.transpose(
            Image.Transpose.ROTATE_270
        )

        self.mask = self.mask.transpose(
            Image.Transpose.ROTATE_270
        )

        self.cancel_crop(
            render=False
        )

        self._render_editor()

    # ==================================================
    # Flipping
    # ==================================================

    def flip_x_axis(self):
        """
        Flip across the X-axis.

        The top and bottom of the image trade places.
        """

        if not self._require_image():
            return

        self._push_history(
            self._capture_state()
        )

        self.source_image = ImageOps.flip(
            self.source_image
        )

        self.mask = ImageOps.flip(
            self.mask
        )

        self.cancel_crop(
            render=False
        )

        self._render_editor()

    def flip_y_axis(self):
        """
        Flip across the Y-axis.

        The left and right sides of the image trade places.
        """

        if not self._require_image():
            return

        self._push_history(
            self._capture_state()
        )

        self.source_image = ImageOps.mirror(
            self.source_image
        )

        self.mask = ImageOps.mirror(
            self.mask
        )

        self.cancel_crop(
            render=False
        )

        self._render_editor()

    # ==================================================
    # Edge smoothing
    # ==================================================

    def on_smoothing_changed(
        self,
        value,
    ):
        strength = int(
            float(value)
        )

        self.smoothing_label.configure(
            text=f"Edge smoothing: {strength} px"
        )

    def smooth_edges(self):
        if not self._require_image():
            return

        self._push_history(
            self._capture_state()
        )

        strength = max(
            1,
            int(self.smoothing_var.get()),
        )

        # Gaussian blur applied only to the alpha mask.
        #
        # Fully opaque and transparent areas remain intact
        # while hard transparency boundaries gain a softer,
        # anti-aliased transition.
        self.mask = self.mask.filter(
            ImageFilter.GaussianBlur(
                radius=strength
            )
        )

        self._render_editor()

    # ==================================================
    # Cropping
    # ==================================================

    def start_crop(self):
        if not self._require_image():
            return

        self.crop_mode = True
        self.crop_start = None
        self.crop_end = None

        self.canvas.configure(
            cursor="crosshair"
        )

        self._update_crop_buttons()
        self._render_editor()

    def cancel_crop(
        self,
        render=True,
    ):
        self.crop_mode = False
        self.crop_start = None
        self.crop_end = None

        if hasattr(
            self,
            "canvas",
        ):
            self.canvas.configure(
                cursor="crosshair"
            )

        if hasattr(
            self,
            "apply_crop_button",
        ):
            self._update_crop_buttons()

        if (
            render
            and self.source_image is not None
        ):
            self._render_editor()

    def _update_crop_buttons(self):
        has_selection = (
            self.crop_mode
            and self.crop_start is not None
            and self.crop_end is not None
            and self.crop_start != self.crop_end
        )

        self.apply_crop_button.configure(
            state=(
                "normal"
                if has_selection
                else "disabled"
            )
        )

        self.cancel_crop_button.configure(
            state=(
                "normal"
                if self.crop_mode
                else "disabled"
            )
        )

        self.start_crop_button.configure(
            state=(
                "disabled"
                if self.crop_mode
                else "normal"
            )
        )

    def apply_crop(self):
        if (
            not self.crop_mode
            or self.crop_start is None
            or self.crop_end is None
        ):
            return

        width, height = self.source_image.size

        x1, y1 = self.crop_start
        x2, y2 = self.crop_end

        left = max(
            0,
            min(x1, x2),
        )

        top = max(
            0,
            min(y1, y2),
        )

        right = min(
            width,
            max(x1, x2) + 1,
        )

        bottom = min(
            height,
            max(y1, y2) + 1,
        )

        if (
            right - left < 2
            or bottom - top < 2
        ):
            messagebox.showerror(
                "Invalid Crop",
                "The selected crop area is too small.",
            )
            return

        self._push_history(
            self._capture_state()
        )

        crop_box = (
            left,
            top,
            right,
            bottom,
        )

        self.source_image = self.source_image.crop(
            crop_box
        )

        self.mask = self.mask.crop(
            crop_box
        )

        self.zoom = 1.0

        self.cancel_crop(
            render=False
        )

        self._render_editor()

    # ==================================================
    # Canvas action dispatcher
    # ==================================================

    def _start_canvas_action(
        self,
        event,
    ):
        if self.crop_mode:
            self._start_crop_selection(
                event
            )
        else:
            self._start_stroke(
                event
            )

    def _continue_canvas_action(
        self,
        event,
    ):
        if self.crop_mode:
            self._continue_crop_selection(
                event
            )
        else:
            self._continue_stroke(
                event
            )

    def _end_canvas_action(
        self,
        event,
    ):
        if self.crop_mode:
            self._end_crop_selection(
                event
            )
        else:
            self._end_stroke(
                event
            )

    # ==================================================
    # Crop selection events
    # ==================================================

    def _start_crop_selection(
        self,
        event,
    ):
        point = self._canvas_to_image_point(
            event.x,
            event.y,
        )

        if point is None:
            return

        self.crop_start = point
        self.crop_end = point

        self._update_crop_buttons()
        self._render_editor()

    def _continue_crop_selection(
        self,
        event,
    ):
        if self.crop_start is None:
            return

        point = self._canvas_to_image_point(
            event.x,
            event.y,
        )

        if point is None:
            return

        self.crop_end = point

        self._update_crop_buttons()
        self._render_editor()

    def _end_crop_selection(
        self,
        event,
    ):
        if self.crop_start is None:
            return

        point = self._canvas_to_image_point(
            event.x,
            event.y,
        )

        if point is not None:
            self.crop_end = point

        self._update_crop_buttons()
        self._render_editor()

    # ==================================================
    # Brush stroke events
    # ==================================================

    def _start_stroke(
        self,
        event,
    ):
        point = self._canvas_to_image_point(
            event.x,
            event.y,
        )

        self.last_point = point

        if point is not None:
            self.stroke_snapshot = (
                self._capture_state()
            )

            self._paint_line(
                point,
                point,
            )

    def _continue_stroke(
        self,
        event,
    ):
        point = self._canvas_to_image_point(
            event.x,
            event.y,
        )

        if point is None:
            return

        start = (
            self.last_point
            or point
        )

        self._paint_line(
            start,
            point,
        )

        self.last_point = point

    def _end_stroke(
        self,
        _event,
    ):
        if self.stroke_snapshot is not None:
            self._push_history(
                self.stroke_snapshot
            )

        self.stroke_snapshot = None
        self.last_point = None

    def _paint_line(
        self,
        start,
        end,
    ):
        if self.mask is None:
            return

        draw = ImageDraw.Draw(
            self.mask
        )

        brush_size = max(
            1,
            int(self.brush_size_var.get()),
        )

        radius = brush_size // 2

        fill_value = (
            255
            if self.tool_var.get() == "Restore"
            else 0
        )

        draw.line(
            (
                start,
                end,
            ),
            fill=fill_value,
            width=brush_size,
        )

        for x, y in (
            start,
            end,
        ):
            draw.ellipse(
                (
                    x - radius,
                    y - radius,
                    x + radius,
                    y + radius,
                ),
                fill=fill_value,
            )

        self._render_editor()

    # ==================================================
    # Zoom
    # ==================================================

    def zoom_in(self):
        if self.source_image is None:
            return

        self.zoom = min(
            8.0,
            self.zoom * 1.25,
        )

        self._render_editor()

    def zoom_out(self):
        if self.source_image is None:
            return

        self.zoom = max(
            0.25,
            self.zoom / 1.25,
        )

        self._render_editor()

    def fit_to_canvas(self):
        self.zoom = 1.0
        self._render_editor()

    # ==================================================
    # Mouse wheel
    # ==================================================

    def _on_mousewheel(
        self,
        event,
    ):
        direction = (
            -1
            if event.delta > 0
            else 1
        )

        self.canvas.yview_scroll(
            direction * 3,
            "units",
        )

        return "break"

    def _on_shift_mousewheel(
        self,
        event,
    ):
        direction = (
            -1
            if event.delta > 0
            else 1
        )

        self.canvas.xview_scroll(
            direction * 3,
            "units",
        )

        return "break"

    def _on_ctrl_mousewheel(
        self,
        event,
    ):
        if event.delta > 0:
            self.zoom_in()

        elif event.delta < 0:
            self.zoom_out()

        return "break"

    # ==================================================
    # Canvas resizing / placeholder
    # ==================================================

    def _on_canvas_resize(
        self,
        _event=None,
    ):
        if self.source_image is not None:
            self.after_idle(
                self._render_editor
            )
        else:
            self._draw_placeholder()

    def _draw_placeholder(self):
        self.canvas.delete(
            "all"
        )

        width = max(
            1,
            self.canvas.winfo_width(),
        )

        height = max(
            1,
            self.canvas.winfo_height(),
        )

        self.canvas.create_text(
            width // 2,
            height // 2,
            text=(
                "Load an image to begin "
                "removing its background"
            ),
            fill=self.current_theme["muted"],
            font=(
                "Segoe UI",
                self.base_font_size,
            ),
            width=max(
                200,
                width - 80,
            ),
            justify="center",
        )

    # ==================================================
    # Checkerboard
    # ==================================================

    @staticmethod
    def _make_checkerboard(
        width,
        height,
        square=16,
    ):
        board = Image.new(
            "RGBA",
            (width, height),
            (205, 205, 205, 255),
        )

        draw = ImageDraw.Draw(
            board
        )

        alternate = (
            155,
            155,
            155,
            255,
        )

        for y in range(
            0,
            height,
            square,
        ):
            for x in range(
                0,
                width,
                square,
            ):
                if (
                    (x // square)
                    + (y // square)
                ) % 2:
                    draw.rectangle(
                        (
                            x,
                            y,
                            min(x + square, width),
                            min(y + square, height),
                        ),
                        fill=alternate,
                    )

        return board

    # ==================================================
    # Rendering
    # ==================================================

    def _render_editor(self):
        if (
            self.source_image is None
            or self.mask is None
        ):
            self._draw_placeholder()
            return

        canvas_width = max(
            100,
            self.canvas.winfo_width(),
        )

        canvas_height = max(
            100,
            self.canvas.winfo_height(),
        )

        source_width, source_height = (
            self.source_image.size
        )

        self.fit_scale = min(
            (canvas_width - 30) / source_width,
            (canvas_height - 30) / source_height,
        )

        self.fit_scale = max(
            0.01,
            self.fit_scale,
        )

        self.scale = (
            self.fit_scale
            * self.zoom
        )

        self.zoom_label_var.set(
            f"{int(self.zoom * 100)}%"
        )

        display_size = (
            max(
                1,
                int(source_width * self.scale),
            ),
            max(
                1,
                int(source_height * self.scale),
            ),
        )

        self.offset_x = max(
            0,
            (canvas_width - display_size[0]) // 2,
        )

        self.offset_y = max(
            0,
            (canvas_height - display_size[1]) // 2,
        )

        edited_image = (
            self.source_image.copy()
        )

        edited_image.putalpha(
            self.mask
        )

        resized_image = edited_image.resize(
            display_size,
            Image.Resampling.LANCZOS,
        )

        checkerboard = self._make_checkerboard(
            *display_size
        )

        checkerboard.alpha_composite(
            resized_image
        )

        self.display_image = checkerboard

        self.tk_image = ImageTk.PhotoImage(
            checkerboard
        )

        self.canvas.delete(
            "all"
        )

        self.canvas.create_image(
            self.offset_x,
            self.offset_y,
            anchor="nw",
            image=self.tk_image,
        )

        content_width = max(
            canvas_width,
            self.offset_x + display_size[0],
        )

        content_height = max(
            canvas_height,
            self.offset_y + display_size[1],
        )

        self.canvas.configure(
            scrollregion=(
                0,
                0,
                content_width,
                content_height,
            )
        )

        self._draw_crop_overlay()

    # ==================================================
    # Crop overlay
    # ==================================================

    def _draw_crop_overlay(self):
        if (
            not self.crop_mode
            or self.crop_start is None
            or self.crop_end is None
        ):
            return

        x1, y1 = self.crop_start
        x2, y2 = self.crop_end

        canvas_x1 = (
            self.offset_x
            + x1 * self.scale
        )

        canvas_y1 = (
            self.offset_y
            + y1 * self.scale
        )

        canvas_x2 = (
            self.offset_x
            + x2 * self.scale
        )

        canvas_y2 = (
            self.offset_y
            + y2 * self.scale
        )

        self.canvas.create_rectangle(
            canvas_x1,
            canvas_y1,
            canvas_x2,
            canvas_y2,
            outline=self.current_theme["accent"],
            width=2,
            dash=(6, 4),
        )

    # ==================================================
    # Coordinate conversion
    # ==================================================

    def _canvas_to_image_point(
        self,
        canvas_x,
        canvas_y,
    ):
        if self.source_image is None:
            return None

        scrolled_x = self.canvas.canvasx(
            canvas_x
        )

        scrolled_y = self.canvas.canvasy(
            canvas_y
        )

        image_x = (
            scrolled_x
            - self.offset_x
        ) / self.scale

        image_y = (
            scrolled_y
            - self.offset_y
        ) / self.scale

        width, height = (
            self.source_image.size
        )

        if not (
            0 <= image_x < width
            and 0 <= image_y < height
        ):
            return None

        return (
            int(image_x),
            int(image_y),
        )

    # ==================================================
    # Common validation
    # ==================================================

    def _require_image(self):
        if (
            self.source_image is None
            or self.mask is None
        ):
            messagebox.showinfo(
                "No Image Loaded",
                "Load an image before using this tool.",
            )
            return False

        return True

    # ==================================================
    # Save PNG
    # ==================================================

    def save_png(self):
        if not self._require_image():
            return

        output_name = (
            self.output_name_var
            .get()
            .strip()
        )

        if not output_name:
            messagebox.showerror(
                "Missing Output Name",
                "Please enter an output image name.",
            )
            return

        os.makedirs(
            self.output_folder,
            exist_ok=True,
        )

        output_path = os.path.join(
            self.output_folder,
            f"{output_name}.png",
        )

        try:
            output_image = (
                self.source_image.copy()
            )

            output_image.putalpha(
                self.mask
            )

            output_image.save(
                output_path,
                "PNG",
            )

            messagebox.showinfo(
                "Success",
                (
                    "Transparent PNG saved successfully!"
                    f"\n\nSaved to:\n{output_path}"
                ),
            )

        except Exception as exc:
            messagebox.showerror(
                "Save Error",
                (
                    "Could not save the "
                    f"transparent PNG:\n{exc}"
                ),
            )

    # ==================================================
    # Theme integration
    # ==================================================

    def apply_theme_overrides(
        self,
        theme,
        base_font_size=None,
    ):
        self.current_theme = theme

        if base_font_size is not None:
            self.base_font_size = base_font_size

        self.configure(
            fg_color=theme["window"]
        )

        self.master.configure(
            fg_color=theme["window"]
        )

        self.help_label.configure(
            text_color=theme["muted"]
        )

        self.crop_help.configure(
            text_color=theme["muted"]
        )

        self.save_note.configure(
            text_color=theme["muted"]
        )

        self.canvas.configure(
            bg=theme["preview"]
        )

        self.canvas_frame.configure(
            border_color=theme["border"]
        )

        if self.source_image is None:
            self._draw_placeholder()
        else:
            self._render_editor()
