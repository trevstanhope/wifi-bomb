import curl

c = curl.Curl()
while True:
    s = c.get('192.168.0.1')
