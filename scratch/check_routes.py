import requests
base = 'http://localhost:8000'
endpoints = [
    '/',
    '/users/',
    '/users/roles',
    '/pricing/fuel/current',
    '/pricing/partners',
    '/settings/system',
    '/settings/logs',
]

for ep in endpoints:
    try:
        r = requests.get(base + ep)
        print(f"{ep}: {r.status_code}")
    except Exception as e:
        print(f"{ep}: Error {e}")
