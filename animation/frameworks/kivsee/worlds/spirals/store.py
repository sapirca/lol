import json
import requests
from spiralsmall import val as spiral_small_val
from spiralbig import val as spiral_big_val

RASPBERRY_PI_IP = "10.100.102.30"
OBJECT_URL = f"http://{RASPBERRY_PI_IP}:8081"

def store_object(thing_name, val):
    url = f"{OBJECT_URL}/thing/{thing_name}"
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(val)
    # print(f"Storing {thing_name} at {url} with data: {data}")
    # print("\n\n\n")
    response = requests.put(url, data=data, headers=headers)
    response.raise_for_status()
    print(f"Stored {thing_name}: {response.status_code}")

def get_object(thing_name):
    url = f"{OBJECT_URL}/thing/{thing_name}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def main():
    # store_object("spiral_small", spiral_small_val)
    # store_object("spiral_big", spiral_big_val)
    get_object("spiral_small")
    get_object("spiral_big")

if __name__ == "__main__":
    main()