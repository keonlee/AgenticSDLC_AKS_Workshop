import tempfile
import unittest
from pathlib import Path

from update_image import update_image


class UpdateImageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "kustomization.yaml"
        self.initial = (
            "images:\n  - name: workshop-app\n"
            "    newName: registry.invalid/workshop-app\n"
            f"    digest: sha256:{'0' * 64}\n"
        )
        self.path.write_text(self.initial, encoding="utf-8")

    def test_updates_registry_and_digest(self):
        digest = "sha256:" + "a" * 64
        update_image(self.path, "workshop123.azurecr.io", digest)
        content = self.path.read_text(encoding="utf-8")
        self.assertIn("newName: workshop123.azurecr.io/workshop-app", content)
        self.assertIn("digest: " + digest, content)
        self.assertIn("name: workshop-app", content)

    def test_rejects_bad_inputs_without_writing(self):
        for registry, digest in [
            ("https://example.com", "sha256:" + "a" * 64),
            ("workshop.azurecr.io", "latest"),
            ("workshop.azurecr.io\ninjected: true", "sha256:" + "a" * 64),
            ("-workshop.azurecr.io", "sha256:" + "a" * 64),
            ("workshop-.azurecr.io", "sha256:" + "a" * 64),
        ]:
            with self.subTest(registry=registry, digest=digest):
                with self.assertRaises(ValueError):
                    update_image(self.path, registry, digest)
                self.assertEqual(self.path.read_text(encoding="utf-8"), self.initial)

    def test_accepts_domain_name_label_hash(self):
        update_image(
            self.path, "workshop123-abc456.azurecr.io", "sha256:" + "b" * 64
        )
        self.assertIn(
            "newName: workshop123-abc456.azurecr.io/workshop-app",
            self.path.read_text(encoding="utf-8"),
        )

    def test_rejects_unexpected_overlay_without_writing(self):
        self.path.write_text("images: []\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            update_image(self.path, "workshop.azurecr.io", "sha256:" + "a" * 64)
        self.assertEqual(self.path.read_text(encoding="utf-8"), "images: []\n")


if __name__ == "__main__":
    unittest.main()
