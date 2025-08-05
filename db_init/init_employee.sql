-- Drop existing tables
DROP TABLE IF EXISTS salary_log;
DROP TABLE IF EXISTS professional_info;
DROP TABLE IF EXISTS employee;

-- 1. Create employee table
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

-- 2. Create professional_info table with extended fields
CREATE TABLE IF NOT EXISTS professional_info (
    emp_id INT PRIMARY KEY REFERENCES employee(emp_id),
    department VARCHAR(100),
    designation VARCHAR(100),
    experience INT,
    salary NUMERIC(10,2),
    last_increment NUMERIC(10,2),
    skills TEXT[],
    performance_rating INT CHECK (performance_rating BETWEEN 1 AND 5)
);

-- 3. Create salary_log for triggers
CREATE TABLE IF NOT EXISTS salary_log (
    log_id SERIAL PRIMARY KEY,
    emp_id INT REFERENCES employee(emp_id),
    old_salary NUMERIC,
    new_salary NUMERIC,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    action TEXT DEFAULT 'update',
    deleted_at TIMESTAMP
);

-- 4. Insert sample employees
INSERT INTO employee (
    first_name, last_name, dob, gender, email, phone, hire_date
) VALUES
('Ananya', 'Sharma', '1990-06-15', 'Female', 'ananya.sharma@example.com', '9876543210', '2020-01-01'),
('Rohit', 'Verma', '1988-12-10', 'Male', 'rohit.verma@example.com', '9999999999', '2019-05-15'),
('Isha', 'Mehta', '1995-03-25', 'Female', 'isha.mehta@example.com', '8888888888', '2021-06-12');

-- 5. Insert sample professional_info
INSERT INTO professional_info (
    emp_id, department, designation, experience, salary, last_increment, skills, performance_rating
) VALUES
(1, 'Finance', 'Senior Analyst', 5, 85000.00, 5000.00, ARRAY['Excel', 'Risk Analysis'], 3),
(2, 'Engineering', 'Team Lead', 6, 95000.00, 6000.00, ARRAY['Python', 'System Design'], 4),
(3, 'HR', 'Recruiter', 2, 55000.00, 3000.00, ARRAY['Recruitment', 'Compliance'], 5);
