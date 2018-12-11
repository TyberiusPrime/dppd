import hashlib
import collections
import itertools
import time
import pathlib
import subprocess

cmd = ["python", "setup.py", "docs"]
hashes = collections.defaultdict(lambda: "")


def get_hash(fn, second=False):
    try:
        with open(fn, "rb") as d:
            return hashlib.md5(d.read()).hexdigest()
    except FileNotFoundError:
        if not second:
            time.sleep(1)
            return get_hash(fn, True)
        else:
            raise


while True:
    rebuild = False
    files = ["docs/conf.py", "docs/_static/my-styles.css"]
    for fn in itertools.chain(
        files, pathlib.Path(".").glob("**/*.rst"), pathlib.Path("./src").glob("**/*.py")
    ):
        fn = str(fn)
        new_hash = get_hash(fn)
        if hashes[fn] != new_hash:
            rebuild = True
        hashes[fn] = new_hash
    if rebuild:
        subprocess.check_call(cmd)
