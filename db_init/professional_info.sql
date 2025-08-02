-- professional_info.sql
-- Structure, views, triggers, functions, and performance tuning for employee professional info

-- 1. Create professional_info table
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

-- 2. Insert sample data
INSERT INTO professional_info (emp_id, department, designation, experience, salary, last_increment, skills, performance_rating)
VALUES 
(101, 'Engineering', 'Software Engineer', 3, 70000, 5000, ARRAY['Python', 'Flask'], 4),
(102, 'Marketing', 'SEO Analyst', 2, 55000, 3000, ARRAY['SEO', 'Analytics'], 2),
(103, 'HR', 'HR Manager', 5, 65000, 4000, ARRAY['Recruitment', 'Compliance'], 5);

-- 3. View: All employees with more than 3 years experience
CREATE OR REPLACE VIEW experienced_employees AS
SELECT e.emp_id, e.name, p.designation, p.experience, p.salary
FROM employee e
JOIN professional_info p ON e.emp_id = p.emp_id
WHERE p.experience > 3;

-- 4. Salary change logging
CREATE TABLE IF NOT EXISTS salary_log (
    log_id SERIAL PRIMARY KEY,
    emp_id INT REFERENCES employee(emp_id),
    old_salary NUMERIC,
    new_salary NUMERIC,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    action TEXT DEFAULT 'update',
    deleted_at TIMESTAMP
);

-- Trigger: log salary update
CREATE OR REPLACE FUNCTION log_salary_update() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.salary <> OLD.salary THEN
        INSERT INTO salary_log (emp_id, old_salary, new_salary)
        VALUES (OLD.emp_id, OLD.salary, NEW.salary);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_salary_update ON professional_info;

CREATE TRIGGER trg_salary_update
AFTER UPDATE ON professional_info
FOR EACH ROW
EXECUTE FUNCTION log_salary_update();

-- Trigger: log deletion
CREATE OR REPLACE FUNCTION log_professional_delete() RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO salary_log(emp_id, old_salary, new_salary, action, deleted_at)
    VALUES (OLD.emp_id, OLD.salary, NULL, 'delete', NOW());
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_log_delete ON professional_info;

CREATE TRIGGER trg_log_delete
BEFORE DELETE ON professional_info
FOR EACH ROW
EXECUTE FUNCTION log_professional_delete();

-- 5. Function: Return highest salary
CREATE OR REPLACE FUNCTION get_highest_salary() RETURNS NUMERIC AS $$
BEGIN
    RETURN (SELECT MAX(salary) FROM professional_info);
END;
$$ LANGUAGE plpgsql;

-- 6. Function: Count of employees in a department
CREATE OR REPLACE FUNCTION count_in_department(dept VARCHAR) RETURNS INT AS $$
BEGIN
    RETURN (SELECT COUNT(*) FROM professional_info WHERE department = dept);
END;
$$ LANGUAGE plpgsql;

-- 7. CTE: Departments with avg salary above overall avg
WITH dept_avg AS (
    SELECT department, AVG(salary) AS dept_avg_salary
    FROM professional_info
    GROUP BY department
), overall_avg AS (
    SELECT AVG(salary) AS overall_salary
    FROM professional_info
)
SELECT d.*
FROM dept_avg d, overall_avg o
WHERE d.dept_avg_salary > o.overall_salary;

-- 8. CASE statement usage
SELECT emp_id, department, salary,
    CASE 
        WHEN salary > 70000 THEN 'High'
        WHEN salary BETWEEN 50000 AND 70000 THEN 'Medium'
        ELSE 'Low'
    END AS salary_grade
FROM professional_info;

-- 9. LEAD & LAG
SELECT emp_id, salary, last_increment,
       LAG(salary) OVER (ORDER BY emp_id) AS previous_salary,
       LEAD(salary) OVER (ORDER BY emp_id) AS next_salary
FROM professional_info;

-- 10. RANK employees by salary
SELECT emp_id, salary,
       RANK() OVER (ORDER BY salary DESC) AS salary_rank
FROM professional_info;

-- 11. Running salary sum & avg
SELECT emp_id, salary,
       SUM(salary) OVER (ORDER BY emp_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_salary_sum,
       AVG(salary) OVER (ORDER BY emp_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_salary_avg
FROM professional_info;

-- 12. Add record
CREATE OR REPLACE FUNCTION add_professional_info(
    p_emp_id INT,
    p_department VARCHAR,
    p_designation VARCHAR,
    p_experience INT,
    p_salary NUMERIC,
    p_last_increment NUMERIC,
    p_skills TEXT[],
    p_rating INT
)
RETURNS TEXT AS $$
BEGIN
    INSERT INTO professional_info(emp_id, department, designation, experience, salary, last_increment, skills, performance_rating)
    VALUES (p_emp_id, p_department, p_designation, p_experience, p_salary, p_last_increment, p_skills, p_rating);
    RETURN 'New professional record inserted';
EXCEPTION
    WHEN unique_violation THEN
        RETURN 'Error: Employee already exists.';
    WHEN foreign_key_violation THEN
        RETURN 'Error: No such employee in employee table.';
END;
$$ LANGUAGE plpgsql;

-- 13. Update record
CREATE OR REPLACE FUNCTION update_professional_info(
    p_emp_id INT,
    p_department VARCHAR,
    p_designation VARCHAR,
    p_experience INT,
    p_salary NUMERIC,
    p_last_increment NUMERIC,
    p_skills TEXT[],
    p_rating INT
)
RETURNS TEXT AS $$
BEGIN
    UPDATE professional_info
    SET department = p_department,
        designation = p_designation,
        experience = p_experience,
        salary = p_salary,
        last_increment = p_last_increment,
        skills = p_skills,
        performance_rating = p_rating
    WHERE emp_id = p_emp_id;

    IF FOUND THEN
        RETURN 'Record updated';
    ELSE
        RETURN 'No such employee found';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 14. Delete record
CREATE OR REPLACE FUNCTION delete_professional_info(p_emp_id INT)
RETURNS TEXT AS $$
BEGIN
    DELETE FROM professional_info WHERE emp_id = p_emp_id;
    IF FOUND THEN
        RETURN 'Record deleted';
    ELSE
        RETURN 'No such employee found';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 15. Upsert record
CREATE OR REPLACE FUNCTION upsert_professional_info(
    p_emp_id INT,
    p_department VARCHAR,
    p_designation VARCHAR,
    p_experience INT,
    p_salary NUMERIC,
    p_last_increment NUMERIC,
    p_skills TEXT[],
    p_rating INT
)
RETURNS TEXT AS $$
BEGIN
    INSERT INTO professional_info (emp_id, department, designation, experience, salary, last_increment, skills, performance_rating)
    VALUES (p_emp_id, p_department, p_designation, p_experience, p_salary, p_last_increment, p_skills, p_rating)
    ON CONFLICT (emp_id) DO UPDATE
    SET department = EXCLUDED.department,
        designation = EXCLUDED.designation,
        experience = EXCLUDED.experience,
        salary = EXCLUDED.salary,
        last_increment = EXCLUDED.last_increment,
        skills = EXCLUDED.skills,
        performance_rating = EXCLUDED.performance_rating;

    RETURN 'Upsert operation completed';
END;
$$ LANGUAGE plpgsql;

-- 16. Promote employee
CREATE OR REPLACE FUNCTION promote_employee(
    p_emp_id INT,
    new_designation VARCHAR,
    salary_raise NUMERIC
)
RETURNS TEXT AS $$
BEGIN
    UPDATE professional_info
    SET designation = new_designation,
        salary = salary + salary_raise,
        last_increment = salary_raise
    WHERE emp_id = p_emp_id;

    IF FOUND THEN
        RETURN 'Employee promoted';
    ELSE
        RETURN 'No such employee found';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 17. Views: Analytics

-- Low performers
CREATE OR REPLACE VIEW low_performers AS
SELECT pi.emp_id, pi.designation, pi.performance_rating, e.name
FROM professional_info pi
JOIN employee e ON e.emp_id = pi.emp_id
WHERE pi.performance_rating <= 2;

-- Top earner per department
CREATE OR REPLACE VIEW top_earners_per_department AS
SELECT *
FROM (
    SELECT *, RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dept_rank
    FROM professional_info
) sub
WHERE dept_rank = 1;

-- Promotion candidates
CREATE OR REPLACE VIEW promotion_candidates AS
SELECT e.name, pi.emp_id, pi.designation, pi.performance_rating
FROM professional_info pi
JOIN employee e ON e.emp_id = pi.emp_id
WHERE pi.performance_rating >= 4 AND pi.salary < 70000;

-- 18. Indexes for performance
CREATE INDEX IF NOT EXISTS idx_department ON professional_info(department);
CREATE INDEX IF NOT EXISTS idx_rating ON professional_info(performance_rating);
CREATE INDEX IF NOT EXISTS idx_salary ON professional_info(salary);
