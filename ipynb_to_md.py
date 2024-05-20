# convert all .ipynb to .md in a directory tree

import os
import subprocess


if __name__ == "__main__":
    original_directory = os.getcwd()
    ipynb_files = []
    for root, dirs, files in os.walk(original_directory):
        for file in files:
            if file.endswith(".ipynb"):
                ipynb_files.append(os.path.join(root, file))
    for fpath in ipynb_files:
        dir = os.path.dirname(fpath)
        fname = os.path.basename(fpath)
        os.chdir(dir)
        subprocess.run(['jupyter', 'nbconvert', '--to', 'markdown', fname])
    os.chdir(original_directory)
