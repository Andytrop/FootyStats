import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env.local file
load_dotenv(dotenv_path='.env.local')

token = os.environ.get('FOOTBALL_API_TOKEN')
if not token:
    raise ValueError("FOOTBALL_API_TOKEN environment variable not set")

# Set your team name here
my_team = "Liverpool"

uri = 'https://api.football-data.org/v4/matches'
headers = {'X-Auth-Token': token}

response = requests.get(uri, headers=headers)
data = response.json()

# Filter matches where my_team is involved (either as home or away team)
filtered_matches = []
for match in data.get('matches', []):
    home_team = match.get('homeTeam', {}).get('name', '')
    away_team = match.get('awayTeam', {}).get('name', '')
    if my_team in home_team or my_team in away_team:
        filtered_matches.append(match)

# Save the filtered matches into a new JSON file
with open('filtered_matches.json', 'w') as f:
    json.dump(filtered_matches, f, indent=4)

print(f"Found {len(filtered_matches)} match(es) involving {my_team}.")
