CREATE TABLE properties (
    id SERIAL PRIMARY KEY,
    title TEXT,
    location TEXT,
    price_raw TEXT,
    price_value BIGINT,
    bhk INTEGER,
    bathrooms INTEGER,
    super_area_sqft INTEGER,
    carpet_area_sqft INTEGER
);
