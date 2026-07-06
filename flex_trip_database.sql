create database flextrip;
use flextrip;

create table users(
  id int auto_increment primary key,
  username varchar(50) not null unique,
  email varchar(100) not null unique,
  bio varchar(500) default '',
  password varchar(255) not null,
  profile_url  VARCHAR(500),
  profile_public_id  VARCHAR(255),
  created_at timestamp default current_timestamp
  );
  
create table trip(
   trip_id int auto_increment primary key,
   user_id int not null,
   title varchar(100) not null,
   description text,
   thumbnail_url VARCHAR(500),
   thumbnail_public_id VARCHAR(255),
   is_complete boolean default false,
   created_at timestamp default current_timestamp,
   foreign key (user_id) references users(id) on delete cascade
);

create table trip_stops(
    trip_id int ,
    sequence_number int,
    stop_name varchar(50) not null,
    description text,
    latitude decimal(9,6) null,
    longitude decimal(9,6) null,
    photo_url  VARCHAR(500),
    photo_public_id VARCHAR(255),
    primary key(trip_id,sequence_number),
    foreign key (trip_id) references trip(trip_id) on delete cascade
);

create table gallary(
    trip_id int,
    sequence_number int,
    image_url  VARCHAR(500),
	image_public_id VARCHAR(255),
    primary key(trip_id,sequence_number),
    foreign key(trip_id) references trip(trip_id) on delete cascade
);

create table likes(
    user_id int,
    trip_id int,
    primary key (user_id,trip_id),
    foreign key (user_id) references users(id) on delete cascade,
    foreign key (trip_id) references trip(trip_id) on delete cascade
);

create table comments(
    comment_id int primary key auto_increment,
    user_id int,
    trip_id int,
    comment varchar(1000),
    created_at timestamp default current_timestamp,
    foreign key (user_id) references users(id) on delete cascade,
    foreign key (trip_id) references trip(trip_id) on delete cascade
);