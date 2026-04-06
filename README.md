# Image Management Facilitator

A CustomTkinter image-sorting GUI application organized into a small package.

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

## Notes

- Images are loaded from a source folder
- Destination folders can be added as buttons
- You can bind a key shortcut to each destination button
- Deleted images are moved into a `Deleted/` subfolder inside the source directory
