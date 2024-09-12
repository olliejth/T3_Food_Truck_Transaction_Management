-- This file should contain table definitions for the database.

SET search_path TO oliver_thompson_schema;

DROP TABLE IF EXISTS FACT_Transaction;
DROP TABLE IF EXISTS DIM_Payment_Method;
DROP TABLE IF EXISTS DIM_Truck;

CREATE TABLE DIM_Truck (
    truck_id SMALLINT PRIMARY KEY UNIQUE NOT NULL,
    truck_name TEXT UNIQUE NOT NULL,
    truck_description TEXT,
    has_card_reader BOOLEAN,
    fsa_rating SMALLINT
);

CREATE TABLE DIM_Payment_Method (
    payment_method_id SMALLINT PRIMARY KEY UNIQUE NOT NULL,
    payment_method VARCHAR(6) UNIQUE NOT NULL
);

CREATE TABLE FACT_Transaction(
    transaction_id BIGINT PRIMARY KEY UNIQUE NOT NULL GENERATED ALWAYS AS IDENTITY,
    truck_id SMALLINT NOT NULL,
    payment_method_id SMALLINT NOT NULL,
    total INT,
    at TIMESTAMP,
    FOREIGN KEY (truck_id) REFERENCES DIM_Truck (truck_id),
    FOREIGN KEY (payment_method_id) REFERENCES DIM_Payment_Method (payment_method_id)
);


INSERT INTO DIM_Truck 
(truck_id, truck_name, truck_description, has_card_reader, fsa_rating)
VALUES
(1, 'Burrito Madness', 'An authentic taste of Mexico.', True, 4),
(2, 'Kings of Kebabs', 'Locally-sourced meat cooked over a charcoal grill.', True, 2),
(3, 'Cupcakes by Michelle', 'Handcrafted cupcakes made with high-quality, organic ingredients.', True, 5),
(4, 'Hartmann''s Jellied Eels', 'A taste of history with this classic English dish.', True, 4),
(5, 'Yoghurt Heaven', 'All the great tastes, but only some of the calories!', True, 4),
(6, 'SuperSmoothie', 'Pick any fruit or vegetable, and we''ll make you a delicious, healthy, multi-vitamin shake. Live well; live wild.', False, 3);


INSERT INTO DIM_Payment_Method
(payment_method_id, payment_method)
VALUES
(1, 'cash'),
(2, 'card');