import os

from dotenv import load_dotenv

load_dotenv()

TOS_ACCESS_KEY = os.getenv("TOS_ACCESS_KEY")
TOS_SECRET_ACCESS_KEY = os.getenv("TOS_SECRET_ACCESS_KEY")
TOS_ENDPOINT = os.getenv("TOS_ENDPOINT")
TOS_REGION = os.getenv("TOS_REGION")
