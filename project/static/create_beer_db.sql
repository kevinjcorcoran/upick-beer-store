CREATE TABLE IF NOT EXISTS Brewery(
	id INTEGER,
	brewery_name VARCHAR(200) NOT NULL,
	street VARCHAR(50),
	city VARCHAR(30),
	state CHAR(2),
	zip NUMERIC(5),
	PRIMARY KEY(id),
    CHECK(id>=0 AND zip>=0)
);

CREATE TABLE IF NOT EXISTS Style(
	style_name VARCHAR(200),
	flavor VARCHAR(30),
	color VARCHAR(30),
	PRIMARY KEY(style_name)
);

CREATE TABLE IF NOT EXISTS Beer(
	upc NUMERIC(12),
	beer_name VARCHAR(200) NOT NULL,
	brewery_id INTEGER NOT NULL,
	style VARCHAR(200) NOT NULL,
	abv DECIMAL(4,2),
	ibu NUMERIC(3),
	stock INTEGER NOT NULL,
	price DECIMAL(18,2) NOT NULL,
	PRIMARY KEY(upc),
	FOREIGN KEY(brewery_id) REFERENCES Brewery(id) ON DELETE CASCADE,
	CHECK(
		upc>=0 AND brewery_id>=0 AND
        abv<=100 AND abv>=0 AND
        ibu>=5 AND ibu<=120 AND 
        stock>=0 AND price>=0
	)
);

CREATE TABLE IF NOT EXISTS Customer(
	email VARCHAR(320),
	password VARCHAR(500),
	first_name VARCHAR(200),
	last_name VARCHAR(200),
	street VARCHAR(50),
	city VARCHAR(30),
	state CHAR(2),
	zip NUMERIC(5),
	favorite_style VARCHAR(200),
    PRIMARY KEY(email),
    FOREIGN KEY(favorite_style) REFERENCES Style(style_name) ON DELETE CASCADE,
    CHECK(zip>=0)
);

CREATE TABLE IF NOT EXISTS Purchase(
	id INTEGER,
    customer_email VARCHAR(320) NOT NULL,
    closed_date DATETIME,
    total DECIMAL(18,2),
    PRIMARY KEY(id),
    FOREIGN KEY(customer_email) REFERENCES Customer(email) ON DELETE CASCADE ON UPDATE CASCADE,
    CHECK(id>=0 AND total>=0 AND id>=0)
);

CREATE TABLE IF NOT EXISTS Purchase_Item(
	purchase_id INTEGER,
    beer_upc NUMERIC(12),
    quantity INTEGER NOT NULL,
    PRIMARY KEY(purchase_id, beer_upc),
    FOREIGN KEY (purchase_id) REFERENCES Purchase(id) ON DELETE CASCADE,
    FOREIGN KEY(beer_upc) REFERENCES Beer(upc) ON DELETE CASCADE,
    CHECK(purchase_id>=0 AND beer_upc>=0 AND quantity>=0)
);

CREATE TABLE IF NOT EXISTS likes(
	customer_email VARCHAR(320),
	beer_upc NUMERIC(12),
    PRIMARY KEY(customer_email, beer_upc),
    FOREIGN KEY(customer_email) REFERENCES Customer(email) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY(beer_upc) REFERENCES Beer(upc) ON DELETE CASCADE,
    CHECK(beer_upc>=0)
);
