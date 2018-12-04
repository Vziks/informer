from .viber_handler import *
from .gitlab_handler import *
from .bitbucket_handler import *
from .codeship_handler import *
from .telegram_handler import *
from .sender_handler import *


@app.after_request
def after_request(response):
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src http:; report-uri"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "no-referrer"

    return response
