import os
import sys

from app import app

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

if __name__ == "__main__":
    app.run()
