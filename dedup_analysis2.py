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

print("=== UUID 329 NOTES ===")
print(uuid_329['notes'])

print("\n=== CHECKING NIGHTINGALE-CONANT URLs ===")
# Find all records with Nightingale-Conant in format_detail or notes
nc_records = []
for r in master:
    if 'nightingale' in r.get('format_detail', '').lower() or 'nightingale' in r.get('notes', '').lower():
        nc_records.append(r)

print(f"Records mentioning Nightingale-Conant: {len(nc_records)}")
for r in nc_records[:10]:
    print(f"\nUUID {r['uuid']}: {r['title']}")
    print(f"  format_detail: {r['format_detail']}")
    print(f"  source_url_nightingale_conant: {r['source_url_nightingale_conant']}")
    print(f"  notes: {r['notes'][:100]}")

print("\n=== CHECKING HAY HOUSE URLs ===")
# Find all records with Hay House URLs
hh_records = [r for r in master if r['source_url_hay_house']]
print(f"Records with Hay House URLs: {len(hh_records)}")
for r in hh_records[:5]:
    print(f"\nUUID {r['uuid']}: {r['title']}")
    print(f"  source_url_hay_house: {r['source_url_hay_house']}")

# Check how many books should have Hay House URLs
book_records = [r for r in master if r['item_type'] == 'book']
print(f"\nTotal book records: {len(book_records)}")
books_with_hh = [r for r in book_records if r['source_url_hay_house']]
print(f"Books with Hay House URLs: {len(books_with_hh)}")
books_without_hh = [r for r in book_records if not r['source_url_hay_house']]
print(f"Books without Hay House URLs: {len(books_without_hh)}")

print("\n=== SAMPLE BOOKS WITHOUT HAY HOUSE URLs ===")
for r in books_without_hh[:5]:
    print(f"UUID {r['uuid']}: {r['title']}")
    print(f"  format: {r['format']}")
    print(f"  year: {r['year']}")

