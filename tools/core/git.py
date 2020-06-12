from __future__ import annotations

import logging
import os
import re
import sys
from dataclasses import dataclass
from subprocess import check_output, PIPE, CalledProcessError
from typing import TYPE_CHECKING, List, Dict

from .image import Image

if TYPE_CHECKING:
    from .toolkit import Context


@dataclass
class GitInfo:
    branch: str
    revision: str
    master: str
    history: List[str]


def get_master_commit_hash():
    try:
        return check_output("git rev-parse master", shell=True, stderr=PIPE).decode().splitlines()[0]
    except CalledProcessError:
        # <hash> refs/heads/master
        return check_output("git ls-remote origin master", shell=True, stderr=PIPE).decode().split()[0]


def get_branch_history(master):
    cmd = "git log --oneline --pretty=format:%h --abbrev=-1 {}..".format(master[:7])
    return check_output(cmd, shell=True, stderr=PIPE).decode().splitlines()


def get_commit_message(commit):
    if commit == "HEAD":
        return ""
    cmd = "git show -s --format=%B {}".format(commit)
    return check_output(cmd, shell=True, stderr=PIPE).decode().splitlines()[0]


class GitTemplate:
    def __init__(self, project_dir):
        self._logger = logging.getLogger("core.GitTemplate")
        self.project_dir = project_dir
        self.commit_before_travis = "0aa9c74f46012d212134ec6b7d58732b84f14ee0"
        self.git_info = self._create_git_info()

    def _create_git_info(self):
        if not os.path.exists(".git"):
            raise RuntimeError("Not a git repository")

        b = os.popen("git rev-parse --abbrev-ref HEAD").read().strip()
        if b == "HEAD":
            b = os.environ["TRAVIS_BRANCH"]
        if b == "local":
            print("ERROR: Git branch name (local) is reserved", file=sys.stderr)
            exit(1)
        if "__" in b:
            print("ERROR: Git branch name (%s) contains \"__\"" % b, file=sys.stderr)
            exit(1)
        r = os.popen("git rev-parse HEAD").read().strip()
        if os.system("git diff --quiet") != 0:
            r = r + "-dirty"
        master = get_master_commit_hash()
        branch = b
        if branch == "master":
            history = get_branch_history(self.commit_before_travis)
        else:
            history = get_branch_history(master)

        output = check_output("git diff --name-only", shell=True)
        output = output.decode().strip()
        if len(output) > 0:
            history.insert(0, "HEAD")

        return GitInfo(b, r, master, history)

    def get_modified_images(self, context: Context) -> List[Image]:
        branch = context.branch
        if branch == "master":
            base = self._get_last_successful_travis_build("master")
        else:
            base = self.git_info.master

        modified_folders = self._get_modified_since_commit(base)

        self._logger.debug("modified_folders=%r", modified_folders)

        result = []
        for folder in modified_folders:
            name = folder.replace("images/", "")
            name = name.replace("/", ":")
            result.append(Image(context, name))
        return result

    def _get_last_successful_travis_build(self, branch):
        return self.commit_before_travis

    def _process_lines(self, lines: List[str]) -> List[str]:
        p = re.compile(r"^images/([^/]+)/([^/]+)/.+$")
        folders = set()
        for line in lines:
            if line.startswith("images/utils"):
                folders.add("utils")
            else:
                m = p.match(line)
                assert m
                folders.add("{}/{}".format(m.group(1), m.group(2)))

        folders = [folder for folder in folders if os.path.exists("images/" + folder)]

        return sorted(folders)

    def _get_modified_since_commit(self, commit: str) -> List[str]:
        prefix = "[_get_modified_since_commit] ({})".format(commit[:7])
        cmd = "git diff --name-only {} -- images".format(commit)
        self._logger.debug("%s cmd=%r", prefix, cmd)
        output = check_output(cmd, shell=True, stderr=PIPE)
        lines = output.decode().splitlines()
        self._logger.debug("%s lines=%r", prefix, lines)
        return self._process_lines(lines)

    def _get_modified_at_head(self):
        prefix = "[_get_modified_at_head]"
        cmd = "git diff --name-only -- images"
        self._logger.debug("%s cmd=%r", prefix, cmd)
        output = check_output(cmd, shell=True, stderr=PIPE)
        lines1 = output.decode().splitlines()
        self._logger.debug("%s lines1=%r", prefix, lines1)

        cmd = "git diff --name-only --cached -- images"
        self._logger.debug("%s cmd=%r", prefix, cmd)
        output = check_output(cmd, shell=True, stderr=PIPE)
        lines2 = output.decode().splitlines()
        self._logger.debug("%s lines2=%r", prefix, lines2)

        return self._process_lines(lines1 + lines2)

    def _get_modified_at_commit(self, commit: str) -> List[str]:
        prefix = "[_get_modified_at_commit] ({})".format(commit[:7])
        if commit == "HEAD":
            return self._get_modified_at_head()

        cmd = "git diff-tree --no-commit-id --name-only -r {} -- images".format(commit)
        self._logger.debug("%s cmd=%r", prefix, cmd)
        output = check_output(cmd, shell=True, stderr=PIPE)
        lines = output.decode().splitlines()
        self._logger.debug("%s lines=%r", prefix, lines)

        return self._process_lines(lines)

    @property
    def history(self) -> Dict[str, List[str]]:
        history = {commit: [] for commit in self.git_info.history}

        for commit in history:
            history[commit] = self._get_modified_at_commit(commit)

        return history
