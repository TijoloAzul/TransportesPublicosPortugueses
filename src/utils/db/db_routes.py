from datetime import datetime 

def save_routes(db, id_operator, routes):

    disable_all(db, id_operator)

    for route in routes.itertuples():
        db.execute(f"""
            insert into routes (id_route, id_operator, code, color, name, created_at, updated_at, deleted) 
            values (%s, %s, %s, %s, %s, now(), now(), false)
            on conflict (id_route, id_operator)
            do update set
                code = excluded.code,
                color = excluded.color,
                name = excluded.name,
                deleted = false,
                updated_at = now();
            """,
            (route.Index, id_operator, route.code, route.color, route.name))
    
def disable_all(db, id_operator):
    db.execute(f"update routes set deleted = true, updated_at = now() where id_operator = %s and deleted = false",
        (str(id_operator)))