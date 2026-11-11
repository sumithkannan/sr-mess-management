import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# app.main installs changed requirements before importing third-party
# packages, so this entry point stays a plain import.
from app.main import app

application = app
