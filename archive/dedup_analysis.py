#!/usr/bin/env python3
"""Analyze potential duplicates UUID 264 and UUID 329."""

import csv

# Load master
with open('data/research_master_draft.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    master = list(reader)

# Find UUID 264 and 329
uuid_264 = next((r for r in master if r['uuid'] == '264'), None)
uuid_329 = next((r for r in master if r['uuid'] == '329'), None)

print("=== UUID 264 ===")
for k, v in uuid_264.items():
    if v:
        print(f"{k}: {v}")

print("\n=== UUID 329 ===")
for k, v in uuid_329.items():
    if v:
        print(f"{k}: {v}")

print("\n=== COMPARISON ===")
print(f"Title match: {uuid_264['title'] == uuid_329['title']}")
print(f"Series match: {uuid_264['series'] == uuid_329['series']}")
print(f"Work ID match: {uuid_264['work_id'] == uuid_329['work_id']}")

# Check work families
with open('data/work_families.csv', 'r', encoding='utf-8') as f:
    families = list(csv.DictReader(f))

fam_264 = [f for f in families if f['uuid'] == '264']
fam_329 = [f for f in families if f['uuid'] == '329']

print("\n=== WORK FAMILIES ===")
print(f"UUID 264 in families: {len(fam_264)}")
print(f"UUID 329 in families: {len(fam_329)}")

# Check edition promotions
with open('data/edition_promotions.csv', 'r', encoding='utf-8') as f:
    editions = list(csv.DictReader(f))

ed_264 = [e for e in editions if e['uuid'] == '264']
ed_329 = [e for e in editions if e['uuid'] == '329']

print("\n=== EDITION PROMOTIONS ===")
print(f"UUID 264 in editions: {len(ed_264)}")
print(f"UUID 329 in editions: {len(ed_329)}")

# Check product relationships
with open('data/product_relationships.csv', 'r', encoding='utf-8') as f:
    relationships = list(csv.DictReader(f))

rel_264 = [r for r in relationships if r['uuid'] == '264']
rel_329 = [r for r in relationships if r['uuid'] == '329']

print("\n=== PRODUCT RELATIONSHIPS ===")
print(f"UUID 264 relationships: {len(rel_264)}")
print(f"UUID 329 relationships: {len(rel_329)}")

for r in rel_264:
    print(f"  264: {r['relationship_type']} -> {r['related_uuid']}")
for r in rel_329:
    print(f"  329: {r['relationship_type']} -> {r['related_uuid']}")

