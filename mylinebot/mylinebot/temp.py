from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

with open(Path(BASE_DIR.parent, 'KEYS'), 'r') as f:
    LINE_CHANNEL_SECRET = f.readline().strip()
    LINE_CHANNEL_ACCESS_TOKEN = f.readline().strip()

print(LINE_CHANNEL_ACCESS_TOKEN)
print(LINE_CHANNEL_SECRET)