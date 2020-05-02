import os

from dotenv import load_dotenv
from pathlib import Path


def setEnvPath():
    env_path = Path('.') / 'config.env'
    load_dotenv(dotenv_path=env_path)


def getEnvValue(key):
    setEnvPath()
    return os.getenv(key)


setEnvPath()
print(getEnvValue("TEST"))

