
from wtforms import Form, StringField, SelectField

# A small class for the Search bar in the frontend app. 

class MusicSearchForm(Form):
    
    search = StringField('')