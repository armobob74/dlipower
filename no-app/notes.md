### Date: Tue, 02-20-2024 ###
# Overview
It should be possible to call the DLI servers directly without worrying about PMAN stuff and timeouts

The DLI is *NOT ON WIFI*, it's directly connected to the build PC

https://www.digital-loggers.com/rest.html

example: (relay 3, but 0-indexed to 2)
for value, true means "on" and false means "off"

```sh
 curl --digest -u admin:1234 -X PUT -H "X-CSRF: x" --data "value=true" "http://192.168.0.100/restapi/relay/outlets/2/state/"
```

in Python:
```python3
import requests
from requests.auth import HTTPDigestAuth
response = requests.put(
	url = "http://192.168.0.100/restapi/relay/outlets/2/state/",
	data = {"value": "true"},
	headers = {
	"X-CSRF": "x"
	},
	auth = HTTPDigestAuth('admin','1234')
)
```

in JavaScript:
```js
fetch("http://192.168.0.100/restapi/relay/outlets/2/state/", {
  method: 'PUT', 
  headers: {
    'Authorization': 'Basic ' + btoa('admin:1234'), 
    'X-CSRF': 'x',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({value:"true"}) 
})
```

## Test 1 learnings:
- the DLI has some CORS issues
- tried to set CORS in the "External API" section, but it kept getting errors
- also Plaintext auth may not be enabled 
