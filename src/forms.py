from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import RadioField, SearchField, SelectField, SubmitField, StringField, PasswordField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    search = SearchField(label='Поиск', validators=[DataRequired()])
    search_type = RadioField(
        'Тип поиска', [DataRequired()],
        choices=[('string_search', 'точный поиск'),
                 ('ngram_search', 'неточный поиск')],
        default='ngram_search')
    submit = SubmitField(label='Найти')


class SearchFormProduct(SearchForm):
    maker = SelectField(
        'Тип поиска', [DataRequired()],
        choices=['ALL', 'PALBIT', 'YG-1', 'VERGNANO', 'VARGUS', 'SANHOG',
                 'OMAP', 'NANOLOY', 'LIKON', 'HORN', 'HELION',
                 'GABRIEL_MAUVAIS', 'FRESAL', 'DEREK', 'BRICE', 'Bribase',
                 'ASKUP', 'ILIX'],
        default='ALL')


class UploadForm(FlaskForm):
    file = FileField(validators=[FileRequired()])


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField()
