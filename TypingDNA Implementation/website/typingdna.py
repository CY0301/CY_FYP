import urllib.request, base64
import json 

def send_typing_data(user_id, pattern):
    base_url = 'https://api.typingdna.com'
    apiKey = '086f3692e85cc39625643a96dfbefea3'
    apiSecret = '4cbd410fb632657ad02657eb451f0eb8'
    tp = pattern

    authstring = '%s:%s' % (apiKey, apiSecret)
    base64string = base64.b64encode(authstring.encode()).decode().replace('\n', '')
    data = urllib.parse.urlencode({'tp':tp})
    url = '%s/auto/%s' % (base_url, user_id)

    request = urllib.request.Request(url, data.encode('utf-8'), method='POST')
    request.add_header("Authorization", "Basic %s" % base64string)
    request.add_header("Content-type", "application/x-www-form-urlencoded")

    res = urllib.request.urlopen(request)
    res_body = res.read()
    return json.loads(res_body.decode('utf-8'))