-- Create table of trips
create table trips (
         id SERIAL PRIMARY KEY,
         code_trip varchar(100) not null,
         id_operator int not null references operators(id),
         id_shape int not null references shapes(id),
         id_route int not null references routes(id),
         headsign varchar(100),
         public_code_route varchar(100) not null,
         color_route varchar(10) not null,
         name_route text not null,
         created_at timestamp not null,
         updated_at timestamp not null,
         deleted boolean not null default false,
         constraint trips_code_trip_id_operator_key unique (code_trip, id_operator)
  );
