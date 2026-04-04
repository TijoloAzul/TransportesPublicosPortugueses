def save_shapes(db, id_operator, shapes, points):

    disable_all(db, id_operator)
    delete_all_points(db, id_operator)

    for shape in shapes.itertuples():
        db.execute(f"""
            insert into shapes (code_shape, id_operator, public_code_route, color_route, name_route, created_at, updated_at, deleted) 
            values (%s, %s, %s, %s, %s, now(), now(), false)
            on conflict (code_shape, id_operator)
            do update set
                public_code_route = excluded.public_code_route,
                color_route = excluded.color_route,
                name_route = excluded.name_route,
                deleted = false,
                updated_at = now();
            """,
            (shape.Index, id_operator, shape.code, shape.color, shape.name))
    
    create_all_points(db, id_operator, points)
    
def create_all_points(db, id_operator, points):
    
    for point in points.itertuples():
        db.execute(f"""
                   insert into shape_points (id_shape, id_operator, idx, latitude, longitude, distance, created_at)
                   values ((select id from shapes where code_shape = %s and id_operator = %s), %s, %s, %s, %s, %s, now())
                   """,
                   (point.Index, id_operator, id_operator, point.idx, point.lat, point.lon, point.distance))
    
def disable_all(db, id_operator):
    db.execute(f"update shapes set deleted = true, updated_at = now() where id_operator = %s and deleted = false;",
        (str(id_operator)))
    
def delete_all_points(db, id_operator):
    db.execute("delete from shape_points where id_operator = %s;", 
               (str(id_operator)))