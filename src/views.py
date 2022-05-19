import aiofiles.os
from flask_login import login_user
from werkzeug.exceptions import NotFound
from flask import (render_template, send_from_directory, redirect,
                   url_for, Blueprint)
from flask_login import login_manager, login_required, logout_user
from core.config import BASE_DIR
from src.forms import SearchForm, SearchFormProduct, UploadForm, LoginForm
from src.users import User
from utils.async_funcs import fetch, fetch_file
from utils.choices import Response_type
from utils.data_models import HTTPResponse
from utils.form_utils import save_form_file
from werkzeug.security import generate_password_hash, check_password_hash


analog = Blueprint('analog', __name__,
                   template_folder=BASE_DIR / 'templates',
                   static_folder=BASE_DIR / 'static')


@analog.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.username.data).first()
        if not user or not check_password_hash(
                user.password_hash, form.password.data):
            return render_template(
                'login.html', form=form, message='name or password not valid')
        login_user(user, remember=form.data)
        return redirect(url_for('analog.index'))
    return render_template('login.html', form=form)


@analog.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('analog.index'))


@analog.route('/', methods=['GET', 'POST'])
async def index():
    template_name = 'index.html'
    form = SearchForm()
    if form.validate_on_submit():
        url = f'http://analoghub.servebeer.com/api/v1/analog/search_analog'
        query = {'query': form.search.data,
                 'search_type': form.search_type.data}
        response: HTTPResponse = await fetch(url, query)
        if response.status == 404:
            return render_template(template_name, form=form, not_found=True)
        return render_template(template_name, form=form, result=response.body)
    return render_template(template_name, form=form)


@analog.route('/search_product', methods=['GET', 'POST'])
async def search_product():
    form = SearchFormProduct()
    if form.validate_on_submit():
        url = f'http://analoghub.servebeer.com/api/v1/analog/search_product'
        query = {'query': form.search.data,
                 'search_type': form.search_type.data,
                 'maker': form.maker.data}
        response: HTTPResponse = await fetch(url, query)
        if response.status == 404:
            return render_template('search_product.html', form=form,
                                   not_found=True)
        return render_template('search_product.html', form=form,
                               result=response.body)
    return render_template('search_product.html', form=form)


@analog.route('/upload_xlsx', methods=['GET', 'POST'])
@login_required
async def upload_xlsx():
    form = UploadForm()
    if form.validate_on_submit():
        file_path, file_name = save_form_file(form)
        url = f'http://analoghub.servebeer.com/api/v1/analog/upload_analogs'
        response = await fetch_file(url, file_path, file_name, 'xlsx_file')
        await aiofiles.os.remove(file_path)
        return {'response': response.status, 'detail': response.body}
    return render_template('upload_xlsx.html', form=form)


@analog.route('/upload_zip', methods=['GET', 'POST'])
@login_required
async def upload_zip():
    form = UploadForm()
    if form.validate_on_submit():
        file_path, file_name = save_form_file(form)
        url = f'http://analoghub.servebeer.com/api/v1/analog/upload_makers'
        response = await fetch_file(url, file_path, file_name, 'zip_file')
        await aiofiles.os.remove(file_path)
        return render_template(
            'upload_zip.html', form=form, result=response.body)
    return render_template('upload_zip.html', form=form)


@analog.route('/search_analogs_list', methods=['GET', 'POST'])
async def search_analogs_list():
    form = UploadForm()
    if form.validate_on_submit():
        file_path, file_name = save_form_file(form)
        url = f'http://analoghub.servebeer.com/api/v1/analog/search_list_analogs'
        response_file = await fetch_file(
            url, file_path, file_name, 'xlsx_file', Response_type.Xlsx)
        await aiofiles.os.remove(file_path)
        return render_template(
            'search_analog_list.html', form=form, resonse_file=response_file)
    return render_template('search_analog_list.html', form=form)


@analog.route('/get_file/<string:file_name>', methods=['GET'])
async def get_file(file_name: str):
    try:
        return send_from_directory(
            BASE_DIR.joinpath('static'), file_name, as_attachment=True)
    except NotFound as err:
        print(type(err))
        return {'fail': 'fail'}
