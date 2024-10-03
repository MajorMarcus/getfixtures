from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_image_string(big_string):
    # Extracts the image URL after 'image='
    parts = big_string.split('image=', 1)
    if len(parts) > 1:
        return parts[1]
    return None

@app.route('/fixtures/<team>', methods=['GET'])
def get_fixtures(team):
    fixtures_list = []  # Rename to avoid conflict
    url = f'https://onefootball.com/en/team/{team}/fixtures'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    fixtures = soup.find_all('div', class_='SimpleMatchCard_simpleMatchCard__content__ZWt2p')

    for fixture in fixtures:
        teamnames = []
        logos = []

        teams = fixture.find_all('div', class_='SimpleMatchCard_simpleMatchCard__teamContent__hQHVO SimpleMatchCardTeam_simpleMatchCardTeam___GPYH')
        
        # Fetch team names
        for team in teams:
            teamname = team.find('span', class_='SimpleMatchCardTeam_simpleMatchCardTeam__name__7Ud8D')
            if teamname:
                teamnames.append(teamname.text)
        
        # Fetch team logos
        for team in teams:
            logo = team.find('img', class_='ImageWithSets_of-image__img__pezo7')
            logo = get_image_string(logo['src'])
            if logo:
                logos.append(logo)  # Get the image URL
        
        # Fetch the match date
        date = fixture.find('time', class_='title-8-bold').text if fixture.find('time', class_='title-8-bold') else "Date not found"
        time = fixture.find('time', class_='SimpleMatchCard_simpleMatchCard__infoMessage___NJqW title-8-medium').text if fixture.find('time', class_='title-8-bold') else "Date not found"
        if len(teamnames) == 2 and len(logos) == 2:  # Ensure both teams and logos are found
            fixtures_list.append({
                'team 1': teamnames[0],
                'team 2': teamnames[1],
                'team 1 logo': logos[0],
                'team 2 logo': logos[1],
                'date': date, 
                'time': time
            })

    return jsonify(fixtures_list)

if __name__ == '__main__':
    app.run(debug=True)
