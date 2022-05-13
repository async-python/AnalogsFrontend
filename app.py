from datetime import datetime
from pathlib import Path

import aiofiles.os
from flask import Flask, render_template
from flask_bootstrap import Bootstrap4
from werkzeug.datastructures import FileStorage

from core.config import Config
from forms import SearchForm, SearchFormProduct, UploadForm
from utils.async_funcs import fetch, fetch_file
from utils.data_models import HTTPResponse

app = Flask(__name__)
bootstrap = Bootstrap4(app)
app.config.from_object(Config)

BASE_DIR = Path(__file__).resolve(strict=True).parent


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
        file: FileStorage = form.file.data
        file_name = file.filename
        file_path = str(BASE_DIR / f'static/{file_name}')
        file.save(file_path)
        url = f'http://analoghub.servebeer.com/api/v1/analog/upload_analogs'
        response = await fetch_file(url, file_path, file_name, 'xlsx_file')
        await aiofiles.os.remove(file_path)
        return {'response': response.status, 'detail': response.body}
    return render_template('upload_xlsx.html', form=form)


@app.route('/upload_zip', methods=['GET', 'POST'])
async def upload_zip():
    form = UploadForm()
    if form.validate_on_submit():
        file: FileStorage = form.file.data
        file_name = file.filename
        file_path = str(BASE_DIR / f'static/{file_name}')
        file.save(file_path)
        url = f'http://analoghub.servebeer.com/api/v1/analog/upload_makers'
        response = await fetch_file(url, file_path, file_name, 'zip_file')
        await aiofiles.os.remove(file_path)
        return {'response': response.status, 'detail': response.body}
    return render_template('upload_zip.html', form=form)

if __name__ == '__main__':
    app.run()
