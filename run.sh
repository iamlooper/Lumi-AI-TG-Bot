#!/bin/bash 

# Start a dummy web server.
py_code="from aiohttp import web
app = web.Application()
app.router.add_get('/', lambda _: web.Response(text='Web server is running...'))
web.run_app(app, host='0.0.0.0', port=$PORT)"
python -c "$py_code" &

# Start the app.
python -m app