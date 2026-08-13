import customtkinter as ctk
from Main_Functions.single_image_tab import SingleImageTab
from Main_Functions.bulk_image_tab import BulkImageTab
from Main_Functions.transparency_tab import TransparencyTab
from Main_Functions.settings_tab import (
    SettingsTab,
    THEMES,
    FONT_SIZES,
    DEFAULT_THEME_NAME,
    DEFAULT_FONT_SIZE_NAME,
)


# --------------------------------------------------
# Application configuration
# --------------------------------------------------

APP_NAME = "Chimera Image Modifier"
OUTPUT_FOLDER = "Modified Images"


# --------------------------------------------------
# Main application
# --------------------------------------------------

class ChimeraImageModifier(ctk.CTk):

    def __init__(self):
        super().__init__()

        # ------------------------------------------
        # Initial appearance
        # ------------------------------------------

        self.current_theme_name = DEFAULT_THEME_NAME
        self.current_font_size_name = DEFAULT_FONT_SIZE_NAME

        self.current_theme = THEMES[
            self.current_theme_name
        ]

        self.base_font_size = FONT_SIZES[
            self.current_font_size_name
        ]

        ctk.set_appearance_mode(
            self.current_theme["appearance"]
        )

        ctk.set_default_color_theme(
            "blue"
        )

        # ------------------------------------------
        # Window configuration
        # ------------------------------------------

        self.title(APP_NAME)
        self.geometry("1050x820")
        self.minsize(900, 720)
        self.resizable(True, True)

        self.configure(
            fg_color=self.current_theme["window"]
        )

        # ------------------------------------------
        # Build application
        # ------------------------------------------

        self._create_fonts()
        self._build_interface()

        # Apply the initial Chimera appearance
        # after every component has been created.
        self.settings_component.apply_theme()

    # ==================================================
    # Shared fonts
    # ==================================================

    def _create_fonts(self):
        size = self.base_font_size

        self.font_normal = ctk.CTkFont(
            family="Segoe UI",
            size=size,
        )

        self.font_small = ctk.CTkFont(
            family="Segoe UI",
            size=max(10, size - 2),
        )

        self.font_bold = ctk.CTkFont(
            family="Segoe UI",
            size=size,
            weight="bold",
        )

        self.font_section = ctk.CTkFont(
            family="Segoe UI",
            size=size + 2,
            weight="bold",
        )

        self.font_title = ctk.CTkFont(
            family="Segoe UI",
            size=size + 15,
            weight="bold",
        )

        self.font_subtitle = ctk.CTkFont(
            family="Segoe UI",
            size=size,
            slant="italic",
        )

    # ==================================================
    # Main interface
    # ==================================================

    def _build_interface(self):
        self.grid_columnconfigure(
            0,
            weight=1,
        )

        self.grid_rowconfigure(
            1,
            weight=1,
        )

        self._build_header()
        self._build_tabview()
        self._build_components()

    # ==================================================
    # Header
    # ==================================================

    def _build_header(self):
        self.header_frame = ctk.CTkFrame(
            self,
            corner_radius=0,
        )

        self.header_frame.grid(
            row=0,
            column=0,
            sticky="ew",
        )

        self.header_frame.grid_columnconfigure(
            0,
            weight=1,
        )

        # Black offset duplicate creates the
        # title outline / shadow effect.
        self.title_shadow = ctk.CTkLabel(
            self.header_frame,
            text=APP_NAME,
            font=self.font_title,
            text_color="#000000",
        )

        self.title_shadow.grid(
            row=0,
            column=0,
            padx=(33, 29),
            pady=(22, 0),
        )

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=APP_NAME,
            font=self.font_title,
        )

        self.title_label.grid(
            row=0,
            column=0,
            padx=30,
            pady=(19, 0),
        )

        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text=(
                "Resize, convert, and organize "
                "images with precision."
            ),
            font=self.font_subtitle,
        )

        self.subtitle_label.grid(
            row=1,
            column=0,
            padx=30,
            pady=(2, 18),
        )

    # ==================================================
    # Tab container
    # ==================================================

    def _build_tabview(self):
        self.tabview = ctk.CTkTabview(
            self,
            corner_radius=18,
            border_width=1,
            segmented_button_selected_hover_color=None,
        )

        self.tabview.grid(
            row=1,
            column=0,
            padx=24,
            pady=(0, 24),
            sticky="nsew",
        )

        self.tabview.add(
            "Single Image Resize"
        )

        self.tabview.add(
            "Bulk Image Resize"
        )

        self.tabview.add(
            "Transparency Editor"
        )

        self.tabview.add(
            "Personal Settings"
        )

        self.tabview.set(
            "Single Image Resize"
        )

        self.single_tab = self.tabview.tab(
            "Single Image Resize"
        )

        self.bulk_tab = self.tabview.tab(
            "Bulk Image Resize"
        )

        self.transparency_tab = self.tabview.tab(
            "Transparency Editor"
        )

        self.settings_tab = self.tabview.tab(
            "Personal Settings"
        )

    # ==================================================
    # Feature components
    # ==================================================

    def _build_components(self):

        # ------------------------------------------
        # Single Image Resize
        # ------------------------------------------

        self.single_image_tab = SingleImageTab(
            parent=self.single_tab,
            font_normal=self.font_normal,
            font_small=self.font_small,
            font_bold=self.font_bold,
            font_section=self.font_section,
            output_folder=OUTPUT_FOLDER,
        )

        # ------------------------------------------
        # Bulk Image Resize
        # ------------------------------------------

        self.bulk_image_tab = BulkImageTab(
            parent=self.bulk_tab,
            font_normal=self.font_normal,
            font_small=self.font_small,
            font_bold=self.font_bold,
            font_section=self.font_section,
            output_folder=OUTPUT_FOLDER,
        )

        # ------------------------------------------
        # Transparency Editor
        # ------------------------------------------

        self.transparency_image_tab = TransparencyTab(
            parent=self.transparency_tab,
            font_normal=self.font_normal,
            font_small=self.font_small,
            font_bold=self.font_bold,
            font_section=self.font_section,
            current_theme=self.current_theme,
            base_font_size=self.base_font_size,
            output_folder=OUTPUT_FOLDER,
        )

        # ------------------------------------------
        # Personal Settings
        # ------------------------------------------

        self.settings_component = SettingsTab(
            parent=self.settings_tab,
            app=self,
            font_normal=self.font_normal,
            font_small=self.font_small,
            font_bold=self.font_bold,
            font_section=self.font_section,
            font_title=self.font_title,
            font_subtitle=self.font_subtitle,
            theme_name=self.current_theme_name,
            font_size_name=self.current_font_size_name,
        )


# --------------------------------------------------
# Launch Chimera Image Modifier
# --------------------------------------------------

if __name__ == "__main__":
    app = ChimeraImageModifier()
    app.mainloop()