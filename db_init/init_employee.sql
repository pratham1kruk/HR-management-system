-- Create employee table
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

-- Insert sample employees with professional data

INSERT INTO employee (
    first_name, last_name, dob, gender, hire_date,
    designation, department, current_salary, previous_salary
) VALUES
(
    'Ananya', 'Sharma', '1990-06-15', 'Female', '2020-01-01',
    'Senior Analyst', 'Finance', 85000.00, 80000.00
),
(
    'Rohit', 'Verma', '1988-12-10', 'Male', '2019-05-15',
    'Team Lead', 'Engineering', 95000.00, 90000.00
);
