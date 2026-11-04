-- EcoCollect | MySQL 8.4 | InnoDB / utf8mb4

CREATE DATABASE IF NOT EXISTS ecocollect CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE ecocollect;

CREATE TABLE ewaste_categories (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(100) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
) ENGINE=InnoDB;

CREATE TABLE recycling_centres (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(100) NOT NULL, 
	address VARCHAR(500) NOT NULL, 
	phone VARCHAR(30) NOT NULL, 
	active BOOL NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
) ENGINE=InnoDB;

CREATE TABLE users (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(100) NOT NULL, 
	email VARCHAR(254) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	`role` VARCHAR(10) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_user_role CHECK (role IN ('user','admin')), 
	UNIQUE (email)
) ENGINE=InnoDB;

CREATE TABLE collection_requests (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	user_id INTEGER NOT NULL, 
	centre_id INTEGER, 
	address VARCHAR(500) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	pickup_date DATE, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_request_status CHECK (status IN ('Pending','Scheduled','Collected','Recycled')), 
	CONSTRAINT ck_request_schedule CHECK (status = 'Pending' OR (centre_id IS NOT NULL AND pickup_date IS NOT NULL)), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE RESTRICT, 
	FOREIGN KEY(centre_id) REFERENCES recycling_centres (id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE INDEX ix_collection_requests_centre_id ON collection_requests (centre_id);

CREATE INDEX ix_collection_requests_status ON collection_requests (status);

CREATE INDEX ix_collection_requests_user_id ON collection_requests (user_id);

CREATE TABLE request_items (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	request_id INTEGER NOT NULL, 
	category_id INTEGER NOT NULL, 
	`condition` VARCHAR(20) NOT NULL, 
	quantity INTEGER NOT NULL, 
	estimated_weight NUMERIC(10, 2) NOT NULL, 
	actual_weight NUMERIC(10, 2), 
	PRIMARY KEY (id), 
	CONSTRAINT ck_item_quantity CHECK (quantity > 0), 
	CONSTRAINT ck_estimated_weight CHECK (estimated_weight > 0), 
	CONSTRAINT ck_actual_weight CHECK (actual_weight IS NULL OR actual_weight > 0), 
	CONSTRAINT ck_item_condition CHECK (`condition` IN ('Working','Damaged','Non-functional')), 
	FOREIGN KEY(request_id) REFERENCES collection_requests (id) ON DELETE CASCADE, 
	FOREIGN KEY(category_id) REFERENCES ewaste_categories (id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE INDEX ix_request_items_request_id ON request_items (request_id);

CREATE TABLE status_history (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	request_id INTEGER NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	changed_by INTEGER NOT NULL, 
	changed_at DATETIME NOT NULL, 
	note VARCHAR(500) NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_history_status CHECK (status IN ('Pending','Scheduled','Collected','Recycled')), 
	FOREIGN KEY(request_id) REFERENCES collection_requests (id) ON DELETE CASCADE, 
	FOREIGN KEY(changed_by) REFERENCES users (id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE INDEX ix_status_history_request_id ON status_history (request_id);
