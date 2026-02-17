"""Integration tests for build cancellation (Story 2.15 Task 15)

Tests the complete cancellation workflow.
"""

import unittest
import logging
import tempfile
import time
import subprocess
from pathlib import Path
from unittest.mock import Mock

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from core.models import (
    ProjectConfig,
    WorkflowConfig,
    BuildContext,
    BuildState,
    StageConfig,
    BuildExecution
)
from core.workflow_thread import WorkflowThread
from utils.process_mgr import terminate_process
from utils.file_ops import cleanup_temp_files
from utils.cancel import (
    save_cancelled_config,
    load_cancelled_config,
    delete_cancelled_config,
    list_cancelled_builds
)

logger = logging.getLogger(__name__)


class TestCancelBuildIntegration(unittest.TestCase):
    """Test build cancellation integration"""

    @classmethod
    def setUpClass(cls):
        """Setup test environment"""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication([])

    def setUp(self):
        """Setup each test"""
        self.temp_base = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Cleanup after each test"""
        if self.temp_base.exists():
            import shutil
            shutil.rmtree(self.temp_base, ignore_errors=True)

    def test_temp_files_cleanup(self):
        """Test 15.6: Test temp files cleanup"""
        temp_dir = self.temp_base / "temp_cleanup_test"
        temp_dir.mkdir()

        (temp_dir / "file1.txt").write_text("test1")
        (temp_dir / "file2.txt").write_text("test2")

        subdir = temp_dir / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").write_text("test3")

        # Verify files exist
        self.assertTrue(temp_dir.exists())
        self.assertEqual(len(list(temp_dir.rglob("*"))), 4)  # 3 files + 1 dir

        # Cleanup temp files
        result = cleanup_temp_files(temp_dir)

        # Verify cleanup success
        self.assertTrue(result["success"], "Cleanup should succeed")
        self.assertEqual(result["deleted_count"], 3, "Should delete 3 files")

        # Verify directory deleted
        self.assertFalse(temp_dir.exists(), "Temp directory should be deleted")

        logger.info("Temp files cleanup test passed")

    def test_temp_files_cleanup_with_error_handling(self):
        """Test 15.10: Test temp files cleanup error handling"""
        temp_dir = self.temp_base / "nonexistent"

        result = cleanup_temp_files(temp_dir)

        self.assertTrue(result["success"], "Non-existent directory should succeed")
        self.assertEqual(result["deleted_count"], 0)

        logger.info("Temp files cleanup error handling test passed")

    def test_process_termination(self):
        """Test 15.5: Test process termination"""
        proc = subprocess.Popen(["python", "-c", "import time; time.sleep(30)"])

        # Verify process is running
        self.assertIsNone(proc.poll(), "Process should be running")

        # Terminate process
        success, suggestions = terminate_process(proc, timeout=5)

        # Verify process terminated
        self.assertTrue(success, "Process should terminate successfully")
        self.assertIsNotNone(proc.poll(), "Process should have exited")

        # Verify no suggestions on success
        self.assertEqual(len(suggestions), 0, "No suggestions on success")

        logger.info("Process termination test passed")

    def test_cancelled_config_save_and_load(self):
        """Test 15.9: Test cancelled config save and load"""
        project_name = "TestProject"
        config = {
            "simulink_path": str(self.temp_base / "simulink"),
            "matlab_code_path": str(self.temp_base / "matlab"),
            "iar_project_path": str(self.temp_base / "iar"),
            "a2l_path": str(self.temp_base / "a2l"),
            "target_path": str(self.temp_base / "target")
        }
        state = {"build_start_time": time.time()}
        current_stage = "test_stage"
        completed_stages = ["stage1", "stage2"]

        # Save cancelled config
        saved_path = save_cancelled_config(
            project_name, config, state, current_stage, completed_stages
        )

        # Verify save success
        self.assertIsNotNone(saved_path, "Config should save successfully")
        self.assertTrue(saved_path.exists(), "Config file should exist")

        # Load cancelled config
        loaded_data = load_cancelled_config(saved_path)

        # Verify load success
        self.assertIsNotNone(loaded_data, "Config should load successfully")
        self.assertEqual(loaded_data["project_name"], project_name)
        self.assertEqual(loaded_data["current_stage"], current_stage)
        self.assertEqual(loaded_data["completed_stages"], completed_stages)

        # Cleanup test file
        delete_cancelled_config(saved_path)

        logger.info("Cancelled config save and load test passed")

    def test_list_and_delete_cancelled_builds(self):
        """Test 15.9: Test list and delete cancelled builds"""
        # Create multiple cancelled configs
        for i in range(3):
            project_name = f"TestProject_{i}"
            config = {"test": f"value_{i}"}
            state = {"test": f"state_{i}"}
            save_cancelled_config(project_name, config, state)

        # List all cancelled builds
        cancelled_builds = list_cancelled_builds()

        # Verify list
        self.assertGreaterEqual(len(cancelled_builds), 3, "Should have at least 3 cancelled builds")

        # Delete all test configs
        for build in cancelled_builds:
            if build["project_name"].startswith("TestProject_"):
                delete_cancelled_config(build["filepath"])

        # List again, test configs should be gone
        cancelled_builds = list_cancelled_builds()
        test_builds = [
            b for b in cancelled_builds
            if b["project_name"].startswith("TestProject_")
        ]
        self.assertEqual(len(test_builds), 0, "Test configs should be deleted")

        logger.info("List and delete cancelled builds test passed")


if __name__ == "__main__":
    unittest.main()
