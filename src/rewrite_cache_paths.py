
# iterate the DATA_DIR directory and list all directories
import os
from pathlib import Path
import shutil

from webcheck.conf import WEBCHECK_DATA_DIR
from webcheck.util.content_helper import reverse_domain_path


def rewrite_cache_paths(old_base_dir: str, new_base_dir: str) -> None:
    for root, dirs, files in os.walk(old_base_dir):
        for domain in dirs:
            old_dir = Path(root) / domain
            new_dir = Path(new_base_dir) / reverse_domain_path(domain)
            new_dir.mkdir(parents=True, exist_ok=True)
            print(f"Copy {old_dir} -> {new_dir}")
            shutil.copytree(old_dir, new_dir, dirs_exist_ok=True)


if __name__ == "__main__":
    rewrite_cache_paths(WEBCHECK_DATA_DIR + "/cache.1", WEBCHECK_DATA_DIR + "/cache")
