import hashlib
import re
from os import path, devnull, getcwd, chdir, system
from subprocess import check_call, CalledProcessError, STDOUT

import yaml


def execute_command(cmd):
    """Execute a specified command"""
    try:
        fnull = open(devnull, "w")
        check_call(cmd, stdout=fnull, stderr=STDOUT)
    except CalledProcessError:
        return False
    return True


def load_yaml(file_path):
    data = None
    err = None
    try:
        with open(file_path, "r") as f:
            data = yaml.load(f)
    except Exception as e:
        err = e.message
    return data, err


def dump_yaml(file_path, data, override_old=True):
    err = None
    try:
        with open(file_path, "w+" if not override_old else "w") as f:
            yaml.dump(data, f)
    except Exception as e:
        err = e.message
    return err


def gen_hash(data):
    return str(hashlib.sha224(data).hexdigest())


def update_git_repo(git_url, git_branch, clone_location="."):
    ret = None

    if not path.exists(clone_location):
        clone_command = ["git", "clone", git_url, clone_location]
        if not execute_command(clone_command):
            return None

    get_back = getcwd()
    chdir(clone_location)

    # This command fetches all branches of added remotes of git repo.
    branches_cmd = r"""git branch -r | grep -v '\->' | while
    read remote; do git branch --track "${remote#origin/}"
    $remote &> /dev/null; done """

    system(branches_cmd)
    cmd = ["git", "fetch", "--all"]
    execute_command(cmd)

    # Pull for update
    cmd = ["git", "pull", "--all"]
    execute_command(cmd)

    # Checkout required branch
    cmd = ["git", "checkout", "origin/" + git_branch]

    if execute_command(cmd):
        ret = clone_location
    chdir(get_back)
    return ret


def print_out(data, verbose=True):
    if verbose:
        print(data)


def match_regex(pattern, match):
    return re.compile(pattern).match(match)


class IndexCIMessage(object):
    def __init__(self, data, title=None):
        self.title = title if title else "Untitled"
        self.success = True
        self.data = data
        self.errors = []
        self.warnings = []
