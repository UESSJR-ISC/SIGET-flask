
import os 


ADMIN_ID = 'root'
ADMIN_PASSW = 'toor'

STATIC_URL_PATH = ''

if not "DOCKER" in os.environ:
    STATIC_FOLDER = 'static'

else:
    STATIC_FOLDER = '/siget-vol/static'

IMG_FOLDER = STATIC_FOLDER + '/img'

FOTOS_GENERACIONALES = IMG_FOLDER + '/generacion/'
FOTOS_EGRESADOS = IMG_FOLDER + '/egresado/'
FOTOS_BLOG = IMG_FOLDER + '/blog/'
MANUALES_MODALIDADES = STATIC_FOLDER + '/manual/'
FICHEROS_ADJUNTOS = STATIC_FOLDER + '/adjuntos/'

def check_folder_existance(path):
    if not os.path.isdir(path):
        os.makedirs(path)

check_folder_existance(STATIC_FOLDER)
check_folder_existance(IMG_FOLDER)
check_folder_existance(FOTOS_GENERACIONALES)
check_folder_existance(FOTOS_EGRESADOS)
check_folder_existance(FOTOS_BLOG)
check_folder_existance(MANUALES_MODALIDADES)
check_folder_existance(FICHEROS_ADJUNTOS)

SESSION_TYPE = 'filesystem'
SECRET_KEY = 'dmo5S4DxuD^9IWK1k33o7Xg88J&D8fq!'
ALLOWED_IMAGE_TYPES = ['png', 'jpg', 'jpeg', 'gif']
ALLOWED_DOC_TYPES = ['pdf', 'doc', 'docx']