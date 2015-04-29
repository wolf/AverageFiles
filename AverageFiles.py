from __future__ import division, print_function

import os, sys
from subprocess import check_output
from collections import Counter
from contextlib import contextmanager


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


def all_non_merge_commits( git_dir=None ):
    """a generator yielding 40-hex-digit strings that are the hashes of commits from the object database"""

    with use_directory(git_dir):
        out = check_output(['git', 'log', '--all', '--no-merges', '--format=%H'])
    for hash in out.splitlines():
        yield hash.decode('utf-8')


def count_files_committed( git_dir=None ):
    """Return a collections.Counter dictionary where the keys are file-counts and the values are the number of commits that touched that exact number of files."""

    counter = Counter()
    with use_directory(git_dir):
        for h in all_non_merge_commits():
            out = check_output(['git', 'log', '-1', '--format=', '--name-only', h])
            count = len(out.splitlines())
            counter[count] += 1
    return counter


def average_files_per_commit( counter ):
    """Given a dictionary as returned by count_files_committed(), return the average number of files per commit."""

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
