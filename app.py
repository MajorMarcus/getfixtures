from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote 
import urllib.parse

def transform_image_url(original_url):
    # Parse the original URL
    parsed_url = urllib.parse.urlparse(original_url)
    
    # Extract the 'image' query parameter which contains the original image URL
    query_params = urllib.parse.parse_qs(parsed_url.query)
    original_image_url = query_params.get('image', [None])[0]
    
    if original_image_url:
        # Decode the image URL
        decoded_image_url = urllib.parse.unquote(original_image_url)
        
        
        return decoded_image_url
    else:
        return None # Import unquote to decode URLs

app = Flask(__name__)

@app.route('/fixtures/<team>', methods=['GET'])
def get_fixtures(team):
    fixtures_list = []  
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
        
        # Fetch team logos and decode the URL
        for team in teams:
            logo = team.find('img', class_='ImageWithSets_of-image__img__pezo7')
            if logo:
                decoded_logo_url = transform_image_url(logo['src'])  # Decode the logo URL
                logos.append(decoded_logo_url)
        
        # Fetch the match date
        date = fixture.find('time', class_='title-8-bold').text if fixture.find('time', class_='title-8-bold') else "Date not found"
        time = fixture.find('time', class_='SimpleMatchCard_simpleMatchCard__infoMessage___NJqW title-8-medium').text if fixture.find('time', class_='SimpleMatchCard_simpleMatchCard__infoMessage___NJqW title-8-medium') else "Date not found"
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
