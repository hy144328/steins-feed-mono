#!/usr/bin/env python3

import dotenv

dotenv.load_dotenv()

from .app import app

if __name__ == "__main__":
    app.start()
