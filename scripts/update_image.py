import argparse
import re
from pathlib import Path


def update_image(path, registry, digest):
    if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.azurecr\.io", registry):
        raise ValueError("Expected a public Azure ACR login server")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        raise ValueError("Expected an immutable SHA-256 image digest")
    content = path.read_text(encoding="utf-8")
    updated, names = re.subn(
        r"(?m)^    newName: .+$",
        f"    newName: {registry}/workshop-app",
        content,
    )
    updated, digests = re.subn(
        r"(?m)^    digest: .+$",
        f"    digest: {digest}",
        updated,
    )
    if names != 1 or digests != 1:
        raise ValueError("Expected exactly one newName and digest in dev overlay")
    path.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--digest", required=True)
    args = parser.parse_args()
    update_image(
        Path("deploy/overlays/dev/kustomization.yaml"), args.registry, args.digest
    )
