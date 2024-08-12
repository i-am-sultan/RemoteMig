from oauth2client.service_account import ServiceAccountCredentials
import socket
import pandas as pd
import logging
import os
import requests
from google_sheet import *
from log_sheet import *

# Logging Configuration
LOG_DIR = os.path.join(os.getcwd(), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOG_DIR, f'migration_log_{socket.gethostname()}.log')

logging.basicConfig(filename=LOG_FILE_PATH,filemode='a',format='%(asctime)s - %(levelname)s - %(message)s',level=logging.INFO)

def get_latest_release_info(repo):
    api_url = f"https://api.github.com/repos/{repo}/releases/latest"
    headers = {
        'Accept': 'application/vnd.github.v3+json'
    }
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        release_info = response.json()
        return release_info
    else:
        print(f"Failed to fetch release information. Status code: {response.status_code}")
        return None

def checkForUpdates():
    logging.info('Checking for updates...')
    try:
        repo = "i-am-sultan/MigrationApp"
        latest_release = get_latest_release_info(repo)

        if latest_release:
            latest_version = latest_release['tag_name']
            assets = latest_release['assets']

            if assets:
                update_asset = assets[0]  # Assuming the first asset is the one you want to download
                update_url = update_asset['browser_download_url']
                os.chdir('..')  # Now in MigrationApp folder
                version_path = os.path.join(os.getcwd(), 'app', 'version.txt')

                # Read the current version from a file
                try:
                    with open(version_path, 'r') as f:
                        current_version = f.read().strip()
                except Exception as e:
                    logging.info(f'Failed to read the current version. Error: {e}')
                    return 1

                logging.info(f'Current version: {current_version}')
                logging.info(f'Latest version: {latest_version}')

                # Compare versions
                if latest_version != current_version:
                    logging.info('New version available. Downloading and applying update...')

                    # Download the update
                    response = requests.get(update_url)
                    if response.status_code == 200:
                        update_dir_path = os.getcwd()  # cwd: MigrationApp

                        try:
                            # Extract the zip file into the new directory
                            with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
                                zip_ref.extractall(update_dir_path)

                            logging.info('Update downloaded and extracted successfully.')
                            logging.info('Update applied successfully.')
                            icon_path = os.path.join(update_dir_path, 'app', 'data-migration.ico')
                            file_path = os.path.join(update_dir_path, 'app', 'main.py')

                        except Exception as e:
                            logging.info(f'Failed to extract and apply update. Error: {e}')
                            return 1
                    else:
                        logging.info(f"Failed to download update. Status code: {response.status_code}")
                        return 1
                else:
                    logging.info('You are already using the latest version.')
                    return 1
            else:
                logging.info('No assets found in the latest release.')
                return 1
        else:
            logging.info('Failed to fetch latest release information.')
            return 1

    except Exception as e:
        logging.info(f'Error checking and applying updates: {e}')
        return 1

if __name__ == '__main__':
    result = checkForUpdates()
    version_path = os.getcwd()
    if result == 0:
        print(f'Updated! Now close this application! Run the latest Verison!\n Check the latest version in directory: {version_path}')
