import pandas as pd

def save_trips(db, id_operator, trips):
    
    disable_all(db, id_operator)

    routes = get_routes_with_ids(db, id_operator)
    shapes = get_shapes_with_ids(db, id_operator)
    
    to_save = pd.merge(
        pd.merge(trips, routes, left_on='route', right_index=True),
        shapes,
        left_on='shape',
        right_index=True)
        
    data = [(trip.Index, id_operator, trip.id_shape, trip.id_route, clean(trip.headsign), trip.code_route, trip.color_route, trip.name_route) for trip in to_save.itertuples()]
    
    db.execute_many(f"""
        insert into trips (code_trip, id_operator, id_shape, id_route, headsign, public_code_route, color_route, name_route, created_at, updated_at, deleted) 
        values %s
        on conflict (code_trip, id_operator)
        do update set
            id_shape = excluded.id_shape,
            id_route = excluded.id_route,
            headsign = excluded.headsign,
            public_code_route = excluded.public_code_route,
            color_route = excluded.color_route,
            name_route = excluded.name_route,
            deleted = false,
            updated_at = now();
        """, 
        data, 
        template="(%s, %s, %s, %s, %s, %s, %s, %s, now(), now(), false)")

def disable_all(db, id_operator):
    db.execute(f"update trips set deleted = true, updated_at = now() where id_operator = %s and deleted = false;",
        (str(id_operator)))
    
def get_routes_with_ids(db, id_operator):
    routes = db.select(f"select id, code_route from routes where id_operator = {id_operator} and deleted = False;")
    return pd.DataFrame(routes, columns=['id_route', 'code_route']).set_index('code_route')

def get_shapes_with_ids(db, id_operator):
    shapes = db.select(f"select id, code_shape from shapes where id_operator = {id_operator} and deleted = False;")
    return pd.DataFrame(shapes, columns=['id_shape', 'code_shape']).set_index('code_shape')

def clean(val):
    return None if pd.isna(val) else val

def read_trips(db, id_operator):
    stops = db.select(f"""
              select code_trip, headsign, public_code_route, color_route, name_route
              from trips
              where id_operator = {id_operator}
                and deleted = false
              """);
    
    return pd.DataFrame(stops, columns=['code', 'headsign', 'code_route', 'color_route', 'name_route'])