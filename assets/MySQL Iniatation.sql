CREATE DATABASE milestone4;
USE milestone4;



CREATE TABLE user(
	id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE,
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255),
    created_at DATETIME,
    updated_at DATETIME
);

CREATE TABLE accounts(
	id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES user(id),
    account_type VARCHAR(255),
    account_number VARCHAR(255) UNIQUE,
    balance DECIMAL(10, 2),
    created_at DATETIME,
    updated_at DATETIME
);

CREATE TABLE transactions(
	id INT AUTO_INCREMENT PRIMARY KEY,
    from_account_id INT,
    FOREIGN KEY (from_account_id) REFERENCES accounts(id),
    to_account_id INT,
    FOREIGN KEY (to_account_id) REFERENCES accounts(id),
    amount DECIMAL(10, 2),
    type VARCHAR(255),
    description VARCHAR(255),
    created_at DATETIME
);

SELECT * FROM user;
SELECT * FROM accounts;
SELECT * FROM transactions;