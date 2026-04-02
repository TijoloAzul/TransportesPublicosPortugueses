def get_operators(db):
    result = db.select("select id, code, name from operators;")
    return [{'id': r[0], 'code': r[1], 'name': r[2]} for r in result]

def get_operator_map(db):
    operators = get_operators(db)
    result = dict()
    for operator in operators:
        result[operator['code']] = operator
    return result

def get_source_url(db, operator):
    result = db.select(f"select id, url from operator_sources where id_operator = {str(operator['id'])};")
    if len(result) != 1:
        raise Exception('Deveria ter uma e só uma fonte de dados')
    return {'id': result[0][0], 'url': result[0][1]}

def set_operator_source_downloaded(db, operator):
    db.execute(f"update operator_sources set downloaded_at = now() where id_operator = {str(operator['id'])};")