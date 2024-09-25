import os
import requests
import json
import logging
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv('API_URL')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LuccaAPI:
    def __init__(self, api_url, auth_token):
        self.api_url = api_url
        self.headers = {
            "Authorization": f"lucca application={auth_token}"
        }

    def get_data(self, endpoint, params=None):
        url = f"{self.api_url}{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            logger.info(f"Récupération de {endpoint} réussie.")
            return response.json()
        else:
            logger.error(f"Erreur lors de la récupération de {endpoint}: {response.status_code}")
            return {}

    def get_all_users(self):
        users = []
        offset = 0
        limit = 1000
        while True:
            params = {
                "fields": (
                    "id,"
                    "name,"
                    "mail,"
                    "dtContractStart,"
                    "dtContractEnd,"
                    "rolePrincipal,"
                    "department"
                ),
                "dtContractEnd": "notequal,null"
            }
            response = requests.get(f"{self.api_url}/api/v3/users", headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data and 'data' in data and 'items' in data['data']:
                    logger.info(f"Récupération de {len(data['data']['items'])} utilisateurs.")
                    users.extend(data['data']['items'])
                    
                    if len(data['data']['items']) < limit:
                        break
                    offset += limit
                else:
                    logger.warning("Aucune donnée d'utilisateur trouvée.")
                    break
            else:
                logger.error(f"Erreur lors de la récupération des utilisateurs : {response.status_code}, {response.text}")
                break
        return users

    def get_departments(self):
        return self.get_data('/api/v3/departments')

            
def main():
    api = LuccaAPI(API_URL, AUTH_TOKEN)

    logger.info("Récupération des utilisateurs...")
    users = api.get_all_users()
    logger.info(f"Nombre d'utilisateurs récupérés : {len(users)}")

    logger.info("Récupération des départements...")
    departments = api.get_departments()
    logger.info(f"Nombre de départements récupérés : {len(departments)}")

    users_file = 'users_with_contracts.json'
    logger.info(f"Sauvegarde des utilisateurs dans le fichier {users_file}...")
    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

    departments_file = 'departments.json'
    logger.info(f"Sauvegarde des départements dans le fichier {departments_file}...")
    with open(departments_file, 'w', encoding='utf-8') as f:
        json.dump(departments, f, ensure_ascii=False, indent=4)

    logger.info("Processus terminé avec succès.")


if __name__ == "__main__":
    main()
