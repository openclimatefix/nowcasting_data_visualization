"""
https://auth0.com/docs/quickstart/webapp/python/01-login
and
https://hackersandslackers.com/plotly-dash-with-flask/
"""
import dash_auth

VALID_USERNAME_PASSWORD_PAIRS = {
    'hello': 'world'
}


def make_auth(app):
    dash_auth.BasicAuth(
        app,
        VALID_USERNAME_PASSWORD_PAIRS
    )

    # TODO use a proper log in using Auth0
