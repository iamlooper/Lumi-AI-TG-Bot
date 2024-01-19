#!/bin/bash

# Start venv.
if [ -d "$PWD/venv" ]; then
    source "$PWD/venv/bin/activate"
fi

# Start a dummy web server.
if [ ! -z "$PORT" ]; then
    py_code="from aiohttp import web
app = web.Application()
app.router.add_get('/', lambda _: web.Response(text='Web server is running...'))
web.run_app(app, host='0.0.0.0', port=$PORT)"
    python -c "$py_code" &
fi

# Start the app.
python -m app