import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def http_get(url):
    with requests.Session() as s:
        retries = Retry(total=20,
                        backoff_factor=0.1)
        s.mount('http://', HTTPAdapter(max_retries=retries))
        return s.get(url)
