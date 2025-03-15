import streamlit as st
import pandas as pd
import requests
from dotenv import load_dotenv
import os
import streamlit.components.v1 as components

# Set page layout to wide
st.set_page_config(layout="wide")

# Display the header image using use_container_width
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("images/Bens-Math-World.png", use_container_width=True)

def load_api_token(dotenv_path='.env.local'):
    load_dotenv(dotenv_path=dotenv_path)
    token = os.environ.get('FOOTBALL_API_TOKEN')
    if not token:
        st.error("FOOTBALL_API_TOKEN environment variable not set")
        st.stop()
    return token

def fetch_standings(token):
    url = "https://api.football-data.org/v4/competitions/PL/standings"
    headers = {"X-Auth-Token": token}
    response = requests.get(url, headers=headers)
    data = response.json()
    standings = data.get('standings', [])
    total_table = next(
        (table.get('table', []) for table in standings if table.get('type') == "TOTAL"),
        None
    )
    if not total_table:
        st.error("Could not find a 'TOTAL' standings table.")
        st.stop()
    return total_table

def build_standings_df(total_table):
    rows = []
    team_names = []
    for entry in total_table:
        pos = entry.get('position')
        team = entry.get('team', {})
        team_id = team.get('id')
        team_name = team.get('name')
        crest = team.get('crest', '')
        team_html = f'<img src="{crest}" width="30" style="vertical-align: middle; margin-right: 5px;"> {team_name}'
        P = entry.get('playedGames')
        Pts = entry.get('points')
        # Compute predicted points (xPts)
        if P and P != 0:
            xPts = Pts + (Pts / P) * (38 - P)
        else:
            xPts = Pts
        row = {
            "Pos": pos,
            "Team Name": team_name,
            "Team": team_html,
            "team_id": team_id,
            "P": entry.get('playedGames'),
            "W": entry.get('won'),
            "D": entry.get('draw'),
            "L": entry.get('lost'),
            "GF": entry.get('goalsFor'),
            "GA": entry.get('goalsAgainst'),
            "GD": entry.get('goalDifference'),
            "Pts": Pts,
            "xPts": round(xPts, 1),
            "Form": entry.get('form')
        }
        rows.append(row)
        team_names.append(team_name)
    df = pd.DataFrame(rows)
    df.sort_values(by="Pos", inplace=True)
    return df, team_names

def style_standings_table(df, selected_team):
    def highlight_row(row):
        idx = row.name
        team_name = df.loc[idx, "Team Name"]
        pos = row["Pos"]
        max_pos = df["Pos"].max()
        if team_name == selected_team:
            return ['background-color: yellow'] * len(row)
        elif pos <= 4:
            return ['background-color: lightgreen'] * len(row)
        elif pos >= max_pos - 2:
            return ['background-color: lightcoral'] * len(row)
        else:
            return ['background-color: #f2f2f2' if pos % 2 == 0 else 'background-color: white'] * len(row)
    
    # Include xPts in the display, exclude Team Name and team_id
    display_columns = [col for col in df.columns if col not in ["Team Name", "team_id"]]
    display_df = df[display_columns]
    styled_df = (
        display_df.style
        .apply(highlight_row, axis=1)
        .set_table_styles([
            {'selector': 'table', 'props': [('border-collapse', 'collapse'), ('border', 'none')]},
            {'selector': 'th, td', 'props': [('padding', '4px'), ('border', '0px')]},
            {'selector': 'thead th:first-child', 'props': [('display', 'none')]},
            {'selector': 'tbody th', 'props': [('display', 'none')]}
        ])
        .format({'xPts': lambda x: f'<span style="color: grey;">{x}</span>'})
    )
    return styled_df

def get_team_details(team_id, token):
    url = f"https://api.football-data.org/v4/teams/{team_id}"
    headers = {"X-Auth-Token": token}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch team details for team id {team_id}")
        return None

def display_team_card(team_details):
    area = team_details.get("area", {})
    team_name = team_details.get("name", "Unknown Team")
    short_name = team_details.get("shortName", "")
    crest = team_details.get("crest", "")
    address = team_details.get("address", "N/A")
    website = team_details.get("website", "")
    founded = team_details.get("founded", "N/A")
    club_colors = team_details.get("clubColors", "N/A")
    venue = team_details.get("venue", "N/A")
    running_competitions = team_details.get("runningCompetitions", [])
    coach = team_details.get("coach", {})
    squad = team_details.get("squad", [])
    num_players = len(squad)

    card_html = f"""
    <div style="
         width:100%;
         margin:0px 0 20px 0;
         border:1px solid #ddd;
         border-radius:10px;
         padding:20px;
         box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
         font-family: Arial, sans-serif;">
      <div style="display:flex; align-items:center;">
          <img src="{crest}" alt="Team Crest" style="width:80px; height:80px; margin-right:20px; border-radius:50%;">
          <div>
              <h1 style="margin:0; font-size:24px;">{team_name}</h1>
              <p style="margin:0; color:#555;">{short_name}</p>
          </div>
      </div>
      <hr style="margin:20px 0;">
      <div style="display:flex; flex-wrap:wrap;">
          <div style="flex:1; min-width:150px;">
              <p><strong>Address:</strong> {address}</p>
              <p><strong>Website:</strong> <a href="{website}" target="_blank">{website}</a></p>
              <p><strong>Founded:</strong> {founded}</p>
          </div>
          <div style="flex:1; min-width:150px;">
              <p><strong>Club Colors:</strong> {club_colors}</p>
              <p><strong>Venue:</strong> {venue}</p>
              <p><strong>Area:</strong> {area.get("name", "N/A")}</p>
          </div>
      </div>
      <hr style="margin:20px 0;">
      <div>
          <h2 style="margin-bottom:10px; font-size:20px;">Running Competitions</h2>
          <div style="display:flex; flex-wrap:wrap;">
    """
    for comp in running_competitions:
        comp_name = comp.get("name", "Unknown")
        comp_emblem = comp.get("emblem", "")
        card_html += f"""
            <div style="margin-right:20px; text-align:center;">
                <img src="{comp_emblem}" alt="{comp_name}" style="width:40px; height:40px;"><br>
                <span style="font-size:12px;">{comp_name}</span>
            </div>
        """
    card_html += """
          </div>
      </div>
      <hr style="margin:20px 0;">
      <div>
          <h2 style="margin-bottom:10px; font-size:20px;">Coach</h2>
    """
    if coach:
        coach_name = coach.get("name", "N/A")
        coach_nationality = coach.get("nationality", "N/A")
        contract = coach.get("contract", {})
        contract_period = f"{contract.get('start', '')} to {contract.get('until', '')}" if contract else "N/A"
        card_html += f"""
          <p><strong>Name:</strong> {coach_name}</p>
          <p><strong>Nationality:</strong> {coach_nationality}</p>
          <p><strong>Contract:</strong> {contract_period}</p>
        """
    else:
        card_html += "<p>No coach information available.</p>"
    
    card_html += f"""
      </div>
      <hr style="margin:20px 0;">
      <div>
          <h2 style="margin-bottom:10px; font-size:20px;">Squad</h2>
          <p><strong>Number of players:</strong> {num_players}</p>
      </div>
    </div>
    """
    components.html(card_html, height=750)

def display_expected_card(standings_row):
    """
    Display a card showing expected (projected) stats for the selected team.
    The projections are computed as: expected_stat = current_stat * (38 / P)
    for each metric in [W, D, L, GF, GA, GD, Pts].
    """
    P = standings_row["P"]
    metrics = ["W", "D", "L", "GF", "GA", "GD", "Pts"]
    html = """
    <div style="
         width:100%;
         margin:0 0 20px 0;
         padding:20px;
         border:1px solid #ddd;
         border-radius:10px;
         box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
         font-family: Arial, sans-serif;">
      <h2 style="margin-bottom:20px;">Projected Season Stats</h2>
      <table style="width:100%; border-collapse: collapse;">
        <thead>
          <tr style="background-color: #f2f2f2;">
            <th style="padding:8px; text-align:left;">Metric</th>
            <th style="padding:8px; text-align:left;">Current</th>
            <th style="padding:8px; text-align:left;">Expected</th>
          </tr>
        </thead>
        <tbody>
    """
    for metric in metrics:
        current_val = standings_row[metric]
        expected_val = current_val * (38 / P) if P else current_val
        expected_val = round(expected_val, 1)
        html += f"""
          <tr>
            <td style="padding:8px; border-bottom:1px solid #ddd;">{metric}</td>
            <td style="padding:8px; border-bottom:1px solid #ddd;">{current_val}</td>
            <td style="padding:8px; border-bottom:1px solid #ddd;"><span style="color: grey;">{expected_val}</span></td>
          </tr>
        """
    html += """
        </tbody>
      </table>
    </div>
    """
    components.html(html, height=400)

def display_squad_card(team_details):
    """
    Display squad details as a nicely formatted HTML table (below the team card).
    """
    squad = team_details.get("squad", [])
    if not squad:
        st.write("No squad information available.")
        return

    html = """
    <div style="
         width:100%;
         margin:0;
         padding:20px;
         border:1px solid #ddd;
         border-radius:10px;
         box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
         font-family: Arial, sans-serif;">
      <h2 style="margin-bottom:20px;">Squad Details</h2>
      <table style="width:100%; border-collapse: collapse;">
        <thead>
          <tr style="background-color: #f2f2f2;">
            <th style="padding:8px; text-align:left;">Name</th>
            <th style="padding:8px; text-align:left;">Position</th>
            <th style="padding:8px; text-align:left;">Date of Birth</th>
            <th style="padding:8px; text-align:left;">Nationality</th>
          </tr>
        </thead>
        <tbody>
    """
    for player in squad:
        name = player.get("name", "N/A")
        position = player.get("position", "N/A")
        dob = player.get("dateOfBirth", "N/A")
        nationality = player.get("nationality", "N/A")
        html += f"""
          <tr>
            <td style="padding:8px; border-bottom:1px solid #ddd;">{name}</td>
            <td style="padding:8px; border-bottom:1px solid #ddd;">{position}</td>
            <td style="padding:8px; border-bottom:1px solid #ddd;">{dob}</td>
            <td style="padding:8px; border-bottom:1px solid #ddd;">{nationality}</td>
          </tr>
        """
    html += """
        </tbody>
      </table>
    </div>
    """
    computed_height = max(600, 200 + len(squad) * 40)
    components.html(html, height=computed_height)

def main():
    token = load_api_token()
    total_table = fetch_standings(token)
    df, team_names = build_standings_df(total_table)

    st.markdown("## Select a Premier League Team")
    selected_team = st.selectbox("Choose a team", sorted(team_names))

    # Identify the standings row for the selected team
    team_row = df[df["Team Name"] == selected_team].iloc[0]
    team_id = team_row["team_id"]

    # Two columns: left for table and right for team info
    left_col, right_col = st.columns([1, 1], gap="small")

    with left_col:
        st.markdown("### Premier League Table")
        st.markdown("Champions League spots in green, drop zones in coral, selected team in yellow:")
        styled_df = style_standings_table(df, selected_team)
        table_html = styled_df.to_html(escape=False)
        st.markdown(table_html, unsafe_allow_html=True)

    with right_col:
        st.markdown("### Team Information")
        team_details = get_team_details(team_id, token)
        if team_details:
            display_team_card(team_details)
            display_expected_card(team_row)
            display_squad_card(team_details)
        else:
            st.error("Team details not found.")

    st.markdown(
        '<p style="text-align: center; color: grey; font-size: small;">Football Data All - a Lab59 Production</p>',
        unsafe_allow_html=True
    )

if __name__ == '__main__':
    main()
