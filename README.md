# Chimera Image Modifier

Chimera Image Modifier is a desktop image-processing application built with Python, CustomTkinter, and Pillow.

The project provides focused tools for resizing individual images, processing image batches, and editing image transparency through a custom graphical interface.

## Features

### Single Image Resize
* Resize individual JPG, JPEG, and PNG images.
* Enter custom width and height values.
* Preserve the original aspect ratio when desired.
* Use preset image dimensions.
* Preview the resized image before saving.
* Export as PNG or JPEG.

### Bulk Image Resize
* Process an entire folder of supported images.
* Apply one resize configuration across multiple images.
* Preserve aspect ratio when desired.
* Use preset or custom dimensions.
* Preview the first supported image before processing.
* Automatically number output files.
* Export batches as PNG or JPEG.

### Transparency Editor
* Load JPG, JPEG, and PNG images for transparency editing.
* Erase image areas using an adjustable transparency brush.
* Restore previously erased image areas.
* Adjustable brush size.
* Undo and redo editing actions.
* Reset removed areas.
* Zoom in, zoom out, and fit images to the canvas.
* Scroll across enlarged images.
* Checkerboard transparency preview.
* Rotate images left or right.
* Flip images across the X-axis or Y-axis.
* Interactive crop selection directly on the canvas.
* Smooth transparency edges with adjustable strength.
* Save completed images as transparent PNG files.

### Personal Settings
* Different color schemes. (Chimera Default theme, a Light theme, and a Dark theme)
* Adjustable interface font sizes.

## Project Structure

The application has been refactored into feature-specific modules to keep the main application file focused on application startup and shared interface construction.

```text
Chimera Image Modifier/
├── main.py
├── Main_Functions/
│   ├── single_image_tab.py
│   ├── bulk_image_tab.py
│   ├── transparency_tab.py
│   └── settings_tab.py
├── assets/
└── Modified Images/
---

## Technologies Used

* Python
* CustomTkinter
* Tkinter
* Pillow
* Git
* GitHub

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/JuanBalderas1/automatic-image-resizer.git
```

### 2. Navigate into the project directory

```bash
cd automatic-image-resizer
```

### 3. Install the required dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the application

```bash
python main.py
```

---

## Output

All resized, converted, and transparency-edited images are saved inside:

```text
Modified Images
```

The folder is created automatically when the first image is saved.

---

## Transparency Editor Controls

| Control               | Action              |
| --------------------- | ------------------- |
| `Ctrl + Z`            | Undo                |
| `Ctrl + Y`            | Redo                |
| Mouse wheel           | Scroll vertically   |
| `Shift + Mouse Wheel` | Scroll horizontally |
| `Ctrl + Mouse Wheel`  | Zoom in or out      |

---

## Screenshots

### Single Image Resize

![Single Image Resize](assets/Screenshot-Single-Tab.png)

### Bulk Image Resize

![Bulk Image Resize](assets/Screenshot-Bulk-Tab.png)

### Transparency Editor

![Transparency Editor](assets/Screenshot-Transparency-Editor.png)

### Personal Settings

![Personal Settings](assets/Screenshot-Personal-Settings.png)

---

## Planned Improvements

Potential future additions include:

* Drag-and-drop image importing
* Persistent user settings
* Polygon and lasso transparency tools
* Additional export-quality controls

---

## Author

Developed by **Juan Balderas**

Part of the **Chimera Project Series**.

---

## License

This project is currently maintained as a personal portfolio and learning project. Licensing information may be added in a future release.
