import os
import shutil
import subprocess
import unittest
from click.testing import CliRunner

# Assuming your CLI's main group 'jetha_bhai' and commands are importable
# If __init__.py is structured to make 'jetha_bhai' directly importable:
from jetha_cli.src import jetha_bhai

# If not, you might need to adjust the import based on your project structure
# For example, if commands are defined in __init__.py and jetha_bhai is the group:
# from jetha_cli.src import git_chalu_karo, commit_maro # and other commands if needed

class TestGitCommands(unittest.TestCase):
    def setUp(self):
        """Set up a temporary directory for testing."""
        self.test_dir = "temp_test_dir_jetha_cli"
        os.makedirs(self.test_dir, exist_ok=True)
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """Clean up the temporary directory."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True) # ignore_errors is important for robustness

    def test_git_chalu_karo(self):
        runner = CliRunner()
        result = runner.invoke(jetha_bhai, ["git-chalu-karo"])
        
        print(f"Output of git-chalu-karo: {result.output}")
        if result.exception:
            print(f"Exception in git-chalu-karo: {result.exception}")
            import traceback
            traceback.print_exception(type(result.exception), result.exception, result.exc_info[2])

        self.assertEqual(result.exit_code, 0, msg=f"CLI command failed with output: {result.output}")
        self.assertTrue(os.path.isdir(".git"), "'.git' directory was not created.")

    def test_commit_maro(self):
        runner = CliRunner()
        
        # 1. Initialize a Git repository
        init_result = runner.invoke(jetha_bhai, ["git-chalu-karo"])
        self.assertEqual(init_result.exit_code, 0, f"git-chalu-karo failed: {init_result.output}")
        self.assertTrue(os.path.isdir(".git"), "'.git' directory was not created by git-chalu-karo.")

        # 2. Create a dummy file
        dummy_file = "test_file.txt"
        with open(dummy_file, "w") as f:
            f.write("This is a test file for commit-maro.")
        
        # 3. Stage the file using git add
        stage_process = subprocess.run(["git", "add", dummy_file], capture_output=True, text=True)
        self.assertEqual(stage_process.returncode, 0, f"git add failed: {stage_process.stderr}")

        # 4. Run the commit-maro command
        commit_message = "Test commit via commit-maro"
        commit_result = runner.invoke(jetha_bhai, ["commit-maro", commit_message])
        
        print(f"Output of commit-maro: {commit_result.output}")
        if commit_result.exception:
            print(f"Exception in commit-maro: {commit_result.exception}")
            import traceback
            traceback.print_exception(type(commit_result.exception), commit_result.exception, commit_result.exc_info[2])

        self.assertEqual(commit_result.exit_code, 0, msg=f"CLI command failed with output: {commit_result.output}")

        # 5. Verify the commit
        log_process = subprocess.run(["git", "log", "-1", "--pretty=%B"], capture_output=True, text=True, check=True)
        # The output of git log includes a trailing newline, so strip it.
        self.assertEqual(log_process.stdout.strip(), commit_message, "Commit message does not match.")

if __name__ == "__main__":
    unittest.main()
