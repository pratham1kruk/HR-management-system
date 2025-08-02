CREATE TABLE IF NOT EXISTS employee (
    emp_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    dob DATE,
    gender VARCHAR(10),
    hire_date DATE,
    designation VARCHAR(100),
    department VARCHAR(100),
    current_salary NUMERIC(10,2),
    previous_salary NUMERIC(10,2)
);
