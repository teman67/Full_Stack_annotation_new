# JWT Temporary Fix
# This file needs to be imported at the start of your FastAPI app

import os
import sys

# Set the correct SECRET_KEY environment variable
os.environ["SECRET_KEY"] = "bvKmIR-A0kWrSvZaqaZ9c5XDUy8AkXsG5x1GG2vYJ7I"

# Print diagnostic info
print(f"JWT Fix applied with SECRET_KEY={os.environ['SECRET_KEY']}")
