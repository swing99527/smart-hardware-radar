#!/bin/bash
cd /Users/chenshangwei/code/smart-hardware-radar
mkdir -p v2/input/l2 v2/input/l3 raw_data

echo "[1/3] Fetching S001: Smart Ring..."
accio-mcp-cli call js_product_database_query --json '{"include_keywords": ["Smart Ring"], "marketplace": "us", "min_revenue": 1000, "page_size": 30}' > raw_data/S001_L3.json
accio-mcp-cli call js_keywords_by_keyword --json '{"search_terms": "Smart Ring", "marketplace": "us", "page_size": 10}' > raw_data/S001_L2.json

echo "[2/3] Fetching S002: Smart Glasses..."
accio-mcp-cli call js_product_database_query --json '{"include_keywords": ["Smart Glasses"], "marketplace": "us", "min_revenue": 1000, "page_size": 30}' > raw_data/S002_L3.json
accio-mcp-cli call js_keywords_by_keyword --json '{"search_terms": "Smart Glasses", "marketplace": "us", "page_size": 10}' > raw_data/S002_L2.json

echo "[3/3] Fetching S003: Audio Sunglasses..."
accio-mcp-cli call js_product_database_query --json '{"include_keywords": ["Audio Sunglasses"], "marketplace": "us", "min_revenue": 1000, "page_size": 30}' > raw_data/S003_L3.json
accio-mcp-cli call js_keywords_by_keyword --json '{"search_terms": "Audio Sunglasses", "marketplace": "us", "page_size": 10}' > raw_data/S003_L2.json

echo "Raw data fetched. Parsing..."
