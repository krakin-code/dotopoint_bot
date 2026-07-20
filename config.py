import os
from dotenv import load_dotenv

# Локально подтягивает переменные из .env.
# На Railway .env-файла нет — там переменные уже заданы в Variables,
# и load_dotenv() их не перезапишет.
load_dotenv()

TOKEN = os.environ["BOT_TOKEN"]