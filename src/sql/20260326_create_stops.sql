-- Create table of stops
create table stops (
		id SERIAL PRIMARY KEY,
		id_stop varchar(100) not null,
		id_operator int not null references operators(id),
		name text not null,
		latitude float not null,
 		longitude float not null,
 		created_at timestamp not null,
		updated_at timestamp not null,
		deleted boolean not null default false,
		constraint stops_id_stop_id_operator_key unique (id_stop, id_operator)
 );
