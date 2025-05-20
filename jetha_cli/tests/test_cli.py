import os
import shutil
import subprocess
import unittest
from click.testing import CliRunner

# Assuming jetha_bhai is in jetha_cli/src/__init__.py
# This import works if tests are run from 'jetha_cli' directory
# and 'jetha_cli' parent directory is in PYTHONPATH, or if jetha_cli is installed.
from src import jetha_bhai

class TestGitCommands(unittest.TestCase):
    def setUp(self):
        """Set up a temporary directory for testing."""
        # Create a test directory *inside* the current working directory (which will be /app/jetha_cli)
        # This keeps test artifacts somewhat contained within the project structure during testing
        self.test_dir_name = "temp_test_dir_for_cli"
        os.makedirs(self.test_dir_name, exist_ok=True)
        
        # Store the CWD at the beginning of setUp (e.g. /app/jetha_cli)
        self.original_cwd = os.getcwd()
        
        # Change CWD to the newly created temporary directory
        os.chdir(self.test_dir_name)

    def tearDown(self):
        """Clean up the temporary directory."""
        # Change back to the original CWD *before* trying to remove the test_dir
        os.chdir(self.original_cwd)
        
        # Remove the temporary directory
        shutil.rmtree(self.test_dir_name, ignore_errors=True)

    def test_git_chalu_karo(self):
        runner = CliRunner()
        # We are now in self.test_dir_name, e.g., /app/jetha_cli/temp_test_dir_for_cli
        result = runner.invoke(jetha_bhai, ["git-chalu-karo"])
        
        if result.exception:
            print(f"Exception in git-chalu-karo: {result.exception}")
            import traceback
            traceback.print_exception(type(result.exception), result.exception, result.exc_info[2])
        self.assertEqual(result.exit_code, 0, msg=f"CLI command 'git-chalu-karo' failed with output: {result.output}")
        self.assertTrue(os.path.isdir(".git"), "'.git' directory was not created in the test directory.")

    def test_commit_maro(self):
        runner = CliRunner()
        # We are in self.test_dir_name

        # 1. Initialize a Git repository using the CLI command
        init_result = runner.invoke(jetha_bhai, ["git-chalu-karo"])
        self.assertEqual(init_result.exit_code, 0, f"Pre-requisite 'git-chalu-karo' failed: {init_result.output}")
        self.assertTrue(os.path.isdir(".git"), "'.git' directory was not created by git-chalu-karo.")

        # 2. Create a dummy file
        dummy_file = "test_file.txt"
        with open(dummy_file, "w") as f:
            f.write("This is a test file for commit-maro.")
        
        # 3. Stage the file using git add (subprocess, as CLI doesn't have 'add' yet)
        # Ensure git is configured with a user, otherwise commit might fail
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True)
        stage_process = subprocess.run(["git", "add", dummy_file], capture_output=True, text=True)
        self.assertEqual(stage_process.returncode, 0, f"git add failed: {stage_process.stderr}")

        # 4. Run the commit-maro command
        commit_message = "Test commit via commit-maro"
        commit_result = runner.invoke(jetha_bhai, ["commit-maro", commit_message])
        
        if commit_result.exception:
            print(f"Exception in commit-maro: {commit_result.exception}")
            import traceback
            traceback.print_exception(type(commit_result.exception), commit_result.exception, commit_result.exc_info[2])
        self.assertEqual(commit_result.exit_code, 0, msg=f"CLI command 'commit-maro' failed with output: {commit_result.output}")

        # 5. Verify the commit
        log_process = subprocess.run(["git", "log", "-1", "--pretty=%B"], capture_output=True, text=True, check=True)
        self.assertEqual(log_process.stdout.strip(), commit_message, "Commit message does not match.")

if __name__ == "__main__":
    # This allows running the test file directly, e.g. `python jetha_cli/tests/test_cli.py`
    # For this to work, PYTHONPATH needs to be set up so `from src import jetha_bhai` works.
    # Typically, if running from /app, then PYTHONPATH should include /app.
    # Or if running from /app/jetha_cli, then `src` is directly available.
    unittest.main()
