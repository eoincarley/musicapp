
from wtforms import Form, StringField, SelectField

class MusicSearchForm(Form):
    
    search = StringField('')