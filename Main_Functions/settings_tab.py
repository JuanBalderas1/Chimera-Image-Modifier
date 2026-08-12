import tkinter as tk

import customtkinter as ctk


# --------------------------------------------------
# Appearance configuration
# --------------------------------------------------

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


DEFAULT_THEME_NAME = "Chimera Default"
DEFAULT_FONT_SIZE_NAME = "Medium"


class SettingsTab(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        app,
        font_normal,
        font_small,
        font_bold,
        font_section,
        font_title,
        font_subtitle,
        theme_name=DEFAULT_THEME_NAME,
        font_size_name=DEFAULT_FONT_SIZE_NAME,
    ):
        super().__init__(
            parent,
            fg_color="transparent",
        )

        # Main application reference
        self.app = app

        # Shared Chimera font objects
        self.font_normal = font_normal
        self.font_small = font_small
        self.font_bold = font_bold
        self.font_section = font_section
        self.font_title = font_title
        self.font_subtitle = font_subtitle

        # Current appearance state
        self.current_theme_name = theme_name
        self.current_font_size_name = font_size_name

        self.current_theme = THEMES[
            self.current_theme_name
        ]

        self.base_font_size = FONT_SIZES[
            self.current_font_size_name
        ]

        self._create_variables()
        self._configure_workspace()
        self._build_interface()

    # ==================================================
    # Variables
    # ==================================================

    def _create_variables(self):
        self.theme_var = tk.StringVar(
            value=self.current_theme_name
        )

        self.font_size_var = tk.StringVar(
            value=self.current_font_size_name
        )

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
            weight=1,
        )

        self.grid_rowconfigure(
            2,
            weight=1,
        )

    # ==================================================
    # Interface
    # ==================================================

    def _build_interface(self):
        self.intro_label = ctk.CTkLabel(
            self,
            text="Personalize your Chimera workspace",
            font=self.font_section,
        )

        self.intro_label.grid(
            row=0,
            column=0,
            padx=26,
            pady=(24, 8),
            sticky="w",
        )

        self.description_label = ctk.CTkLabel(
            self,
            text=(
                "Appearance changes apply immediately. "
                "More personal settings can be added here "
                "as the program grows."
            ),
            font=self.font_normal,
            justify="left",
            wraplength=760,
        )

        self.description_label.grid(
            row=1,
            column=0,
            padx=26,
            pady=(0, 14),
            sticky="w",
        )

        self._build_appearance_card()

        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=self.font_small,
        )

        self.status_label.grid(
            row=3,
            column=0,
            padx=26,
            pady=16,
            sticky="w",
        )

        self._update_status()

    def _build_appearance_card(self):
        self.appearance_card = ctk.CTkFrame(
            self,
            corner_radius=18,
            border_width=1,
        )

        self.appearance_card.grid(
            row=2,
            column=0,
            padx=26,
            pady=10,
            sticky="new",
        )

        self.appearance_card.grid_columnconfigure(
            1,
            weight=1,
        )

        self.appearance_heading = ctk.CTkLabel(
            self.appearance_card,
            text="Appearance",
            font=self.font_section,
        )

        self.appearance_heading.grid(
            row=0,
            column=0,
            columnspan=2,
            padx=20,
            pady=(18, 14),
            sticky="w",
        )

        self._label(
            self.appearance_card,
            "Color scheme",
        ).grid(
            row=1,
            column=0,
            padx=20,
            pady=10,
            sticky="w",
        )

        self.theme_menu = self._option_menu(
            self.appearance_card,
            self.theme_var,
            list(THEMES.keys()),
            self.on_theme_selected,
            width=230,
        )

        self.theme_menu.grid(
            row=1,
            column=1,
            padx=20,
            pady=10,
            sticky="e",
        )

        self._label(
            self.appearance_card,
            "Text font size",
        ).grid(
            row=2,
            column=0,
            padx=20,
            pady=10,
            sticky="w",
        )

        self.font_size_menu = self._option_menu(
            self.appearance_card,
            self.font_size_var,
            list(FONT_SIZES.keys()),
            self.on_font_size_selected,
            width=230,
        )

        self.font_size_menu.grid(
            row=2,
            column=1,
            padx=20,
            pady=10,
            sticky="e",
        )

        self.button_row = ctk.CTkFrame(
            self.appearance_card,
            fg_color="transparent",
        )

        self.button_row.grid(
            row=3,
            column=0,
            columnspan=2,
            pady=(18, 20),
        )

        self.restore_defaults_button = self._button(
            self.button_row,
            "Restore Defaults",
            self.restore_defaults,
            width=180,
            secondary=True,
        )

        self.restore_defaults_button.grid(
            row=0,
            column=0,
            padx=8,
        )

    # ==================================================
    # Widget helpers
    # ==================================================

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
    # Theme controls
    # ==================================================

    def on_theme_selected(
        self,
        theme_name,
    ):
        self.current_theme_name = theme_name
        self.current_theme = THEMES[theme_name]

        self.apply_theme()
        self._update_status()

    # ==================================================
    # Font controls
    # ==================================================

    def on_font_size_selected(
        self,
        size_name,
    ):
        self.current_font_size_name = size_name

        self.base_font_size = FONT_SIZES[
            size_name
        ]

        self._update_font_objects()

        # Transparency placeholder uses the numeric
        # base font size rather than a CTkFont.
        if hasattr(
            self.app,
            "transparency_image_tab",
        ):
            self.app.transparency_image_tab.apply_theme_overrides(
                self.current_theme,
                self.base_font_size,
            )

        self._update_status()

    def _update_font_objects(self):
        size = self.base_font_size

        self.font_normal.configure(
            size=size
        )

        self.font_small.configure(
            size=max(10, size - 2)
        )

        self.font_bold.configure(
            size=size
        )

        self.font_section.configure(
            size=size + 2
        )

        self.font_title.configure(
            size=size + 15
        )

        self.font_subtitle.configure(
            size=size
        )

    # ==================================================
    # Restore defaults
    # ==================================================

    def restore_defaults(self):
        self.theme_var.set(
            DEFAULT_THEME_NAME
        )

        self.font_size_var.set(
            DEFAULT_FONT_SIZE_NAME
        )

        self.on_theme_selected(
            DEFAULT_THEME_NAME
        )

        self.on_font_size_selected(
            DEFAULT_FONT_SIZE_NAME
        )

    # ==================================================
    # Status
    # ==================================================

    def _update_status(self):
        self.status_label.configure(
            text=(
                f"Current profile: "
                f"{self.current_theme_name} · "
                f"{self.current_font_size_name} text"
            )
        )

    # ==================================================
    # Global Chimera theming
    # ==================================================

    def apply_theme(self):
        theme = self.current_theme
        app = self.app

        # ------------------------------------------
        # Main application shell
        # ------------------------------------------

        app.configure(
            fg_color=theme["window"]
        )

        app.header_frame.configure(
            fg_color=theme["window"]
        )

        app.title_label.configure(
            text_color=theme["text"]
        )

        app.subtitle_label.configure(
            text_color=theme["muted"]
        )

        # ------------------------------------------
        # Main tab container
        # ------------------------------------------

        app.tabview.configure(
            fg_color=theme["window"],
            border_color=theme["border"],
            segmented_button_fg_color=theme["surface_alt"],
            segmented_button_selected_color=theme["accent"],
            segmented_button_selected_hover_color=theme["accent_hover"],
            segmented_button_unselected_color=theme["surface_alt"],
            segmented_button_unselected_hover_color=theme["entry_border"],
            text_color=theme["text"],
        )

        # Explicitly theme the actual tab page backgrounds.
        app.single_tab.configure(
            fg_color=theme["window"]
        )

        app.bulk_tab.configure(
            fg_color=theme["window"]
        )

        app.transparency_tab.configure(
            fg_color=theme["window"]
        )

        app.settings_tab.configure(
            fg_color=theme["window"]
        )

        # ------------------------------------------
        # Theme only OUR component trees
        # ------------------------------------------

        self._apply_theme_recursive(
            app.single_image_tab
        )

        self._apply_theme_recursive(
            app.bulk_image_tab
        )

        self._apply_theme_recursive(
            app.transparency_image_tab
        )

        self._apply_theme_recursive(
            self
        
        )

    # ------------------------------------------
    # Tab-specific exceptions
    # ------------------------------------------

        app.single_image_tab.apply_theme_overrides(
            theme
        )

        app.bulk_image_tab.apply_theme_overrides(
            theme
        )

        app.transparency_image_tab.apply_theme_overrides(
            theme,
            self.base_font_size,
        )

        self.description_label.configure(
            text_color=theme["muted"]
        )

        self.status_label.configure(
            text_color=theme["muted"]
        )

    def _apply_theme_recursive(
        self,
        widget,
    ):
        theme = self.current_theme

        for child in widget.winfo_children():
            try:
                if isinstance(
                    child,
                    ctk.CTkFrame,
                ):
                    if child.cget(
                        "fg_color"
                    ) != "transparent":
                        child.configure(
                            fg_color=theme["surface"],
                            border_color=theme["border"],
                        )

                elif isinstance(
                    child,
                    ctk.CTkLabel,
                ):
                    # Preserve the black header shadow.
                    if child is not self.app.title_shadow:
                        child.configure(
                            text_color=theme["text"]
                        )

                elif isinstance(
                    child,
                    ctk.CTkEntry,
                ):
                    child.configure(
                        fg_color=theme["entry"],
                        border_color=theme[
                            "entry_border"
                        ],
                        text_color=theme["text"],
                        placeholder_text_color=theme[
                            "muted"
                        ],
                    )

                elif isinstance(
                    child,
                    ctk.CTkButton,
                ):
                    if getattr(
                        child,
                        "_chimera_secondary",
                        False,
                    ):
                        child.configure(
                            fg_color=theme[
                                "surface_alt"
                            ],
                            hover_color=theme[
                                "entry_border"
                            ],
                            border_color=theme[
                                "accent"
                            ],
                            text_color=theme["text"],
                        )

                    else:
                        child.configure(
                            fg_color=theme["accent"],
                            hover_color=theme[
                                "accent_hover"
                            ],
                            text_color="#151515",
                        )

                elif isinstance(
                    child,
                    ctk.CTkOptionMenu,
                ):
                    child.configure(
                        fg_color=theme["entry"],
                        button_color=theme["accent"],
                        button_hover_color=theme[
                            "accent_hover"
                        ],
                        dropdown_fg_color=theme[
                            "surface_alt"
                        ],
                        dropdown_hover_color=theme[
                            "accent"
                        ],
                        text_color=theme["text"],
                        dropdown_text_color=theme[
                            "text"
                        ],
                    )

                elif isinstance(
                    child,
                    ctk.CTkSlider,
                ):
                    child.configure(
                        fg_color=theme[
                            "entry_border"
                        ],
                        progress_color=theme[
                            "accent"
                        ],
                        button_color=theme[
                            "accent"
                        ],
                        button_hover_color=theme[
                            "accent_hover"
                        ],
                    )

                elif isinstance(
                    child,
                    ctk.CTkCheckBox,
                ):
                    child.configure(
                        fg_color=theme["accent"],
                        hover_color=theme[
                            "accent_hover"
                        ],
                        border_color=theme[
                            "entry_border"
                        ],
                        text_color=theme["text"],
                    )

            except (
                tk.TclError,
                ValueError,
            ):
                pass

            self._apply_theme_recursive(
                app.single_image_tab
            )

            self._apply_theme_recursive(
                app.bulk_image_tab
            )

            self._apply_theme_recursive(
                app.transparency_image_tab
            )

            self._apply_theme_recursive(
                self
            )
