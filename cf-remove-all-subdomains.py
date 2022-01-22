import argparse
import sys

parser = argparse.ArgumentParser(description='Remove all subdomains from a cloudflare domain')
parser.add_argument('--api_key', help='Check out https://dash.cloudflare.com/profile/api-tokens', required=True)
parser.add_argument('--domain', help='Domain to strip subdomains from', required=True)
parser.add_argument('--type', help='Specific type of DNS record to remove')

import requests
BASE_URL = 'https://api.cloudflare.com/client/v4/'
def make_request(method, path, params={}):
    assert(method in ['get', 'post', 'delete'])
    results = []
    page = 1
    while True:
        # Flirting with the classic python bug here
        params['page'] = page
        r = getattr(requests, method)(
            BASE_URL + path,
            headers = {
                'Authorization' : 'Bearer ' + args.api_key,
                'Content-Type' : 'application/json',
            },
            params=params,
        )
        j = r.json()

        #import pprint
        #print(r.status_code)
        #pprint.pp(j)
        r.raise_for_status()
        assert(j['success'] == True)

        # If a dict, bomb out without paging
        if type(j['result']) is dict:
            return j['result']

        results.extend(j['result'])
        if page == j['result_info']['total_pages']:
            break
        page += 1
    return results

if __name__ == '__main__':
    args = parser.parse_args()
    print("BARELY TESTED DESTRUCTIVE CODE. USE AT OWN RISK. WHY WOULD YOU DO THIS TO YOURSELF.")
    make_request('get', 'user/tokens/verify')
    zones = [z for z in make_request('get', 'zones') if z['name'] == args.domain]
    assert(len(zones) == 1)
    zone = zones[0]

    if args.type != None:
        params = {'type' : args.type}
    else:
        params = {}
    records = make_request('get', 'zones/' + zone['id'] + '/dns_records', params)
    print(f"Found the following {len(records)} records:")
    for r in records:
        print(f"{r['type']}: {r['name']}")
    sys.exit(0)
    if input("Type domain name to remove all records: ") != args.domain:
        sys.exit(0)
    print('Removing DNS records')
    for count, r in enumerate(records):
        print(f"Removing {count+1} of {len(records)}: {r['name']}")
        make_request('delete', 'zones/' + zone['id'] + '/dns_records/' + r['id'])
