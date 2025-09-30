# 🐝 BeeDev Services - Business Lead Generation Process

> Website Design & Development Solutions

## Overview

This repository contains the automated lead generation process for BeeDev Services. The workflow extracts business information from Yelp and discovers business websites to build our mailer and cold call prospect lists.

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Virtual environment (recommended)

### Setup

1. Navigate to the project directory:
   ```bash
   cd client_list
   ```

2. Activate your virtual environment:
   ```bash
   source venv/bin/activate
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 📋 Process Workflow

### Step 1: Fetch Business Data from Yelp 🔍

Use `fetch_yelp.py` to search Yelp for businesses matching your target criteria. This creates a CSV file with business names, addresses, and Yelp URLs.

```bash
python fetch_yelp.py --term "coffee shops" --location "Oklahoma City, OK" --max 100
```

**Parameters:**
- `--term`: Business type or category (e.g., "coffee shops", "restaurants", "dental offices")
- `--location`: Target city and state (format: "City, ST")
- `--max`: Maximum number of results to fetch

**Output:** `yelp_[term]_[location].csv`

Example: `yelp_coffee_Oklahoma_City_OK.csv`

### Step 2: Discover Business Websites 🌐

Run `check_websites.py` to automatically find business websites. The script searches Yelp pages first, then attempts to guess and verify website URLs for businesses without listed websites.

```bash
python check_websites.py --input yelp_coffee_Oklahoma_City_OK.csv --output leads_coffee_ok.csv
```

**Parameters:**
- `--input`: Input CSV file from Step 1
- `--output`: Output filename for the final leads list

**Output:** Ready-to-use CSV file containing business information and verified website URLs

## 📁 File Structure

```
client_list/
├── fetch_yelp.py          # Yelp business data extraction
├── check_websites.py      # Website discovery and verification
├── requirements.txt       # Python dependencies
├── venv/                  # Virtual environment (create if needed)
└── output/               # Generated CSV files
```

## 🐛 Troubleshooting

### Common Issues

1. **Virtual Environment Not Activated**
   - Ensure you've activated your virtual environment before running scripts
   - Check that your terminal prompt shows the environment name

2. **Missing Dependencies**
   - Run `pip install -r requirements.txt` if you encounter import errors

3. **API Rate Limits**
   - Yelp API has rate limits; reduce `--max` parameter if encountering errors
   - Consider adding delays between requests for large datasets

4. **Website Discovery Failures**
   - Some businesses may not have websites or may have websites that are difficult to auto-discover
   - The script handles these gracefully and marks them appropriately in the output

## 📊 Output Format

The final CSV file contains the following columns:
- Business Name
- Address
- Phone Number
- Yelp URL
- Website URL (if found)
- Website Status (verified/not found/error)

## 🔧 Customization

### Modifying Search Terms

Edit the search terms in your command to target different business types:
```bash
# Target restaurants
python fetch_yelp.py --term "restaurants" --location "Austin, TX" --max 50

# Target dental offices  
python fetch_yelp.py --term "dental offices" --location "Dallas, TX" --max 25
```

### Adjusting Output Filenames

Use descriptive output filenames to organize your campaigns:
```bash
python check_websites.py --input yelp_restaurants_Austin_TX.csv --output leads_restaurants_austin_q1.csv
```

## 📞 Usage for Campaigns

The generated CSV files are ready for:
- Email marketing campaigns
- Cold calling lists
- Direct mail campaigns
- CRM import

## 🐝 BeeDev Services

*Buzzing with efficient lead generation • Creating sweet business opportunities*

---

For questions or support, contact the BeeDev Services team.