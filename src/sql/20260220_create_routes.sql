-- Create table of routes
create table routes (
		id SERIAL PRIMARY KEY,
		id_route varchar(100) not null,
		id_operator int not null references operators(id),
		code varchar(100) not null,
		color varchar(10) not null,
 		name text not null,
 		created_at timestamp not null,
		updated_at timestamp not null,
		deleted boolean not null default false,
		constraint routes_id_route_id_operator_key unique (id_route, id_operator)
 );
