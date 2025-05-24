import os
import shutil
import subprocess
import tempfile # Added import
import unittest
import click # Added import
from unittest.mock import patch # Added import
from click.testing import CliRunner

# Import for running tests from the project root directory (/app)
from jetha_cli.src import jetha_bhai

class TestGitCommands(unittest.TestCase):
    def setUp(self):
        """Set up a temporary directory for testing."""
        # self.original_cwd will be the project root (e.g., /app) when tests are run from there.
        self.original_cwd = os.getcwd()
        self.temp_dir = tempfile.TemporaryDirectory() # Create TemporaryDirectory
        
        # Change CWD to the newly created temporary directory
        os.chdir(self.temp_dir.name) # Use temp_dir.name

    def tearDown(self):
        """Clean up the temporary directory."""
        # Change back to the original CWD *before* trying to remove the test_dir
        os.chdir(self.original_cwd)
        
        # Clean up the temporary directory
        self.temp_dir.cleanup()

    def test_git_chalu_karo(self):
        runner = CliRunner()
        # We are now in self.temp_dir.name
        result = runner.invoke(jetha_bhai, ["git-chalu-karo"])
        
        if result.exception:
            # Removed print and traceback statements
            self.fail(f"CLI command 'git-chalu-karo' raised an unexpected exception: {result.exception}")
        
        self.assertTrue(
            (result.exit_code == 0) or ("Error encountered" in result.output),
            msg=f"CLI command 'git-chalu-karo' failed unexpectedly. Exit code: {result.exit_code}, Output: {result.output}"
        )
        
        self.assertTrue(os.path.isdir(".git"), "'.git' directory was not created in the test directory.")

    def test_commit_maro_success(self):
        runner = CliRunner()
        # We are in self.temp_dir.name

        # 1. Initialize a Git repository using the CLI command
        init_result = runner.invoke(jetha_bhai, ["git-chalu-karo"])
        if init_result.exception:
            # Removed print and traceback statements
            self.fail(f"Prerequisite 'git-chalu-karo' raised an unexpected exception: {init_result.exception}")
        
        # Allow for the case where .git might already exist if tests are run multiple times and cleanup failed once.
        # The command should still pass if it's already a git repo.
        self.assertTrue(
            (init_result.exit_code == 0) or ("Error encountered" in init_result.output),
            msg=f"Prerequisite 'git-chalu-karo' failed unexpectedly. Exit code: {init_result.exit_code}, Output: {init_result.output}"
        )

        self.assertTrue(os.path.isdir(".git"), "'.git' directory was not created by git-chalu-karo or did not exist.")

        # 2. Create a dummy file
        dummy_file = "test_file.txt"
        with open(dummy_file, "w") as f:
            f.write("This is a test file for commit-maro.")
        
        # 3. Stage the file using git add & configure git user
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True, capture_output=True, text=True)
        stage_process = subprocess.run(["git", "add", dummy_file], capture_output=True, text=True)
        self.assertEqual(stage_process.returncode, 0, f"git add failed: {stage_process.stderr}")

        # 4. Run the commit-maro command
        commit_message = "Test commit via commit-maro"
        commit_result = runner.invoke(jetha_bhai, ["commit-maro", commit_message])
        
        if commit_result.exception:
            # Removed print and traceback statements
            self.fail(f"CLI command 'commit-maro' raised an unexpected exception: {commit_result.exception}")
        
        # Check if the CLI command itself failed due to error handling (exit(1))
        # e.g. if commit is run without staging, git commit returns non-zero.
        if commit_result.exit_code != 0 and "Error encountered" in commit_result.output:
            # This might be an expected failure path if git commit command fails (e.g. nothing to commit)
            # For a success test, this path should not be taken.
            self.fail(f"commit-maro indicated an error for a supposedly successful commit: {commit_result.output}")
        else:
             self.assertEqual(commit_result.exit_code, 0, msg=f"CLI command 'commit-maro' failed unexpectedly. Output: {commit_result.output}")


        # 5. Verify the commit
        log_process = subprocess.run(["git", "log", "-1", "--pretty=%B"], capture_output=True, text=True, check=True)
        self.assertEqual(log_process.stdout.strip(), commit_message, "Commit message does not match.")

    def test_commit_maro_no_staging(self):
        runner = CliRunner()
        # We are in self.temp_dir.name

        # 1. Initialize a Git repository
        init_result = runner.invoke(jetha_bhai, ["git-chalu-karo"])
        if init_result.exception:
            # Removed print and traceback statements
            self.fail(f"Prerequisite 'git-chalu-karo' for no_staging test raised an unexpected exception: {init_result.exception}")
        self.assertTrue(os.path.isdir(".git"), "'.git' directory was not created by git-chalu-karo for no_staging test.")
        
        # Configure git user
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True, capture_output=True, text=True)

        # 2. Attempt to commit without staging any files
        commit_message = "Attempting commit with no staged files"
        commit_result = runner.invoke(jetha_bhai, ["commit-maro", commit_message])

        if commit_result.exception:
            # We expect _handle_git_command_error to call ctx.exit(1).
            # CliRunner catches SystemExit (and click.exceptions.Exit is a SystemExit).
            # The actual exception instance is in result.exception.
            # The exit code of the exception is in result.exception.code.
            # result.exit_code is also set to this code.
            if not isinstance(commit_result.exception, (SystemExit, click.exceptions.Exit)):
                # This was an actual Python exception other than SystemExit/Exit.
                # Removed print and traceback statements
                self.fail(f"CLI command 'commit-maro' (no staging) raised an unexpected Python exception: {commit_result.exception}")
            
            # Check if the exit code from SystemExit/Exit was 0, which is not expected here.
            # Note: isinstance check above ensures commit_result.exception has 'code' attribute.
            if hasattr(commit_result.exception, 'code') and commit_result.exception.code == 0:
                self.fail(f"CLI command 'commit-maro' (no staging) exited with code 0 but a failure was expected.")
            # If it's a SystemExit/Exit with a non-zero code, that's expected, so we don't fail here.
            # The assertions below on result.exit_code and output will verify the details.
        
        # Expecting a non-zero exit code because git commit should fail
        self.assertNotEqual(commit_result.exit_code, 0, "CLI command 'commit-maro' should have failed for no staged files, but it succeeded.")
        self.assertTrue("Error encountered" in commit_result.output, "Error message not found in output when commit failed as expected.")
        # Check that no commit was made
        log_process = subprocess.run(["git", "log", "-1", "--pretty=%B"], capture_output=True, text=True)
        self.assertNotEqual(log_process.stdout.strip(), commit_message, "A commit was made even though it should have failed.")

    @patch('jetha_cli.src.subprocess.run') # Patching subprocess.run in the context of jetha_cli.src module
    def test_git_commands_file_not_found(self, mock_subprocess_run):
        runner = CliRunner()
        mock_subprocess_run.side_effect = FileNotFoundError("Mocked FileNotFoundError: git command not found")

        # Test 'git-chalu-karo'
        result_init = runner.invoke(jetha_bhai, ['git-chalu-karo'])
        self.assertNotEqual(result_init.exit_code, 0, "CLI should exit with non-zero code on FileNotFoundError for git-chalu-karo.")
        self.assertIn("Git command not found. Make sure Git is installed and in your PATH.", result_init.output)

        # Reset side_effect for the next call if necessary, or ensure it's general enough
        # For FileNotFoundError, it's general.

        # Test 'commit-maro'
        result_commit = runner.invoke(jetha_bhai, ['commit-maro', 'test message for file not found'])
        self.assertNotEqual(result_commit.exit_code, 0, "CLI should exit with non-zero code on FileNotFoundError for commit-maro.")
        self.assertIn("Git command not found. Make sure Git is installed and in your PATH.", result_commit.output)


if __name__ == "__main__":
    unittest.main()
