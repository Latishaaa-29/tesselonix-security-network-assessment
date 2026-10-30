"""Generate local secrets without placing them in the repository or output."""
from pathlib import Path
import secrets

root = Path(__file__).resolve().parents[1]
target = root / '.env'
if target.exists():
    print('.env already exists; preserving it')
else:
    target.write_text('SECRET_KEY=' + secrets.token_hex(32) + '\nDB_PASSWORD=' +
                      secrets.token_hex(24) + '\n', encoding='utf-8')
    print('Created ignored .env with random local secrets')
