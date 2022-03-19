import os
import requests
from zipfile import ZipFile

def check_font_extension(font_name):
    ALLOWED_FONT_EXTENSIONS = ['ttf', 'otf', 'ttc']
    return font_name.rsplit('.', 1)[-1].lower() in ALLOWED_FONT_EXTENSIONS

def download_font(font_path):
    print('Downloading fonts...')
    link_id = '122Xio9ZiJm2Ulqh6U-S5FAabVHMXi_zQ'
    save_dir = 'fonts.zip'
    destination = os.path.join(font_path, save_dir)
    download_file_from_google_drive(link_id, destination)
    
    print('Extracting all the fonts...')
    try:
        with ZipFile(destination, 'r') as zip:
            # extracting all the files
            zip.extractall(font_path)
    except :
        os.system('unzip {}'.format(destination))    
    
    os.remove(destination)
    print('Using fonts from {} to generate training data.'.format(font_path))

def check_exist_and_download_fonts(font_path):
    if not (os.path.exists(font_path)):
        print('{} not fount!'.format(font_path))
        os.makedirs(font_path)
        
        download_font(font_path)
    elif len(os.listdir(font_path)) == 0:
        download_font(font_path)
        
        
# ====================
# helper functions		
# ====================

def download_file_from_google_drive(id, destination):
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value

        return None

    def save_response_content(response, destination):
        CHUNK_SIZE = 32768

        with open(destination, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)

    URL = "https://www.googleapis.com/drive/v3/files/{}?alt=media&key={}"
    api_key = 'AIzaSyCI1h7RXop1DlmTXRZUrletJNTIxzhnC24'

    session = requests.Session()

    response = session.get(URL.format(id, api_key), params = { }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    
        