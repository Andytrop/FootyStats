import requests
import json
import os

from dotenv import load_dotenv

# Load environment variables from .env.local file
load_dotenv(dotenv_path='.env.local')


token = os.environ.get('FOOTBALL_API_TOKEN')
if not token:
    raise ValueError("FOOTBALL_API_TOKEN environment variable not set")


uri = 'https://api.football-data.org/v4/matches'
headers = {'X-Auth-Token': token}  # Replace YOUR_TOKEN with your actual API token

response = requests.get(uri, headers=headers)
data = response.json()

# Filter matches where Liverpool is involved (either as home or away team)
liverpool_matches = []
for match in data.get('matches', []):
    home_team = match.get('homeTeam', {}).get('name', '')
    away_team = match.get('awayTeam', {}).get('name', '')
    if "Liverpool" in home_team or "Liverpool" in away_team:
        liverpool_matches.append(match)

# Save the filtered matches into a new JSON file
with open('liverpool_matches.json', 'w') as f:
    json.dump(liverpool_matches, f, indent=4)

print(f"Found {len(liverpool_matches)} Liverpool match(es).")