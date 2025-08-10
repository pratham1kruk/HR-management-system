-- =============================
-- REWRITTEN professional_info.sql
-- With updated column names and derived experience
-- =============================

-- 🔁 Trigger Function: Log salary updates
CREATE OR REPLACE FUNCTION log_salary_update() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.current_salary <> OLD.current_salary THEN
        INSERT INTO salary_log (emp_id, old_salary, new_salary)
        VALUES (OLD.emp_id, OLD.current_salary, NEW.current_salary);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 🔁 Create Trigger for salary update
DROP TRIGGER IF EXISTS trg_salary_update ON professional_info;
CREATE TRIGGER trg_salary_update
AFTER UPDATE ON professional_info
FOR EACH ROW
EXECUTE FUNCTION log_salary_update();

-- 🔁 Trigger Function: Log deletion
CREATE OR REPLACE FUNCTION log_professional_delete() RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO salary_log(emp_id, old_salary, new_salary, action, deleted_at)
    VALUES (OLD.emp_id, OLD.current_salary, NULL, 'delete', NOW());
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- 🔁 Create Trigger for deletion
DROP TRIGGER IF EXISTS trg_log_delete ON professional_info;
CREATE TRIGGER trg_log_delete
BEFORE DELETE ON professional_info
FOR EACH ROW
EXECUTE FUNCTION log_professional_delete();

-- 🔧 Function: Return highest salary
CREATE OR REPLACE FUNCTION get_highest_salary() RETURNS NUMERIC AS $$
BEGIN
    RETURN (SELECT MAX(current_salary) FROM professional_info);
END;
$$ LANGUAGE plpgsql;

-- 🔧 Function: Count in department
CREATE OR REPLACE FUNCTION count_in_department(dept VARCHAR) RETURNS INT AS $$
BEGIN
    RETURN (SELECT COUNT(*) FROM professional_info WHERE department = dept);
END;
$$ LANGUAGE plpgsql;

-- 📊 View: Employees with >3 years experience
CREATE OR REPLACE VIEW experienced_employees AS
SELECT e.emp_id, CONCAT(e.first_name, ' ', e.last_name) AS name, 
       p.designation, 
       DATE_PART('year', AGE(e.hire_date)) AS experience,
       p.current_salary AS salary
FROM employee e
JOIN professional_info p ON e.emp_id = p.emp_id
WHERE DATE_PART('year', AGE(e.hire_date)) > 3;

-- 📊 View: Low performers (rating ≤ 2)
CREATE OR REPLACE VIEW low_performers AS
SELECT pi.emp_id, pi.designation, pi.performance_rating, 
       CONCAT(e.first_name, ' ', e.last_name) AS name
FROM professional_info pi
JOIN employee e ON e.emp_id = pi.emp_id
WHERE pi.performance_rating <= 2;

-- 📊 View: Top earners per department
CREATE OR REPLACE VIEW top_earners_per_department AS
SELECT *
FROM (
    SELECT *, RANK() OVER (PARTITION BY department ORDER BY current_salary DESC) AS dept_rank
    FROM professional_info
) sub
WHERE dept_rank = 1;

-- 📊 View: Promotion candidates
CREATE OR REPLACE VIEW promotion_candidates AS
SELECT CONCAT(e.first_name, ' ', e.last_name) AS name, pi.emp_id, 
       pi.designation, pi.performance_rating
FROM professional_info pi
JOIN employee e ON e.emp_id = pi.emp_id
WHERE pi.performance_rating >= 4 AND pi.current_salary < 70000;

-- 📊 CTE: Departments with avg salary above overall avg
WITH dept_avg AS (
    SELECT department, AVG(current_salary) AS dept_avg_salary
    FROM professional_info
    GROUP BY department
), overall_avg AS (
    SELECT AVG(current_salary) AS overall_salary
    FROM professional_info
)
SELECT d.*
FROM dept_avg d, overall_avg o
WHERE d.dept_avg_salary > o.overall_salary;

-- 🎯 CASE statement usage
SELECT emp_id, department, current_salary,
    CASE 
        WHEN current_salary > 70000 THEN 'High'
        WHEN current_salary BETWEEN 50000 AND 70000 THEN 'Medium'
        ELSE 'Low'
    END AS salary_grade
FROM professional_info;

-- 📊 Salary Comparison Analysis
CREATE OR REPLACE VIEW salary_comparison AS
SELECT 
    e.emp_id,
    (e.first_name || ' ' || e.last_name) AS full_name,
    e.hire_date,
    
    -- Salary difference for the same employee
    (p.current_salary - COALESCE(p.previous_salary, 0)) AS salary_diff,
    
    -- Previous employee's current salary (by hire date)
    LAG(p.current_salary, 1) OVER (ORDER BY e.hire_date) AS prev_emp_salary,
    
    -- Current employee's salary
    p.current_salary,
    
    -- Next employee's current salary (by hire date)
    LEAD(p.current_salary, 1) OVER (ORDER BY e.hire_date) AS next_emp_salary,
    
    -- Last increment (directly from record)
    p.last_increment

FROM employee e
JOIN professional_info p 
     ON e.emp_id = p.emp_id
ORDER BY e.hire_date;


-- 🏆 RANK employees by salary
SELECT emp_id, current_salary,
       RANK() OVER (ORDER BY current_salary DESC) AS salary_rank
FROM professional_info;

-- 📈 Running salary SUM & AVG
SELECT emp_id, current_salary,
       SUM(current_salary) OVER (ORDER BY emp_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_salary_sum,
       AVG(current_salary) OVER (ORDER BY emp_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_salary_avg
FROM professional_info;

-- 🔁 Upsert Function
CREATE OR REPLACE FUNCTION upsert_professional_info(
    p_emp_id INT,
    p_department VARCHAR,
    p_designation VARCHAR,
    p_current_salary NUMERIC,
    p_previous_salary NUMERIC,
    p_last_increment NUMERIC,
    p_skills TEXT[],
    p_rating FLOAT
)
RETURNS TEXT AS $$
BEGIN
    INSERT INTO professional_info (emp_id, department, designation, current_salary, previous_salary, last_increment, skills, performance_rating)
    VALUES (p_emp_id, p_department, p_designation, p_current_salary, p_previous_salary, p_last_increment, p_skills, p_rating)
    ON CONFLICT (emp_id) DO UPDATE
    SET department = EXCLUDED.department,
        designation = EXCLUDED.designation,
        current_salary = EXCLUDED.current_salary,
        previous_salary = EXCLUDED.previous_salary,
        last_increment = EXCLUDED.last_increment,
        skills = EXCLUDED.skills,
        performance_rating = EXCLUDED.performance_rating;

    RETURN 'Upsert operation completed';
END;
$$ LANGUAGE plpgsql;

-- 🔁 Promotion Function
CREATE OR REPLACE FUNCTION promote_employee(
    p_emp_id INT,
    new_designation VARCHAR,
    salary_raise NUMERIC
)
RETURNS TEXT AS $$
BEGIN
    UPDATE professional_info
    SET designation = new_designation,
        current_salary = current_salary + salary_raise,
        last_increment = salary_raise,
        previous_salary = current_salary
    WHERE emp_id = p_emp_id;

    IF FOUND THEN
        RETURN 'Employee promoted';
    ELSE
        RETURN 'No such employee found';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 📈 Indexes
CREATE INDEX IF NOT EXISTS idx_department ON professional_info(department);
CREATE INDEX IF NOT EXISTS idx_rating ON professional_info(performance_rating);
CREATE INDEX IF NOT EXISTS idx_current_salary ON professional_info(current_salary);
