from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import json
import os
from dotenv import load_dotenv
import logging

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)
# CORS(app)  # CORS 허용


# API 기본 정보 (환경 변수에서 API 키 가져오기)
api_url = "https://api.neople.co.kr/df/servers/{serverId}/characters"
apikey = os.getenv('API_KEY')  # 환경 변수에서 API 키를 가져옴

# 기존 JSON 파일 경로
file_path = 'characters_full.json'

# API 키가 설정되어 있는지 확인하는 로직
if not apikey:
    raise EnvironmentError("API key not set. Please set the NEOPLE_API_KEY environment variable.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_character():
    data = request.json
    character_name = data.get('characterName')
    server_id = data.get('serverId')

    if not character_name or not server_id:
        return jsonify({"error": "Character name and server ID are required."}), 400

    # API 요청에 serverId 추가
    url = api_url.format(serverId=server_id)
    params = {
        "characterName": character_name,
        "apikey": apikey  # 서버에서 API 요청 시 API 키를 포함
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # 상태 코드 확인

        api_data = response.json()

        # Print the response to check
        print("API Response:", api_data)

        # 기존 파일 읽기 (있다면)
        characters = {}
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                characters = json.load(file)

        # 새 데이터를 기존 데이터에 추가
        for character in api_data['rows']:
            character_id = character['characterId']
            characters[character_id] = {
                "serverId": character["serverId"],
                "characterName": character["characterName"],
                "characterId": character['characterId']
            }

        # 모든 데이터를 저장 (덮어쓰기)
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(characters, file, indent=4, ensure_ascii=False)

        # # 검색된 캐릭터만 반환하도록 수정
        # characters = {}
        # for character in api_data['rows']:
        #     character_id = character['characterId']
        #     characters[character_id] = {
        #         "serverId": character["serverId"],
        #         "characterName": character["characterName"],
        #         "characterId": character['characterId']
        #     }

        # # 검색된 캐릭터 목록만 반환
        # return jsonify(characters)

        return jsonify(characters)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "API request failed.", "details": str(e)}), 500
    

# 장비 정보 API
@app.route('/api/equipment/<serverId>/<characterId>', methods=['GET'])
def get_equipment(serverId, characterId):
    equipment_url = f"https://api.neople.co.kr/df/servers/{serverId}/characters/{characterId}/equip/equipment?apikey={apikey}"
    try:
        response = requests.get(equipment_url)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "API request failed.", "details": str(e)}), 500
    

# 장비 상세 정보 요청 처리
# @app.route('/api/item/<item_id>')
# def get_item_detail(item_id):
#     response = requests.get(f'https://api.neople.co.kr/df/items/{item_id}?apikey=YOUR_API_KEY')
#     return jsonify(response.json())

# 로그 설정
logging.basicConfig(level=logging.INFO)

# @app.route('/api/item/<item_id>')
# def get_item_detail(item_id):
#     item_id_url = f'https://api.neople.co.kr/df/items/{item_id}?apikey={apikey}'
#     logging.info(f"Requesting URL: {item_id_url}")
    
#     response = requests.get(item_id_url)
#     logging.info(f"Response Status Code: {response.status_code}")
    
#     return jsonify(response.json())


@app.route('/api/item/<item_id>', methods=['GET'])
def get_item_detail(item_id):
    url = f'https://api.neople.co.kr/df/items/{item_id}?apikey={apikey}'
    logging.info(f"Requesting URL: {url}")

    response = requests.get(url)
    logging.info(f"Response Status Code: {response.status_code}")
    
    if response.status_code == 200:
        item_data = response.json()
        logging.info(f"Item Data: {item_data}")  # 응답 데이터 로깅
        return jsonify(item_data)
    else:
        logging.error(f"Error fetching item details: {response.text}")
        return jsonify({"error": "Failed to fetch item details"}), response.status_code



# 아바타 정보 API
@app.route('/api/avatar/<serverId>/<characterId>', methods=['GET'])
def get_avatar(serverId, characterId):
    avatar_url = f"https://api.neople.co.kr/df/servers/{serverId}/characters/{characterId}/equip/avatar?apikey={apikey}"
    try:
        response = requests.get(avatar_url)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "API request failed.", "details": str(e)}), 500

# 능력치 정보 API
@app.route('/api/status/<serverId>/<characterId>', methods=['GET'])
def get_status(serverId, characterId):
    status_url = f"https://api.neople.co.kr/df/servers/{serverId}/characters/{characterId}/status?apikey={apikey}"
    try:
        response = requests.get(status_url)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "API request failed.", "details": str(e)}), 500

# 크리처 정보 API
@app.route('/api/creature/<serverId>/<characterId>', methods=['GET'])
def get_creature(serverId, characterId):
    creature_url = f"https://api.neople.co.kr/df/servers/{serverId}/characters/{characterId}/equip/creature?apikey={apikey}"
    try:
        response = requests.get(creature_url)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "API request failed.", "details": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
