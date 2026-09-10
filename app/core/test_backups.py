import hashlib
import json
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.backup_service import BACKUP_FORMAT, BackupError, inspect_backup


class BackupAccessTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin = user_model.objects.create_user(username="admin-backup", password="test-pass-123", role="admin")
        self.user = user_model.objects.create_user(username="warden-backup", password="test-pass-123", role="youth_warden")

    def test_admin_can_open_backup_center(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("core:backup_center"))
        self.assertEqual(response.status_code, 200)

    def test_non_admin_cannot_open_backup_center(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("core:backup_center"))
        self.assertEqual(response.status_code, 403)


class BackupArchiveTests(TestCase):
    @patch("core.backup_service._run")
    def test_valid_archive_is_accepted(self, mocked_run):
        with tempfile.TemporaryDirectory() as temp_name:
            path = Path(temp_name) / "backup.zip"
            dump = b"database"
            manifest = {
                "format": BACKUP_FORMAT,
                "database_sha256": hashlib.sha256(dump).hexdigest(),
            }
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("database.dump", dump)
                archive.writestr("manifest.json", json.dumps(manifest))
            result = inspect_backup(path)
            self.assertEqual(result["format"], BACKUP_FORMAT)

    def test_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp_name:
            path = Path(temp_name) / "backup.zip"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("../evil", b"x")
                archive.writestr("database.dump", b"x")
                archive.writestr("manifest.json", json.dumps({"format": BACKUP_FORMAT}))
            with self.assertRaises(BackupError):
                inspect_backup(path)
