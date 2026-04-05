def save_routes(db, id_operator, routes):

    disable_all(db, id_operator)
    
    data = [(route.Index, id_operator, route.code, route.color, route.name) for route in routes.itertuples()]

    db.execute_many(f"""
        insert into routes (code_route, id_operator, public_code, color, name, created_at, updated_at, deleted) 
        values %s
        on conflict (code_route, id_operator)
        do update set
            public_code = excluded.public_code,
            color = excluded.color,
            name = excluded.name,
            deleted = false,
            updated_at = now();
        """,
        data,
        template="(%s, %s, %s, %s, %s, now(), now(), false)")
    
def disable_all(db, id_operator):
    db.execute(f"update routes set deleted = true, updated_at = now() where id_operator = %s and deleted = false",
        (str(id_operator)))