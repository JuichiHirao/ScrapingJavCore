from src import site
from src import common
from src import db

parser = common.ImportParser()

import_dao = db.import_dao.ImportDao()
imports = import_dao.get_where_agreement('WHERE id = 4558')
# imports = import_dao.get_where_agreement('WHERE id = 2948')

if imports is not None:
    import_data = imports[0]
    print('filename : ' + parser.get_filename(import_data) + '')
