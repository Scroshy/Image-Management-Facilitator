import os
import shutil

VALID_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp', '.bmp')


def load_image_paths(folder_path):
    return [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.lower().endswith(VALID_EXTENSIONS)
    ]


def ensure_deleted_folder(source_file):
    deleted_folder = os.path.join(os.path.dirname(source_file), "Deleted")
    os.makedirs(deleted_folder, exist_ok=True)
    return deleted_folder


def safe_destination_path(destination_dir, filename):
    dest_file = os.path.join(destination_dir, filename)
    base, ext = os.path.splitext(dest_file)
    counter = 1
    while os.path.exists(dest_file):
        dest_file = f"{base} ({counter}){ext}"
        counter += 1
    return dest_file


def move_image(source_path, destination_dir):
    dest_path = safe_destination_path(destination_dir, os.path.basename(source_path))
    shutil.move(source_path, dest_path)
    return dest_path


def move_to_deleted_folder(source_path):
    deleted_folder = ensure_deleted_folder(source_path)
    return move_image(source_path, deleted_folder)
