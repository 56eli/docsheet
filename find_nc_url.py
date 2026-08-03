#!/usr/bin/env python3
"""Search for Nightingale-Conant URL for 'In the World But Not of It'."""

import json

# Load the official discovery queue and other data files to see if NC URL is documented
import os

data_dir = 'data'
for filename in os.listdir(data_dir):
    if filename.endswith('.csv'):
        filepath = os.path.join(data_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'nightingale' in content.lower() or 'In the World' in content:
                print(f"\n=== {filename} mentions Nightingale or 'In the World' ===")
                # Show relevant lines
                for line in content.split('\n'):
                    if 'nightingale' in line.lower() or 'In the World' in line:
                        print(line[:200])

# Check decisions folder
decisions_dir = 'decisions'
for filename in os.listdir(decisions_dir):
    if filename.endswith('.md'):
        filepath = os.path.join(decisions_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'nightingale' in content.lower() and 'In the World' in content:
                print(f"\n=== {filename} mentions both ===")
                # Show context
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'nightingale' in line.lower() or 'In the World' in line:
                        start = max(0, i-2)
                        end = min(len(lines), i+3)
                        print('\n'.join(lines[start:end]))
                        print('---')

