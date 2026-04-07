import pandas as pd

def save_shapes(db, id_operator, shapes, points):

    disable_all(db, id_operator)
    delete_all_points(db, id_operator)
    
    data = [(shape.Index, id_operator, shape.code, shape.color, shape.name) for shape in shapes.itertuples()]

    db.execute_many(f"""
        insert into shapes (code_shape, id_operator, public_code_route, color_route, name_route, created_at, updated_at, deleted) 
        values %s
        on conflict (code_shape, id_operator)
        do update set
            public_code_route = excluded.public_code_route,
            color_route = excluded.color_route,
            name_route = excluded.name_route,
            deleted = false,
            updated_at = now();
        """, 
        data, 
        template="(%s, %s, %s, %s, %s, now(), now(), false)")
    
    shapes_with_ids = get_shapes_with_ids(db, id_operator)
    points_to_save = pd.merge(points, shapes_with_ids, left_index=True, right_index=True)
    
    save_points(db, id_operator, points_to_save)
    
def save_points(db, id_operator, points):
    
    data = [(point.id_shape, id_operator, point.idx, point.lat, point.lon, point.distance) for point in points.itertuples()]
    
    db.execute_many(f"""
        insert into shape_points (id_shape, id_operator, idx, latitude, longitude, distance, created_at)
        values %s ;
        """,
        data,
        template = "(%s, %s, %s, %s, %s, %s, now())")
    
def read_shapes(db, id_operator):
    shapes = db.select(f"""
        select id, code_shape, public_code_route, color_route, name_route
        from shapes
        where id_operator = {id_operator}
        and deleted = false
        """);
    
    return pd.DataFrame(shapes, columns=['id', 'code', 'code_route', 'color', 'name'])

def read_points(db, id_operator):
    points = db.select(f"""
        select id_shape, idx, latitude, longitude, distance
        from shape_points
        where id_operator = {id_operator}
        """);
    
    return pd.DataFrame(points, columns=['id_shape', 'idx', 'lat', 'lon', 'distance'])
    
def disable_all(db, id_operator):
    db.execute(f"update shapes set deleted = true, updated_at = now() where id_operator = %s and deleted = false;",
        (str(id_operator)))

def get_shapes_with_ids(db, id_operator):
    shapes = db.select(f"select id, code_shape from shapes where id_operator = {id_operator} and deleted = False;")
    return pd.DataFrame(shapes, columns=['id_shape', 'code_shape']).set_index('code_shape')
    
def delete_all_points(db, id_operator):
    db.execute("delete from shape_points where id_operator = %s;", 
               (str(id_operator)))