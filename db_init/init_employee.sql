CREATE TABLE IF NOT EXISTS employee (
    emp_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    dob DATE,
    gender VARCHAR(10),
    hire_date DATE,
    email VARCHAR(120) UNIQUE,
    phone VARCHAR(15),
    designation VARCHAR(100),
    department VARCHAR(100),
    current_salary NUMERIC(10,2),
    previous_salary NUMERIC(10,2)
);
