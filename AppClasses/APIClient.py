import requests
import requests_cache
import time
from kivymd.toast import toast
from kivymd.app import MDApp


class APIClient:
    def __init__(self, access_token=None, refresh_token=None):
        self.base_url = "http://127.0.0.1:8000"
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.app = MDApp.get_running_app()

        # Enable GET response caching (30 seconds default)
        #requests_cache.install_cache("api_cache", expire_after=90)

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
        }

    def _url(self, endpoint):
        return f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    def _handle_response(self, response, method, endpoint, **kwargs):
        print(f"response code and refresh token are {response.status_code} and {self.refresh_token}")
        if response.status_code == 401 or response.status_code == 403:
            print("[Auth] Token expired, attempting refresh...")
            if self.refresh_token and self._refresh_access_token():
                print("[Auth] Retry after refreshing token")
                return self._request(method, endpoint, **kwargs)
            else:
                # After app in-active without logout for a long time(refresh token expiry time)
                #self.app.logout()
                return {"error" : "Forbidden"}
        response.raise_for_status()
        return response.json()

    def _refresh_access_token(self):
        try:
            resp = requests.post(self._url("/refresh"), json={"refresh_token": self.refresh_token})
            if resp.status_code == 200:
                tokens = resp.json()
                self.access_token = tokens.get("access_token")
                self.refresh_token = tokens.get("refresh_token")
                print("[Auth] Token refreshed successfully.")
                return True
        except Exception as e:
            print(f"[Auth] Refresh failed: {e}")
        return False

    def _request(self, method, endpoint, **kwargs):
        url = self._url(endpoint)
        headers = self._headers()
        kwargs.setdefault("headers", headers)

        response = requests.request(method, url, **kwargs)

        if hasattr(response,"from_cache") and response.from_cache:
            print(f"[CACHE] {method.upper()} {url}")
        else:
            print(f"[LIVE] {method.upper()} {url}")

        return self._handle_response(response, method, endpoint, **kwargs)

    # Common HTTP methods
    def get(self, endpoint, **kwargs):
        return self._request("GET", endpoint, **kwargs)

    def post(self, endpoint, **kwargs):
        return self._request("POST", endpoint, **kwargs)

    def put(self, endpoint, **kwargs):
        return self._request("PUT", endpoint, **kwargs)

    def delete(self, endpoint, **kwargs):
        return self._request("DELETE", endpoint, **kwargs)

    def login(self, phone_number, otp):
        resp = requests.post(self._url("/token"), json={
            "phone_number": phone_number,
            "otp": otp
        })

        if resp.status_code == 200:
            tokens = resp.json()
            self.access_token = tokens.get("access_token")
            self.refresh_token = tokens.get("refresh_token")
            print("[Auth] Logged in successfully.")
            return True
        else:
            print("[Auth] Login failed.")
            return False


    def logout(self):
        resp = requests.post(self._url("/logout"),json={"refresh_token" : str(self.refresh_token)})
        if resp.status_code == 200:
            print("[Auth] Logged out successfully")
            return True
        else:
            print("[Auth] Error in logging out")
            return False
