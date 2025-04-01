from unittest.mock import patch, MagicMock
from oscar_python._oidc import OIDC


def test_is_access_token_expired():
    token = ("eyJraWQiOiJyc2ExIiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiJkYzVkNWFiNy02ZGI5LTQwNzktOTg1Yy04MGFjMDUwMTcw"
             "NjYiLCJpc3MiOiJodHRwczpcL1wvaWFtLXRlc3QuaW5kaWdvLWRhdGFjbG91ZC5ldVwvIiwiZXhwIjoxNDY2MDkzOTE3LCJ"
             "pYXQiOjE0NjYwOTAzMTcsImp0aSI6IjE1OTU2N2U2LTdiYzItNDUzOC1hYzNhLWJjNGU5MmE1NjlhMCJ9.eINKxJa2J--xd"
             "GAZWIOKtx9Wi0Vz3xHzaSJWWY-UHWy044TQ5xYtt0VTvmY5Af-ngwAMGfyaqAAvNn1VEP-_fMYQZdwMqcXLsND4KkDi1ygiC"
             "IwQ3JBz9azBT1o_oAHE5BsPsE2BjfDoVRasZxxW5UoXCmBslonYd8HK2tUVjz0")
    assert OIDC.is_access_token_expired(token)


def test_refresh_access_token():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "new_access_token",
        "expires_in": 3600,
        "refresh_token": "new_refresh_token"
    }

    with patch("requests.post") as mock_post:
        mock_post.return_value = mock_response
        access_token = OIDC.refresh_access_token("old_refresh_token",
                                                 ["openid", "profile", "email"],
                                                 "http://test.com/token")

        assert access_token == "new_access_token"
        mock_post.assert_called_once_with(
            "http://test.com/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": "old_refresh_token",
                "client_id": "token-portal",
                "scope": "openid profile email"
            }
        )
