import os


def get_deduplicated_destination_path(destination_path: str) -> str:
    counter = 1
    deduplicated_destination_path = destination_path
    while os.path.exists(deduplicated_destination_path):
        path_parts = destination_path.rsplit(".")
        path_parts[0] = f"{path_parts[0]}_{counter}"

        # add extension after split if present
        if "." in destination_path:
            path_parts[0] += "."

        counter += 1
        deduplicated_destination_path = "".join(path_parts)

    return deduplicated_destination_path
