from datetime import datetime

import aiofiles.os
from werkzeug.exceptions import NotFound
from flask import Flask, render_template, send_from_directory
from flask_bootstrap import Bootstrap4

from core.config import Config, BASE_DIR
from forms import SearchForm, SearchFormProduct, UploadForm
from utils.async_funcs import fetch, fetch_file
from utils.choices import Response_type
from utils.data_models import HTTPResponse
from utils.form_utils import save_form_file

app = Flask(__name__)
bootstrap = Bootstrap4(app)
app.config.from_object(Config)


@app.context_processor
def year_processor():
    year = datetime.now().year
    return dict(year=year)


@app.route('/', methods=['GET', 'POST'])
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


@app.route('/search_product', methods=['GET', 'POST'])
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


@app.route('/upload_xlsx', methods=['GET', 'POST'])
async def upload_xlsx():
    form = UploadForm()
    if form.validate_on_submit():
        file_path, file_name = save_form_file(form)
        url = f'http://analoghub.servebeer.com/api/v1/analog/upload_analogs'
        response = await fetch_file(url, file_path, file_name, 'xlsx_file')
        await aiofiles.os.remove(file_path)
        return {'response': response.status, 'detail': response.body}
    return render_template('upload_xlsx.html', form=form)


@app.route('/upload_zip', methods=['GET', 'POST'])
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


@app.route('/search_analogs_list', methods=['GET', 'POST'])
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


@app.route('/get_file/<string:file_name>', methods=['GET'])
async def get_file(file_name: str):
    try:
        return send_from_directory(
            BASE_DIR.joinpath('static'), file_name, as_attachment=True)
    except NotFound as err:
        print(type(err))
        return {'fail': 'fail'}


if __name__ == '__main__':
    app.run()
