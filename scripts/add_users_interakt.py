import sys, os, django

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

os.environ["DJANGO_SETTINGS_MODULE"] = "phurti.settings"
django.setup()


users = [
    [847, "Simran", None, "9711119991", "2022-01-27T13:53:28.683007+0000"],
    [778, "Divya Mahendra", None, "9930874732", "2022-01-21T09:54:54.720001+0000"],
    [739, "Neha Khemka", None, "9538079688", "2022-01-17T12:57:41.300084+0000"],
    [693, "Paromita", None, " 9730334568", "2022-01-14T04:29:38.375987+0000"],
    [676, "Sama", None, "9886823306", "2022-01-12T13:38:17.564018+0000"],
    [273, "Geeta", None, "7867931672", "2021-12-23T12:19:51.431600+0000", "+44"],
]

import http.client
import json

# import ipdb
# ipdb.set_trace()
for user in users:
    try:
        conn = http.client.HTTPSConnection("api.interakt.ai")
        payload = json.dumps(
            {
                "userId": f"{user[0]}",
                "phoneNumber": user[3],
                "countryCode": "+91" if len(user) == 5 else "+44",
                "traits": {"name": user[1], "email": user[2] if user[2] else ""},
                "createdAt": user[4],
            }
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic cEpVSURBRmlJdEpWNVVOQlozNkhDOVFZQmFlTk5JRjYxdUZLSkh4SUY3RTo=",
        }
        conn.request("POST", "/v1/public/track/users/", payload, headers)
        res = conn.getresponse()
        data = res.read()
        print(data.decode("utf-8"))
    except Exception as e:
        print(e)


# strftime('%Y-%m-%dT%H:%M:%S.%f%z')
