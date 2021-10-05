import argparse
import pprint
import redis
import vt
import json
from typing import Sequence, Dict, Optional
from dataclasses import dataclass, field, asdict


# TBD: move to yaml config file
VT_URL_ANALYSIS_RISK_INDICATORS = ('malicious', 'phishing', 'malware')
# SCAN EXPIRY
SCAN_EXPIRE = 15*60  # in seconds

r = redis.Redis(host='localhost', port=6379)

@dataclass
class SiteScan:
    is_risky: bool = field(default=False)

    def serialize(self):
        return json.dumps(asdict(self))
    
    @classmethod
    def deserialize(cls, input):
        return cls(**json.loads(input))


def get_site_scan(url: str, vt_apikey: str) -> SiteScan:
    #yes/no url is risky

    url_id = vt.url_id(url)
    with vt.Client(vt_apikey) as vt_client:
        url_res = vt_client.get_object(f'/urls/{url_id}')
    

    # at least one risk indicator?
    is_risky = any(
        url_res.last_analysis_stats.get(key, 0) > 0
        for key in VT_URL_ANALYSIS_RISK_INDICATORS)

    return SiteScan(
        is_risky=is_risky,
    )

def save_to_redis(url: str, scan: SiteScan):
    # cache results for a scan
    r.set(url, scan.serialize(), ex=SCAN_EXPIRE)

def get_urls_from_cache(urls: Sequence[str])->Dict[str, Optional[SiteScan]]:
    # fetch cached scans from db
    return {
        url: SiteScan.deserialize(cache_str) if cache_str else None
        for url, cache_str in zip(urls, r.mget(urls))
    }



def main():

    parser = argparse.ArgumentParser(description='Enqueue URLs to be scanned.')

    parser.add_argument('--apikey', type=str, required=True, 
                        help='your VirusTotal API key')
    parser.add_argument('--file', type=str, required=True,
                        help='ds1 input file')
    parser.add_argument('--reset-cache',
                        default=False,
                        action='store_true',
                        help='ignore the results in the cache')

    args = parser.parse_args()
    
    with open(args.file, 'r') as f:
        urls = set(l.strip() for l in f.readlines())
        assert urls, f'no urls found in {args.file}'

    # fetch results from cache if exists
    results = get_urls_from_cache(urls) if not args.reset_cache else {
        url: None for url in urls
    }

    missing_from_cache = (
        key
        for key, value in results.items()
        if value is None
    )

    # fetch what we are missing from VT
    for url in missing_from_cache:
        print(f'url is not fresh - fetching from VT...{url}')
        scan = get_site_scan(url, args.apikey)
        results[url] = scan
        save_to_redis(url, scan)

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(results)



if __name__ == '__main__':
  main()