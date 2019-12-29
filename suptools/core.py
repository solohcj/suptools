# AUTOGENERATED! DO NOT EDIT! File to edit: dev/00_core.ipynb (unless otherwise specified).

__all__ = ['get_all_files']

# Cell
import pathlib

# Cell
def get_all_files(file_path, recurse=False):
    """
    Returns all files in a directory.
    Supports return of files from sub-directories if recurse=True is passed.
    """
    path = pathlib.Path(file_path)
    if recurse:
        tmp = path.rglob('**/*')
    else:
        tmp = path.glob('**/*')
    all_files = [x for x in tmp if x.is_file()]
    return all_files