"""Create a private snippet; never edit an existing Hermes installation."""
import argparse
import os
from pathlib import Path
import secrets


def create_config(path, port=8642):
    if not 1 <= port <= 65535:
        raise ValueError('Port must be between 1 and 65535')
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = ('API_SERVER_ENABLED=true\nAPI_SERVER_HOST=127.0.0.1\n'
               f'API_SERVER_PORT={port}\nAPI_SERVER_KEY={secrets.token_hex(32)}\n')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as output:
        output.write(content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='.local/hermes-api.env')
    parser.add_argument('--port', type=int, default=8642)
    args = parser.parse_args()
    try:
        create_config(args.output, args.port)
    except FileExistsError:
        parser.exit(1, 'Refusing to overwrite an existing file.\n')
    except (OSError, ValueError):
        parser.exit(1, 'Cannot create config: check path permissions and port.\n')
    print('Created private snippet. Merge into your active profile after backup.')
    print('Nothing was installed or restarted. Never commit this file.')


if __name__ == '__main__':
    main()
