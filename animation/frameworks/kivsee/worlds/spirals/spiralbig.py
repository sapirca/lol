import json
val = {
        "numberOfPixels": 1307,
        "segments": [{
            "name": "spiral1",
            "pixels": [dict({"index": n}) for n in range(0, 92)]
        },
        {
            "name": "spiral2",
            "pixels": [dict({"index": n}) for n in range(92, 391)]
        },
        {
            "name": "spiral3",
            "pixels": [dict({"index": n}) for n in range(391, 691)]
        },
        {
            "name": "spiral4",
            "pixels": [dict({"index": n}) for n in range(691, 850)]
        },
        {
            "name": "spiral5",
            "pixels": [dict({"index": n}) for n in range(830, 878)]
        },
        {
            "name": "outline",
            "pixels": [dict({"index": n}) for n in range(878, 1168)]
        },
        {
            "name": "spiral6",
            "pixels": [dict({"index": n}) for n in range(1168, 1307)]
        },
        {
            "name": "subout1",
            "pixels": [dict({"index": n}) for n in range(878, 932)]
        },
        {
            "name": "subout2",
            "pixels": [dict({"index": n}) for n in range(932, 954)] + [dict({"index": n}) for n in range(1150, 1168)]
        },
        {
            "name": "subout3",
            "pixels": [dict({"index": n}) for n in range(954, 987)]
        },
        {
            "name": "subout4",
            "pixels": [dict({"index": n}) for n in range(987, 1021)]
        },
        {
            "name": "subout5",
            "pixels": [dict({"index": n}) for n in range(1021, 1028)] + [dict({"index": n}) for n in range(1152, 1057)]
        },
        {
            "name": "subout6",
            "pixels": [dict({"index": n}) for n in range(1028, 1048)]
        },
        {
            "name": "subout7",
            "pixels": [dict({"index": n}) for n in range(1057, 1091)]
        },
        {
            "name": "subout8",
            "pixels": [dict({"index": n}) for n in range(1091, 1101)]
        },
        {
            "name": "subout9",
            "pixels": [dict({"index": n}) for n in range(1101, 1123)]
        },
        {
            "name": "subout10",
            "pixels": [dict({"index": n}) for n in range(1123, 1152)]
        }
        ]
    }

pretty_json_string = json.dumps(val, indent=4, sort_keys=True)
print(pretty_json_string)