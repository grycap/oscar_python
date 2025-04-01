"""
Class to manage OIDC JWT tokens
"""
import json
import base64
import re
import time
import requests


class OIDC(object):

    @staticmethod
    def _b64d(b):
        """Decode some base64-encoded bytes.

        Raises Exception if the string contains invalid characters or padding.

        :param b: bytes
        """

        cb = b.rstrip(b"=")  # shouldn't but there you are

        # Python's base64 functions ignore invalid characters, so we need to
        # check for them explicitly.
        b64_re = re.compile(b"^[A-Za-z0-9_-]*$")
        if not b64_re.match(cb):
            raise Exception(cb, "base64-encoded data contains illegal characters")

        if cb == b:
            b = OIDC._add_padding(b)

        return base64.urlsafe_b64decode(b)

    @staticmethod
    def _add_padding(b):
        # add padding chars
        m = len(b) % 4
        if m == 1:
            # NOTE: for some reason b64decode raises *TypeError* if the
            # padding is incorrect.
            raise Exception(b, "incorrect padding")
        elif m == 2:
            b += b"=="
        elif m == 3:
            b += b"="
        return b

    @staticmethod
    def get_info(token):
        """
        Unpacks a JWT into its parts and base64 decodes the parts
        individually, returning the part 1 json decoded, where the
        token info is stored.

        :param token: The JWT token
        """
        part = tuple(token.encode("utf-8").split(b"."))
        part = [OIDC._b64d(p) for p in part]
        return json.loads(part[1].decode("utf-8"))

    @staticmethod
    def is_access_token_expired(token):
        """
        Check if the current access token is expired
        """
        try:
            decoded_token = OIDC.get_info(token)
            now = int(time.time())
            expires = int(decoded_token['exp'])
            validity = expires - now
            if validity < 0:
                return True
            else:
                return False
        except Exception:
            return True

    @staticmethod
    def refresh_access_token(refresh_token, scopes, token_endpoint):
        """
        Refresh the access token using the refresh token
        """
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': 'token-portal',
            'scope': ' '.join(scopes)
        }

        response = requests.post(token_endpoint, data=data)

        if response.status_code == 200:
            return response.json()['access_token']
        else:
            return None
