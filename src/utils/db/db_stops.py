from datetime import datetime 

def save_stops(db, id_operator, stops):

    disable_all(db, id_operator)

    for stop in stops.itertuples():
        db.execute(f"""
            insert into stops (id_stop, id_operator, name, latitude, longitude, created_at, updated_at, deleted) 
            values (%s, %s, %s, %s, %s, now(), now(), false)
            on conflict (id_stop, id_operator)
            do update set
                name = excluded.name, 
                latitude = excluded.latitude,
                longitude = excluded.longitude,
                deleted = false,
                updated_at = now();
            """,
            (stop.Index, id_operator, stop.name, stop.lat, stop.lon))
    
def disable_all(db, id_operator):
    db.execute(f"update stops set deleted = true, updated_at = now() where id_operator = %s and deleted = false",
        (str(id_operator)))