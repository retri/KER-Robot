#!/usr/bin/env python3
import json
import pathlib
import sys

REQUIRED_QOS = {"reliability", "durability", "depth"}

def validate(data):
    errors = []
    names = [item.get("name") for item in data.get("topics", [])]
    if len(names) != len(set(names)):
        errors.append("duplicate topic name")
    for idx, item in enumerate(data.get("topics", [])):
        label = item.get("name") or f"topics[{idx}]"
        if not str(label).startswith("/ker/"):
            errors.append(f"{label}: namespace must start /ker/")
        if not item.get("type") or "/msg/" not in item["type"]:
            errors.append(f"{label}: invalid message type")
        missing = REQUIRED_QOS - set(item.get("qos", {}))
        if missing:
            errors.append(f"{label}: missing QoS {sorted(missing)}")
        if item.get("qos", {}).get("depth", 0) < 1:
            errors.append(f"{label}: QoS depth must be >= 1")
    if "motion_safety_gate" != next((x["publisher"] for x in data["topics"] if x["name"].endswith("joint_command_safe")), None):
        errors.append("safe joint command must be owned by motion_safety_gate")
    return errors

if __name__ == "__main__":
    path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).parents[1] / "config/topic_contract.json"
    errors = validate(json.loads(path.read_text(encoding="utf-8")))
    if errors:
        print("\n".join(errors))
        raise SystemExit(1)
    print(f"PASS: {path}")
