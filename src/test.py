import subprocess
from oracle_tools import is_same_dom, do_xss_post_request
import time

endpoint = 'http://127.0.0.1:5555/vuln_backend/1.0/endpoint/'

f = open("./XSS_dataset.csv", "r", encoding="utf-8")
lines = f.readlines()

for line in lines:
    payload, answer = line[:-2], line[-1:]
    result_1 = do_xss_post_request(endpoint, 'abc')
    result_2 = do_xss_post_request(endpoint, payload)
    print(payload[:10], is_same_dom(result_1, result_2))
    time.sleep(1)
