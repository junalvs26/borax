import os
import shutil
import tempfile
import unittest
from knowledge_manager import KnowledgeManager

class TestKnowledgeDrive(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.sample_txt = os.path.join(self.test_dir, "cartucho_teste.txt")
        with open(self.sample_txt, "w", encoding="utf-8") as f:
            f.write("Este é um documento de teste montado no leitor de cartuchos do BORAX. Contém dados de física quântica.")

        self.km = KnowledgeManager()

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_01_mount_document(self):
        status_initial = self.km.get_active_status()
        self.assertFalse(status_initial["mounted"])

        mount_res = self.km.mount_media(self.sample_txt, file_name="cartucho_teste.txt")
        self.assertEqual(mount_res["status"], "success")

        status_mounted = self.km.get_active_status()
        self.assertTrue(status_mounted["mounted"])
        self.assertEqual(status_mounted["name"], "Cartucho_teste")
        self.assertGreater(status_mounted["vectors_count"], 0)

    def test_02_eject_document(self):
        self.km.mount_media(self.sample_txt, file_name="cartucho_teste.txt")
        eject_res = self.km.eject_media()
        self.assertEqual(eject_res["status"], "success")

        status_after = self.km.get_active_status()
        self.assertFalse(status_after["mounted"])

if __name__ == "__main__":
    unittest.main()
