import os
import random
import shutil
import subprocess

import click
from rich import print


def print_rainbow(line):
    colors = ["orange", "yellow", "green", "blue", "indigo", "violet"]
    color = random.choice(colors)
    print("")
    print(f"[{color}]{line}[/{color}]")


def _handle_git_command_error(ctx, e, default_error_message):
    if isinstance(e, FileNotFoundError):
        print_rainbow("Git command not found. Make sure Git is installed and in your PATH.")
        ctx.exit(1)
    elif isinstance(e, subprocess.CalledProcessError):
        error_output = e.stderr.strip() if e.stderr else default_error_message
        print_rainbow(f"Error encountered: {error_output}")
        ctx.exit(1)
    else:
        # Fallback for any other unexpected exceptions
        print_rainbow(f"An unexpected error occurred: {str(e)}")
        ctx.exit(1)


@click.group("jetha-bhai")
def jetha_bhai():
    pass


@jetha_bhai.command("babita-ji-kaha", help="Display the current working directory")
def pwd():
    print_rainbow(f"Babita ji, yeh current working directory mai hai: {os.getcwd()}")


@jetha_bhai.command(
    "list-kardo", help="List files and directories in the current folder"
)
def ls():
    print_rainbow("Bhai, yeh le list, jalebi bhej dena par yaad se")
    print_rainbow("\n".join(os.listdir(os.getcwd())))


@jetha_bhai.command("ye-banado", help="Create a new directory")
@click.argument("folder")
def mkdir(folder):
    print_rainbow("Mota bhai kaam kar diya hai, naya folder ban gaya")
    os.makedirs(folder, exist_ok=True)


@jetha_bhai.command("move-on-karado", help="Move a folder to another location")
@click.argument("src_folder")
@click.argument("destination_folder")
def mv(src_folder, destination_folder):
    print_rainbow("Yei vayadi move on nahi move hota hai voh, maine kar diya kam kher")
    shutil.move(src_folder, destination_folder)


@jetha_bhai.command("udado-isko", help="Remove a folder")
@click.argument("folder")
def rm(folder):
    print_rainbow("Sunder ko to uda nahi sakta, lekin folder ko uda diya maine")
    shutil.rmtree(folder)


@jetha_bhai.command("copy-maro", help="Copy a folder to another location")
@click.argument("src_folder")
@click.argument("destination_folder")
def cp(src_folder, destination_folder):
    print_rainbow(
        "Tapu ki sangat ka asar laga hai tume sayad, copying kar raha hoon mai chalo"
    )
    shutil.copytree(src_folder, destination_folder)


# @jetha_bhai.command("chalo")
# @click.argument("path")
# def cd(path):
#     print(f"lo bhai aa gaye hum ye path pai {os.path.abspath(path)}")


# @jetha_bhai.command("sunder-aaya")
# def cd_dot_dot():
#     print(f"lo bhai aa gaye hum ye path pai {os.path.abspath('/../')}")


@jetha_bhai.command("git-chalu-karo", help="Initialize a new Git repository")
@click.pass_context
def git_chalu_karo(ctx):
    try:
        subprocess.run(["git", "init"], capture_output=True, text=True, check=True)
        print_rainbow("Git chalu kar diya hai, ab Daya ko mat bolna!")
    except FileNotFoundError as e:
        _handle_git_command_error(ctx, e, "")
    except subprocess.CalledProcessError as e:
        _handle_git_command_error(ctx, e, "An unknown error occurred while initializing the Git repository.")


@jetha_bhai.command("commit-maro", help="Commit changes to the Git repository")
@click.pass_context
@click.argument("message")
def commit_maro(ctx, message):
    try:
        subprocess.run(["git", "commit", "-m", message], capture_output=True, text=True, check=True)
        print_rainbow("Commit kar diya hai, Champak chacha ko mat batana!")
    except FileNotFoundError as e:
        _handle_git_command_error(ctx, e, "")
    except subprocess.CalledProcessError as e:
        _handle_git_command_error(ctx, e, "An unknown error occurred during the commit.")
