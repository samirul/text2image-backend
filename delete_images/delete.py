"""
    For deleting specific data from the docker container.
"""

import subprocess

def delete_data_from_media_container(path_to_delete):
    """Delete data from the docker container.

    Args:
        path_to_delete (String): Path/file name to delete from the docker container.
    """
    try:
        command = f"rm -rf {path_to_delete}"
        subprocess.run(command, shell=True, check=True)
        print(f"{path_to_delete} deleted")
    except subprocess.CalledProcessError as e:
        print(f"Failed to delete {path_to_delete} Error: {e}")