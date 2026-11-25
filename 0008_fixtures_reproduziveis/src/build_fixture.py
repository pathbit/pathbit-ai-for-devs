#!/usr/bin/env python3
"""Render deterministic JSON orders from explicit input."""

import argparse
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import re
import sys


def build_fixture(specification):
    if not isinstance(specification, dict) or set(specification) != {"seed", "created_at", "customers"}:
        raise ValueError("Expected seed, created_at and customers.")
    seed = specification["seed"]
    timestamp = specification["created_at"]
    customers = specification["customers"]
    if not isinstance(seed, str) or not seed.strip():
        raise ValueError("seed must be a nonempty string.")
    if not isinstance(timestamp, str) or not re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", timestamp
    ):
        raise ValueError("created_at must use YYYY-MM-DDTHH:MM:SSZ.")
    datetime.fromisoformat(timestamp.removesuffix("Z") + "+00:00")
    if not isinstance(customers, list) or not customers:
        raise ValueError("customers must be a nonempty list.")

    names = {}
    for customer in customers:
        if not isinstance(customer, dict) or set(customer) != {"id", "name"}:
            raise ValueError("Each customer needs id and name.")
        customer_id, name = customer["id"], customer["name"]
        if not isinstance(customer_id, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", customer_id):
            raise ValueError("Customer IDs must use lowercase ASCII letters, digits and optional hyphens.")
        if customer_id in names:
            raise ValueError(f"Duplicate customer ID: {customer_id}")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"Customer {customer_id} needs a nonempty name.")
        names[customer_id] = name

    orders = []
    for customer_id in sorted(names):
        key = json.dumps(["order-amount-v1", seed, customer_id], separators=(",", ":"))
        digest = sha256(key.encode("ascii")).digest()
        amount = 1000 + int.from_bytes(digest[:4], "big") % 9000
        orders.append(
            {"order_id": f"order-{customer_id}", "customer_id": customer_id,
             "customer_name": names[customer_id], "amount_cents": amount, "created_at": timestamp}
        )
    return {"schema_version": 1, "orders": orders}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("specification", type=Path)
    parser.add_argument("--check", type=Path, help="Compare against a golden file without writing it.")
    args = parser.parse_args()
    try:
        specification = json.loads(args.specification.read_text(encoding="utf-8"))
        fixture = build_fixture(specification)
        rendered = (json.dumps(fixture, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
        if args.check is None:
            sys.stdout.buffer.write(rendered)
        elif args.check.read_bytes() != rendered:
            print(f"Fixture differs: {args.check}", file=sys.stderr)
            return 1
        else:
            print(f"Fixture matches: {args.check}")
    except (OSError, ValueError) as error:
        print(f"Fixture could not be generated: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
