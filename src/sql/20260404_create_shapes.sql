-- Create table of stops
create table shapes (
		id SERIAL PRIMARY KEY,
		code_shape varchar(100) not null,
		id_operator int not null references operators(id),
		public_code_route varchar(100) not null,
		color_route varchar(10) not null,
 		name_route text not null,
 		created_at timestamp not null,
		updated_at timestamp not null,
		deleted boolean not null default false,
		constraint shapes_code_shape_id_operator_key unique (code_shape, id_operator)
 );

create table shape_points (
    id BIGSERIAL PRIMARY KEY,
    id_shape int not null references shapes(id),
    id_operator int not null references operators(id),
    idx int not null,
    latitude float not null,
    longitude float not null,
    distance float not null,
    created_at timestamp not null
);