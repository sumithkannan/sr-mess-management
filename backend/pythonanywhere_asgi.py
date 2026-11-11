import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Install changed requirements before importing the application, so newly
# added packages are available on the first start after a deploy.
from deploy_dependencies import ensure_dependencies

ensure_dependencies()

from app.main import app

application = app
