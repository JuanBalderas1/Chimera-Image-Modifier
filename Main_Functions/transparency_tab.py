import os
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk


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
        super().__init__(
            parent,
            fg_color="transparent",
        )

        # Shared application resources
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

        self.last_point = None
        self.stroke_snapshot = None

        self.undo_stack = []
        self.redo_stack = []

        self.history_limit = 30

    # ==================================================
    # Workspace
    # ==================================================

    def _configure_workspace(self):
        self.master.grid_columnconfigure(
            0,
            weight=1,
        )

        self.master.grid_rowconfigure(
            0,
            weight=1,
        )

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

    # --------------------------------------------------
    # Left controls
    # --------------------------------------------------

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
        self._build_save_card()

    # --------------------------------------------------
    # Image input
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
    # Brush controls
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
                "Choose Erase to remove pixels or Restore "
                "to paint them back. The checkerboard "
                "represents true transparency."
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
            [
                "Erase",
                "Restore",
            ],
            self.on_tool_changed,
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
    # Save controls
    # --------------------------------------------------

    def _build_save_card(self):
        self.save_card = self._create_card(
            self.controls,
            "3  Save transparent PNG",
            2,
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
    # Editor / canvas column
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

        self.zoom_fit_button = self._button(
            self.zoom_row,
            "Fit",
            self.fit_to_canvas,
            width=70,
            secondary=True,
        )

        self.zoom_fit_button.grid(
            row=0,
            column=2,
            padx=5,
        )

        self.zoom_label = ctk.CTkLabel(
            self.zoom_row,
            textvariable=self.zoom_label_var,
            font=self.font_normal,
        )

        self.zoom_label.grid(
            row=0,
            column=4,
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
            self._start_stroke,
        )

        self.canvas.bind(
            "<B1-Motion>",
            self._continue_stroke,
        )

        self.canvas.bind(
            "<ButtonRelease-1>",
            self._end_stroke,
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

        self.bind_all(
            "<Control-z>",
            lambda _event: self.undo(),
        )

        self.bind_all(
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
    # Load image
    # ==================================================

    def browse_image(self):
        file_path = filedialog.askopenfilename(
            title="Select an image for transparency editing",
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

            self._update_history_buttons()
            self._render_editor()

        except Exception as exc:
            messagebox.showerror(
                "Image Error",
                f"Could not load the selected image:\n{exc}",
            )

    # ==================================================
    # Brush controls
    # ==================================================

    def on_brush_changed(self, value):
        brush_size = int(
            float(value)
        )

        self.brush_label.configure(
            text=f"Brush size: {brush_size} px"
        )

    def on_tool_changed(self, _tool_name):
        # tool_var already contains the selected mode.
        pass

    # ==================================================
    # Undo / redo
    # ==================================================

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

    def _push_history(self, snapshot):
        if snapshot is None:
            return

        self.undo_stack.append(
            snapshot
        )

        if len(self.undo_stack) > self.history_limit:
            self.undo_stack.pop(0)

        self.redo_stack.clear()

        self._update_history_buttons()

    def undo(self):
        if self.mask is None:
            return

        if not self.undo_stack:
            return

        self.redo_stack.append(
            self.mask.copy()
        )

        self.mask = self.undo_stack.pop()

        self._update_history_buttons()
        self._render_editor()

    def redo(self):
        if self.mask is None:
            return

        if not self.redo_stack:
            return

        self.undo_stack.append(
            self.mask.copy()
        )

        self.mask = self.redo_stack.pop()

        self._update_history_buttons()
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
    # Reset transparency
    # ==================================================

    def reset_mask(self):
        if self.source_image is None:
            messagebox.showinfo(
                "No Image Loaded",
                "Load an image before resetting the mask.",
            )
            return

        previous_mask = self.mask.copy()

        self.mask = Image.new(
            "L",
            self.source_image.size,
            255,
        )

        self._push_history(
            previous_mask
        )

        self._render_editor()

    # ==================================================
    # Mouse wheel / canvas movement
    # ==================================================

    def _on_mousewheel(self, event):
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

    def _on_shift_mousewheel(self, event):
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

    def _on_ctrl_mousewheel(self, event):
        if event.delta > 0:
            self.zoom_in()

        elif event.delta < 0:
            self.zoom_out()

        return "break"

    # ==================================================
    # Canvas resizing / placeholder
    # ==================================================

    def _on_canvas_resize(self, _event=None):
        if self.source_image is not None:
            self.after_idle(
                self._render_editor
            )

        else:
            self._draw_placeholder()

    def _draw_placeholder(self):
        self.canvas.delete("all")

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
    # Transparency rendering
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
            (
                canvas_width
                - display_size[0]
            ) // 2,
        )

        self.offset_y = max(
            0,
            (
                canvas_height
                - display_size[1]
            ) // 2,
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

        self.canvas.delete("all")

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

    # ==================================================
    # Canvas-to-image coordinates
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
    # Brush strokes
    # ==================================================

    def _start_stroke(self, event):
        point = self._canvas_to_image_point(
            event.x,
            event.y,
        )

        self.last_point = point

        if point is not None:
            self.stroke_snapshot = (
                self.mask.copy()
            )

            self._paint_line(
                point,
                point,
            )

    def _continue_stroke(self, event):
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

    def _end_stroke(self, _event):
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
    # Save transparent PNG
    # ==================================================

    def save_png(self):
        if (
            self.source_image is None
            or self.mask is None
        ):
            messagebox.showerror(
                "No Image Loaded",
                "Load and edit an image before saving.",
            )
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

        self.help_label.configure(
            text_color=theme["muted"],
        )

        self.save_note.configure(
            text_color=theme["muted"],
        )

        self.canvas.configure(
            bg=theme["preview"],
        )

        self.canvas_frame.configure(
            border_color=theme["border"],
        )

        if self.source_image is None:
            self._draw_placeholder()
        