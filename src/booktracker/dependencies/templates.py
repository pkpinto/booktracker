import os
from fastapi.templating import Jinja2Templates


templates_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'templates')
templates = Jinja2Templates(directory=templates_folder)
