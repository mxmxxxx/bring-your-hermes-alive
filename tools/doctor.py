"""Check a Hermes OpenAI-compatible endpoint without logging secrets or replies."""
import argparse
import getpass
import ipaddress
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


class CheckError(Exception):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise CheckError('Redirect refused; use the final trusted API URL.')


def normalize_url(value):
    try:
        parts = urlsplit(value.strip())
        port = parts.port
        host = parts.hostname
    except ValueError:
        raise CheckError('Invalid API URL.') from None
    if (parts.scheme not in ('http', 'https') or not host or
            parts.username is not None or parts.password is not None or
            parts.query or parts.fragment or any(c.isspace() for c in value)):
        raise CheckError('Use an HTTP(S) URL without credentials, query or fragment.')
    try:
        local = ipaddress.ip_address(host).is_loopback
    except ValueError:
        local = host == 'localhost'
    if parts.scheme == 'http' and not local:
        raise CheckError('Remote endpoints must use HTTPS; HTTP is loopback-only.')
    path = parts.path.rstrip('/')
    if not path:
        path = '/v1'
    if not path.endswith('/v1'):
        raise CheckError('Base URL must end in /v1, not /chat/completions.')
    return urlunsplit((parts.scheme, parts.netloc, path, '', ''))


def stream_text(lines):
    """Parse SSE by event boundaries; skip Hermes progress, reject truncation."""
    event, data = '', []
    ended = False
    for raw in lines:
        line = raw.decode('utf-8').rstrip('\r\n') if isinstance(raw, bytes) else raw.rstrip('\r\n')
        if line:
            if line.startswith('event:'):
                event = line[6:].strip()
            elif line.startswith('data:'):
                data.append(line[5:].lstrip())
            continue
        if not data:
            event = ''
            continue
        payload = '\n'.join(data)
        data, previous_event = [], event
        event = ''
        if previous_event == 'hermes.tool.progress':
            continue
        if payload == '[DONE]':
            ended = True
            break
        try:
            chunk = json.loads(payload)
        except json.JSONDecodeError:
            raise CheckError('Malformed SSE JSON.') from None
        if not isinstance(chunk, dict):
            raise CheckError('Malformed SSE event.')
        if 'error' in chunk or previous_event == 'error':
            raise CheckError('Server returned a streaming error.')
        if chunk.get('type') == 'hermes.tool.progress':
            continue
        choices = chunk.get('choices', [])
        if not isinstance(choices, list):
            raise CheckError('Malformed streaming choices.')
        for choice in choices:
            if not isinstance(choice, dict) or not isinstance(choice.get('delta', {}), dict):
                raise CheckError('Malformed streaming delta.')
            content = choice.get('delta', {}).get('content')
            if isinstance(content, str):
                yield content
    if not ended:
        raise CheckError('Stream ended without [DONE]; may be truncated.')


def request(opener, base, endpoint, key, timeout, payload=None):
    headers = {'Authorization': 'Bearer ' + key, 'Accept': 'application/json'}
    body = None
    if payload is not None:
        body = json.dumps(payload).encode('utf-8')
        headers['Content-Type'] = 'application/json'
        if payload.get('stream'):
            headers['Accept'] = 'text/event-stream'
    return opener.open(Request(base + endpoint, data=body, headers=headers), timeout=timeout)


def check(base, key, model=None, chat=False, stream=False, timeout=120):
    base = normalize_url(base)
    if not key or any(c in key for c in '\r\n'):
        raise CheckError('A nonempty single-line API key is required.')
    opener = build_opener(NoRedirect())
    with request(opener, base, '/models', key, timeout) as response:
        result = json.load(response)
    if not isinstance(result, dict) or not isinstance(result.get('data'), list):
        raise CheckError('Model list is not OpenAI-compatible.')
    ids = [item['id'] for item in result['data']
           if isinstance(item, dict) and isinstance(item.get('id'), str)]
    if not ids:
        raise CheckError('No model IDs advertised.')
    print(f'PASS: model discovery ({len(ids)} model(s)).')
    if model is not None and model not in ids:
        raise CheckError('Requested model not advertised by this endpoint.')
    if not (chat or stream):
        return
    if model is None:
        if len(ids) != 1:
            raise CheckError('Multiple models advertised; specify --model.')
        model = ids[0]
    messages = [{'role': 'user', 'content': 'Reply with a short hello. Do not use tools.'}]
    for streaming, enabled in ((False, chat), (True, stream)):
        if not enabled:
            continue
        payload = {'model': model, 'messages': messages, 'stream': streaming}
        with request(opener, base, '/chat/completions', key, timeout, payload) as response:
            if streaming:
                if 'text/event-stream' not in response.headers.get('Content-Type', ''):
                    raise CheckError('Expected text/event-stream.')
                count = sum(len(part) for part in stream_text(response))
            else:
                result = json.load(response)
                try:
                    content = result['choices'][0]['message']['content']
                except (KeyError, IndexError, TypeError):
                    raise CheckError('Missing assistant content.') from None
                count = len(content) if isinstance(content, str) else 0
        if not count:
            raise CheckError('No assistant text received.')
        print('PASS: ' + ('streaming' if streaming else 'ordinary') + ' reply (body hidden).')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', required=True)
    parser.add_argument('--model')
    parser.add_argument('--chat', action='store_true', help='Send a billable inference request')
    parser.add_argument('--stream', action='store_true', help='Send a separate streaming request')
    parser.add_argument('--timeout', type=float, default=120, help='Socket operation timeout in seconds')
    args = parser.parse_args()
    try:
        normalize_url(args.base_url)  # Validate before asking for credentials.
        if args.timeout <= 0:
            raise CheckError('Timeout must be positive.')
        key = os.environ.get('HERMES_API_KEY')
        if not key:
            if not sys.stdin.isatty():
                raise CheckError('Noninteractive run requires HERMES_API_KEY.')
            key = getpass.getpass('Hermes API key (hidden): ')
        check(args.base_url, key, args.model, args.chat, args.stream, args.timeout)
    except HTTPError as error:
        print(f'FAIL: HTTP {error.code}; check authentication, route and server status.', file=sys.stderr)
        return 1
    except CheckError as error:
        print(f'FAIL: {error}', file=sys.stderr)
        return 1
    except (URLError, OSError, ValueError):
        print('FAIL: network/TLS/timeout or invalid response; check server locally.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
