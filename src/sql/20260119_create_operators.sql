-- Create table of operators
create table operators (
		id SERIAL PRIMARY KEY,
		code varchar(100) unique not null,
 		name text not null,
 		created_at timestamp not null
 );

-- Create table of operator sources
create table operator_sources (
		id SERIAL PRIMARY KEY,
		id_operator int not null references operators(id),
		url text,
		created_at timestamp not null,
		downloaded_at timestamp
);