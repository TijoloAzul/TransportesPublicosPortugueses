def get_color(db, code):
    result = db.select(f"select color_route from carris_colors where code_route = '{code}';")
    
    if len(result) == 0:
        return None
    else:
        return result[0][0]

def set_color(db, code, color):
    db.execute(f"""
        insert into carris_colors (
            code_route, 
            color_route, 
            created_at) 
        values (%s, %s, now())""",
        (code, color))