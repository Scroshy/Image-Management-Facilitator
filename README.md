# Image Management Facilitator

A CustomTkinter image-sorting GUI application with zoom and navigation features.

## Project Structure

- `main.py` — application entrypoint
- `image_sorter/` — package containing the UI and file operations
  - `image_sorter/ui.py` — UI and event handling logic
  - `image_sorter/fileops.py` — filesystem helpers for loading and moving images
  - `image_sorter/__init__.py` — package export

## Running

Install dependencies and run the app:

```bash
python main.py
```

## Features

### Image Navigation
- **Previous/Next Buttons** — navigate between images
- **Arrow Keys** — use ← and → for navigation
- **Direct Jump** — enter an image number to jump directly to it

### Image Sorting
- **Add Destination Folders** — create buttons for target directories
- **Key Bindings** — assign keyboard shortcuts to destination buttons for quick sorting
- **Delete Option** — move unwanted images to a `Deleted/` subfolder in the source directory

### Image Zoom
- **Zoom Buttons** — click 🔍+ to zoom in and 🔍− to zoom out
- **Mouse Wheel** — scroll up to zoom in, scroll down to zoom out
- **Trackpad Pinch** — pinch gestures to zoom in/out (Windows laptops)
- **Reset Button** — return to 100% zoom instantly
- **Persistent Zoom** — zoom level carries over when navigating between images
- **Zoom Range** — zoom from 50% to 300% in 20% increments

## Usage

1. Click **"Select Source Folder"** to choose a directory with images
2. Click **"Add Target Folder"** to create destination buttons for sorting
3. Optionally bind keyboard shortcuts to speed up sorting
4. Navigate images using Previous/Next buttons, arrow keys, or direct jump
5. Use zoom controls to inspect image details
6. Click a destination button or press its bound key to move the image
