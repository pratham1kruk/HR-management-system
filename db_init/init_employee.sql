-- Create employee table
CREATE TABLE IF NOT EXISTS employee (
    emp_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    dob DATE,
    gender VARCHAR(10),
    email VARCHAR(100),
    phone VARCHAR(20),
    hire_date DATE DEFAULT CURRENT_DATE
);

-- Create professional_info table
CREATE TABLE IF NOT EXISTS professional_info (
    emp_id INT PRIMARY KEY REFERENCES employee(emp_id),
    designation VARCHAR(100),
    department VARCHAR(100),
    current_salary NUMERIC(10,2),
    previous_salary NUMERIC(10,2)
);

-- Insert sample employees (basic info only)
INSERT INTO employee (
    first_name, last_name, dob, gender, email, phone, hire_date
) VALUES
(
    'Ananya', 'Sharma', '1990-06-15', 'Female', 'ananya.sharma@example.com', '+91-9876543210', '2020-01-01'
),
(
    'Rohit', 'Verma', '1988-12-10', 'Male', 'rohit.verma@example.com', '+91-8888888888', '2019-05-15'
);

-- Insert their professional_info
INSERT INTO professional_info (
    emp_id, designation, department, current_salary, previous_salary
) VALUES
(
    1, 'Senior Analyst', 'Finance', 85000.00, 80000.00
),
(
    2, 'Team Lead', 'Engineering', 95000.00, 90000.00
);
