import os
import shutil
import subprocess
import unittest
from click.testing import CliRunner

# Import for running tests from the project root directory (/app)
from jetha_cli.src import jetha_bhai

class TestGitCommands(unittest.TestCase):
    def setUp(self):
        """Set up a temporary directory for testing."""
        # self.original_cwd will be the project root (e.g., /app) when tests are run from there.
        self.original_cwd = os.getcwd()
        self.test_dir_name = "temp_test_dir_for_cli_tests" # Unique name
        
        # Create the test directory relative to the original_cwd
        os.makedirs(self.test_dir_name, exist_ok=True)
        
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
        # We are now in self.test_dir_name
        result = runner.invoke(jetha_bhai, ["git-chalu-karo"])
        
        if result.exception:
            print(f"Exception in git-chalu-karo: {result.exception}")
            import traceback
            traceback.print_exception(type(result.exception), result.exception, result.exc_info[2])
            self.fail(f"CLI command 'git-chalu-karo' raised an unexpected exception: {result.exception}")
        
        # Check exit code first, then output, then side effects
        # Check if the CLI command itself failed due to error handling (exit(1))
        if result.exit_code != 0 and "Error encountered" in result.output:
             pass # This is an expected failure if git init fails (e.g. already initialized, caught by CLI)
        else: # If no "Error encountered" message, it should be a clean success.
            self.assertEqual(result.exit_code, 0, msg=f"CLI command 'git-chalu-karo' failed unexpectedly. Output: {result.output}")
        
        self.assertTrue(os.path.isdir(".git"), "'.git' directory was not created in the test directory.")

    def test_commit_maro_success(self):
        runner = CliRunner()
        # We are in self.test_dir_name

        # 1. Initialize a Git repository using the CLI command
        init_result = runner.invoke(jetha_bhai, ["git-chalu-karo"])
        if init_result.exception:
            print(f"Exception in prerequisite 'git-chalu-karo': {init_result.exception}")
            import traceback
            traceback.print_exception(type(init_result.exception), init_result.exception, init_result.exc_info[2])
            self.fail(f"Prerequisite 'git-chalu-karo' raised an unexpected exception: {init_result.exception}")
        
        # Allow for the case where .git might already exist if tests are run multiple times and cleanup failed once.
        # The command should still pass if it's already a git repo.
        # We also need to check init_result.exit_code if there was no exception, 
        # as git-chalu-karo itself might return non-zero for a known error.
        if init_result.exit_code != 0 and "Error encountered" in init_result.output:
             pass # This is an expected failure if git init fails (e.g. already initialized, caught by CLI)
        elif init_result.exit_code !=0: # If no "Error encountered" message, but still non-zero code
            self.assertEqual(init_result.exit_code, 0, msg=f"Prerequisite 'git-chalu-karo' failed unexpectedly. Output: {init_result.output}")

        self.assertTrue(os.path.isdir(".git"), "'.git' directory was not created by git-chalu-karo or did not exist.")

        # 2. Create a dummy file
        dummy_file = "test_file.txt"
        with open(dummy_file, "w") as f:
            f.write("This is a test file for commit-maro.")
        
        # 3. Stage the file using git add & configure git user
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True, capture_output=True)
        stage_process = subprocess.run(["git", "add", dummy_file], capture_output=True, text=True)
        self.assertEqual(stage_process.returncode, 0, f"git add failed: {stage_process.stderr}")

        # 4. Run the commit-maro command
        commit_message = "Test commit via commit-maro"
        commit_result = runner.invoke(jetha_bhai, ["commit-maro", commit_message])
        
        if commit_result.exception:
            print(f"Exception in commit-maro: {commit_result.exception}")
            import traceback
            traceback.print_exception(type(commit_result.exception), commit_result.exception, commit_result.exc_info[2])
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
        # We are in self.test_dir_name

        # 1. Initialize a Git repository
        init_result = runner.invoke(jetha_bhai, ["git-chalu-karo"])
        if init_result.exception:
            print(f"Exception in prerequisite 'git-chalu-karo' for no_staging test: {init_result.exception}")
            import traceback
            traceback.print_exception(type(init_result.exception), init_result.exception, init_result.exc_info[2])
            self.fail(f"Prerequisite 'git-chalu-karo' for no_staging test raised an unexpected exception: {init_result.exception}")
        self.assertTrue(os.path.isdir(".git"), "'.git' directory was not created by git-chalu-karo for no_staging test.")
        
        # Configure git user
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True)

        # 2. Attempt to commit without staging any files
        commit_message = "Attempting commit with no staged files"
        commit_result = runner.invoke(jetha_bhai, ["commit-maro", commit_message])

        if commit_result.exception:
            print(f"Exception in commit-maro (no staging): {commit_result.exception}")
            import traceback
            traceback.print_exception(type(commit_result.exception), commit_result.exception, commit_result.exc_info[2])
            self.fail(f"CLI command 'commit-maro' (no staging) raised an unexpected exception: {commit_result.exception}")
        
        # Expecting a non-zero exit code because git commit should fail
        self.assertNotEqual(commit_result.exit_code, 0, "CLI command 'commit-maro' should have failed for no staged files, but it succeeded.")
        self.assertTrue("Error encountered" in commit_result.output, "Error message not found in output when commit failed as expected.")
        # Check that no commit was made
        log_process = subprocess.run(["git", "log", "-1", "--pretty=%B"], capture_output=True, text=True)
        self.assertNotEqual(log_process.stdout.strip(), commit_message, "A commit was made even though it should have failed.")


if __name__ == "__main__":
    unittest.main()
