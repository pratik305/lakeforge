import pathlib


def upload_directory(client, local_dir, bucket_name):
    keys = []
    for path in sorted(pathlib.Path(local_dir).rglob("*.parquet")):
        relative_path = path.relative_to(local_dir)
        key = str(relative_path).replace("\\", "/")
        client.upload_file(str(path), bucket_name, key)
        keys.append(key)
    return keys
