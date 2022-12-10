import os
import sys

from app import create_app

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)


application = create_app()


if __name__ == "__main__":
    application.run()
