import json

val = {
    "numberOfPixels":
    722,
    "segments": [{
        "name": "spiral1",
        "pixels": [dict({"index": n}) for n in range(0, 300)]
    }, {
        "name": "spiral2",
        "pixels": [dict({"index": n}) for n in range(300, 439)]
    }, {
        "name": "spiral3",
        "pixels": [dict({"index": n}) for n in range(439, 520)]
    }, {
        "name": "outline",
        "pixels": [dict({"index": n}) for n in range(520, 722)]
    }, {
        "name":
        "subout1",
        "pixels": [{
            "index": 721
        }] + [dict({"index": n}) for n in range(520, 560)]
    }, {
        "name": "subout2",
        "pixels": [dict({"index": n}) for n in range(560, 598)]
    }, {
        "name": "subout3",
        "pixels": [dict({"index": n}) for n in range(598, 615)]
    }, {
        "name": "subout4",
        "pixels": [dict({"index": n}) for n in range(615, 629)]
    }, {
        "name":
        "subout5",
        "pixels": [dict({"index": n}) for n in range(629, 638)] +
        [dict({"index": n}) for n in range(690, 703)]
    }, {
        "name":
        "subout6",
        "pixels": [dict({"index": n}) for n in range(638, 648)] +
        [dict({"index": n}) for n in range(679, 690)]
    }, {
        "name":
        "subout7",
        "pixels": [dict({"index": n}) for n in range(648, 653)] +
        [dict({"index": n}) for n in range(672, 679)]
    }, {
        "name":
        "subout8",
        "pixels": [dict({"index": n}) for n in range(653, 659)] +
        [dict({"index": n}) for n in range(667, 672)]
    }, {
        "name": "subout9",
        "pixels": [dict({"index": n}) for n in range(659, 667)]
    }, {
        "name": "subout10",
        "pixels": [dict({"index": n}) for n in range(703, 721)]
    }]
}

pretty_json_string = json.dumps(val, indent=4, sort_keys=True)
print(pretty_json_string)