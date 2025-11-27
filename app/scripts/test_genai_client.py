# app/scripts/test_genai_client.py
# -*- coding: utf-8 -*-
import os
import sys

CURRENT_DIR = os.path.dirname(__file__)          # .../app/scripts
APP_DIR = os.path.dirname(CURRENT_DIR)           # .../app
sys.path.insert(0, APP_DIR)

import system
from modules.genai import get_genai_client


if __name__ == "__main__":
    client = get_genai_client()
    print("Client:", client)
    cfg = getattr(system.settings, "genai", {})
    print("Project from settings:", cfg.get("project"))

