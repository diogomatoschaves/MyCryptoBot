
token_default = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlFrTkZOak0xTURnNE5ETTFORFpFTjBVNU1rWTJORVpDT0RORE1rUTBSamN3TWpSR1JEazJRdyJ9.eyJnaXZlbl9uYW1lIjoiRGlvZ28iLCJmYW1pbHlfbmFtZSI6IkNoYXZlcyIsIm5pY2tuYW1lIjoiZGkubWF0b3NjaGF2ZXMiLCJuYW1lIjoiRGlvZ28gQ2hhdmVzIiwicGljdHVyZSI6Imh0dHBzOi8vbGg0Lmdvb2dsZXVzZXJjb250ZW50LmNvbS8taXZMbEZHc0NYVGMvQUFBQUFBQUFBQUkvQUFBQUFBQUFBQUEvQU1adXVja2VVNzBId2tsNE1xSV9EZV9QLVo3QXFuOTlpUS9zOTYtYy9waG90by5qcGciLCJsb2NhbGUiOiJlbiIsInVwZGF0ZWRfYXQiOiIyMDIxLTAzLTEyVDE3OjE3OjMzLjc1M1oiLCJlbWFpbCI6ImRpLm1hdG9zY2hhdmVzQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJpc3MiOiJodHRwczovL2FjY291bnRzLm1lc3NhcmkuaW8vIiwic3ViIjoiZ29vZ2xlLW9hdXRoMnwxMTc5NzU5MDU5NDY5MTAyODU5OTciLCJhdWQiOiJHRjhRV2ZZNGR4UnRmVVVRVldEN1JjWGpKcEcxYjk4biIsImlhdCI6MTYxNTY2OTUxNCwiZXhwIjoxNjE2Mjc0MzE0fQ.sEcmFIwMhAWrAMd_sc6zGTTeziMQSzXNPqBTx_39YTkCtUEgl7lv2QYod8HtE1jjtws7CkbIldKUXM2_ja-wDbJ4YRFNSFA9e0kosYdAJvhlVqy5USzmiIJ_DcxGai7-5QNSbh1xH7Q6cNxIhMEfR_gOWYBwIpF-17_9aRjd-beFCsBDQP1ok1ZGhxsOrMNbePD04PHq6jrt39P9PN10UhgBiPwj3Lsa6s8JkB00eIY87mJfKXi2OPaQlGOkoQcIDhseyWSkIeolDGpMOJn6h3XvXePqgthQNmOI_3KwipDenN-BCDCQvfLnJjSkChqE7wWRH5dyTGz0N3czYvIb-A"


def get_headers(token=token_default):
    return {
        'authority': 'data.messari.io',
        'method': 'GET',
        'path': '/api/v1/assets/1e31218a-e44e-4285-820c-8282ee222035/metrics/price/time-series?beg=2021-02-13T19%3A22'
                '%3A48.906Z&end=2021-03-13T19%3A22%3A48.906Z&interval=1h',
        'scheme': 'https',
        'authorization': f'Bearer {token}',
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,pt;q=0.8,es;q=0.7',
        'cache-control': 'no-cache',
        'origin': 'https://messari.io',
        'pragma': 'no-cache',
        'referer': 'https://messari.io/',
        'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/88.0.4324.192 Safari/537.36',
    }