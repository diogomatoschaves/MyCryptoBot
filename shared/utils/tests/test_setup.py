import os
from collections import defaultdict

from IPython.utils.py3compat import execfile


def get_fixtures(current_path, fixtures=None, keys=None):

    if not keys:
        keys = ["in", "out"]

    if not fixtures:
        fixtures = defaultdict(lambda: {key: {} for key in keys})

    for key in keys:

        files_path = os.path.join(current_path, key)

        for filename in os.listdir(files_path):

            if filename == "__pycache__":
                continue

            name = ".".join(filename.split(".")[:-1])

            variables = {}

            execfile(os.path.join(files_path, filename), variables)
            fixtures[name][key] = variables

    return fixtures


if __name__ == "__main__":

    fixtures = get_fixtures("/data/tests/sources/binance/extract")

    print(fixtures)
