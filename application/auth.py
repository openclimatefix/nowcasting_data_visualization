"""
Links to help with auth

https://auth0.com/docs/quickstart/webapp/python/01-login
and
https://hackersandslackers.com/plotly-dash-with-flask/
"""
import os

import dash_auth
from log import logger

VALID_USERNAME_PASSWORD_PAIRS = {os.getenv("USERNAME", "hello"): os.getenv("WORD", "world")}


def make_auth(app):
    """Add auth to app"""

    logger.debug("Add auth to app")

    dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

    # TODO use a proper log in using Auth0
