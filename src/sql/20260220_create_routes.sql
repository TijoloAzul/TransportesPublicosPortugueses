-- Create table of routes
create table routes (
		id SERIAL PRIMARY KEY,
		code_route varchar(100) not null,
		id_operator int not null references operators(id),
		public_code varchar(100) not null,
		color varchar(10) not null,
 		name text not null,
 		created_at timestamp not null,
		updated_at timestamp not null,
		deleted boolean not null default false,
		constraint routes_code_route_id_operator_key unique (code_route, id_operator)
 );
