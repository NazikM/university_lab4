import os

from dotenv import load_dotenv

from fastapi.templating import Jinja2Templates

load_dotenv()
templates = Jinja2Templates(directory="app/templates")

# Secret key to sign and verify JWT tokens
try:
    SECRET_KEY_CLOUDFLARE = os.environ['SECRET_KEY_CLOUDFLARE']
    SECRET_KEY = os.environ['SECRET_KEY']
    ALGORITHM = os.environ['ALGORITHM']
except KeyError:
    print("Cannot find environment variable, exiting...")
    raise
