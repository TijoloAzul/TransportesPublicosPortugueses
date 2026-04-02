-- Create table of carris colors
create table carris_colors (
		id SERIAL PRIMARY KEY,
		code_route varchar(100) unique not null,
		color_route varchar(10) not null,
        created_at timestamp not null
 );
