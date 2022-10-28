create table users
(
	id varchar(15) not null,
	password varchar(20) not null,
	primary key (id)
);


create table category
(
	code varchar(2) not null,
	type varchar(20) not null,
	primary key (code)
);

create table items
(
	code varchar(2) not null,
	name varchar(20) not null,
	price int not null check (price>=0),
	stock int not null check (stock>0),
	seller varchar(15) not null,
	primary key (code, name, price, seller),
	foreign key (code) references category (code),
	foreign key (seller) references users (id)
);

create table trades
(
	buyer varchar(15) not null,
	seller varchar(15) not null,
	code varchar(2) not null,
	trade_price int null check (trade_price>=0),
	foreign key (buyer) references users (id),
	foreign key (seller) references users (id),
	foreign key (code) references category (code)
);

create table rating_info
(
	rating varchar(10) not null,
	condition int not null check (condition>=0),
	discount numeric(4,2) not null check (100>discount and discount>=0),
	primary key (rating)
);

create table account
(
	id varchar(15) not null,
	balance int not null check (balance>=0), 
	rating varchar(10) not null,
	primary key (id),
	foreign key (id) references users (id),
	foreign key (rating) references rating_info (rating)	
);

INSERT INTO users VALUES('admin', '0000');
INSERT INTO users VALUES('postgres', 'dbdb');

INSERT INTO category VALUES('00', 'books');
INSERT INTO category VALUES('01', 'electronics');
INSERT INTO category VALUES('02', 'clothing');

INSERT INTO rating_info VALUES('gold', 500000, 2.5);
INSERT INTO rating_info VALUES('silver', 100000, 1);
INSERT INTO rating_info VALUES('bronze', 50000, 0.5);
INSERT INTO rating_info VALUES('beginner', 0, 0);

INSERT INTO account VALUES('admin', 10000000, 'gold');
INSERT INTO account VALUES('postgres', 75000, 'bronze');

INSERT INTO items VALUES('00', 'Database', 1000, 10, 'admin');

INSERT INTO trades VALUES('postgres', 'admin', '01', 1000);
