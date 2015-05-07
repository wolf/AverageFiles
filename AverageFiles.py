from __future__ import division, print_function

import os
import sys
from collections import Counter
from contextlib import contextmanager
from subprocess import check_output


@contextmanager
def use_directory( path=None ):
    """A Context Manager to change to the given directory for the duration of the 'with' context.
    When path is None, don't change directories.
    """
    olddir = os.getcwd()
    try:
        if path:
            os.chdir(path)
        yield
    finally:
        os.chdir(olddir)


def all_non_merge_commits( git_dir=None, limit=None ):
    """a generator yielding 40-hex-digit commit hash strings"""
    args = ['git', 'rev-list', '--all', '--no-merges']
    if type(limit)==int:
        args += ['-{}'.format(limit)]
    with use_directory(git_dir):
        out = check_output(args)
    for h in out.decode('utf-8').splitlines():
        yield h


def count_files_committed( git_dir=None, depth=None ):
    """Return a collections.Counter dictionary where the keys are file-counts and the values
    are the number of commits that touched exactly that many files.
    """
    counter = Counter()
    with use_directory(git_dir):
        for h in all_non_merge_commits(limit=depth):
            out = check_output(['git', 'log', '--no-walk', '--format=', '--name-only', h])
            num_files_touched = len(out.splitlines())
            counter[num_files_touched] += 1
    return counter


def note_files_committed( git_dir=None, depth=None ):
    """Return a collections.Counter dictionary where the keys are paths and the values
    are the number of commits that touched exactly that many files.
    """
    counter = Counter()
    with use_directory(git_dir):
        for h in all_non_merge_commits(limit=depth):
            out = check_output(['git', 'log', '--no-walk', '--format=', '--name-only', h])
            for path in out.decode('utf-8').splitlines():
                counter[path] += 1
    return counter


def average_files_per_commit( counter ):
    """Given a dictionary as returned by count_files_committed(),
    return the average number of files touched per commit.
    """
    total_files = 0
    total_commits = 0

    for num_files, num_commits in counter.items():
        total_files += num_files * num_commits
        total_commits += num_commits

    return total_files / total_commits


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv)>1 else None
    counter = count_files_committed(path)
    print(counter)
    print("Average files / commit: {}".format(average_files_per_commit(counter)))
