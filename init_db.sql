-- ============================================================================
-- PUBLIC WORKS DEPARTMENT - DATABASE INITIALIZATION SCRIPT
-- Red Flag Detection System for Financial Irregularities
-- ============================================================================

-- Drop existing tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS pending_actions;
DROP TABLE IF EXISTS approval_records;
DROP TABLE IF EXISTS red_flag_alerts;
DROP TABLE IF EXISTS deposit_expenditure;
DROP TABLE IF EXISTS deposit_works;
DROP TABLE IF EXISTS agreement_register;
DROP TABLE IF EXISTS ra_bills;
DROP TABLE IF EXISTS works_master;

-- ============================================================================
-- TABLE DEFINITIONS
-- ============================================================================

-- Main Works Master Table
CREATE TABLE works_master (
    work_id VARCHAR(50) PRIMARY KEY,
    work_name VARCHAR(500),
    work_type VARCHAR(50), -- 'ROAD', 'BUILDING', 'Deposit'
    division_code VARCHAR(20),
    sub_division VARCHAR(50),
    aa_amount DECIMAL(15,2),
    aa_date DATE,
    aa_number VARCHAR(100),
    ts_amount DECIMAL(15,2),
    contract_amount DECIMAL(15,2),
    stipulated_completion_date DATE,
    actual_completion_date DATE,
    work_status VARCHAR(50),
    scheme_code VARCHAR(50),
    road_number VARCHAR(50),
    start_km DECIMAL(10,3),
    end_km DECIMAL(10,3),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- RA Bills / Payment Details
CREATE TABLE ra_bills (
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    work_id VARCHAR(50),
    financial_year VARCHAR(20),
    bill_type VARCHAR(100),
    bill_date DATE,
    bill_number VARCHAR(50),
    agency_name VARCHAR(200),
    gross_amount DECIMAL(15,2),
    cumulative_expenditure DECIMAL(15,2),
    remark TEXT,
    item_type VARCHAR(100), -- 'Survey', 'Subgrade', 'Work Contengencies', etc.
    FOREIGN KEY (work_id) REFERENCES works_master(work_id)
);

-- Deposit Works
CREATE TABLE deposit_works (
    deposit_work_id VARCHAR(50) PRIMARY KEY,
    work_name VARCHAR(500),
    user_department VARCHAR(200),
    aa_number VARCHAR(100),
    aa_date DATE,
    aa_amount DECIMAL(15,2),
    total_received DECIMAL(15,2),
    total_expenditure DECIMAL(15,2),
    centage_amount DECIMAL(15,2),
    balance_with_ddo DECIMAL(15,2),
    work_status VARCHAR(50),
    completion_date DATE,
    division_code VARCHAR(20)
);

-- Expenditure Details for Deposit Works
CREATE TABLE deposit_expenditure (
    exp_id INT AUTO_INCREMENT PRIMARY KEY,
    deposit_work_id VARCHAR(50),
    financial_year VARCHAR(20),
    bill_type VARCHAR(100),
    bill_date DATE,
    agency_name VARCHAR(200),
    bill_amount DECIMAL(15,2),
    centage_amount DECIMAL(15,2),
    cumulative_expenditure DECIMAL(15,2),
    remark TEXT,
    FOREIGN KEY (deposit_work_id) REFERENCES deposit_works(deposit_work_id)
);

-- Agreement Register
CREATE TABLE agreement_register (
    agreement_id INT AUTO_INCREMENT PRIMARY KEY,
    agreement_no VARCHAR(50),
    contractor_name VARCHAR(200),
    work_name VARCHAR(500),
    road_number VARCHAR(50),
    start_km DECIMAL(10,3),
    end_km DECIMAL(10,3),
    agreement_amount DECIMAL(15,2),
    award_date DATE,
    award_year INT,
    work_completion_months INT,
    head_of_account VARCHAR(100),
    sub_division VARCHAR(50)
);

-- Red Flag Alerts Table
CREATE TABLE red_flag_alerts (
    alert_id INT AUTO_INCREMENT PRIMARY KEY,
    alert_type VARCHAR(100),
    work_id VARCHAR(50),
    deposit_work_id VARCHAR(50),
    severity VARCHAR(20), -- 'HIGH', 'MEDIUM', 'LOW'
    description TEXT,
    detected_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    amount_involved DECIMAL(15,2),
    status VARCHAR(50) DEFAULT 'PENDING', -- 'PENDING', 'REVIEWED', 'RESOLVED'
    reviewed_by VARCHAR(100),
    review_date TIMESTAMP,
    INDEX idx_alert_type (alert_type),
    INDEX idx_detected_date (detected_date),
    INDEX idx_status (status)
);

-- Approval Records (for tracking approvals of excess expenditure, etc.)
CREATE TABLE approval_records (
    approval_id INT AUTO_INCREMENT PRIMARY KEY,
    work_id VARCHAR(50),
    approval_type VARCHAR(100),
    approval_date DATE,
    approved_amount DECIMAL(15,2),
    approved_by VARCHAR(100),
    remarks TEXT,
    FOREIGN KEY (work_id) REFERENCES works_master(work_id)
);

-- Pending Actions (for tracking required follow-up actions)
CREATE TABLE pending_actions (
    action_id INT AUTO_INCREMENT PRIMARY KEY,
    action_type VARCHAR(100),
    work_id VARCHAR(50),
    due_date DATE,
    priority VARCHAR(20),
    description TEXT,
    status VARCHAR(50) DEFAULT 'PENDING',
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TRIGGERS FOR REAL-TIME RED FLAG DETECTION
-- ============================================================================

-- Trigger 1: Detect Fund Diversion in Deposit Works
DELIMITER $$

CREATE TRIGGER trg_detect_fund_diversion_deposit
AFTER INSERT ON deposit_expenditure
FOR EACH ROW
BEGIN
    DECLARE work_name_text VARCHAR(500);
    DECLARE similarity_score INT DEFAULT 0;
    
    -- Get the approved work name
    SELECT work_name INTO work_name_text
    FROM deposit_works
    WHERE deposit_work_id = NEW.deposit_work_id;
    
    -- Check if remark significantly differs from work name
    IF (LOWER(NEW.remark) NOT LIKE CONCAT('%', 
        SUBSTRING_INDEX(LOWER(work_name_text), ' ', 3), '%'))
       AND NEW.bill_amount > 100000 THEN
        
        INSERT INTO red_flag_alerts (
            alert_type,
            deposit_work_id,
            severity,
            description,
            amount_involved
        ) VALUES (
            'Fund Diversion',
            NEW.deposit_work_id,
            'HIGH',
            CONCAT('Remark "', NEW.remark, '" does not match approved work: "', 
                   work_name_text, '"'),
            NEW.bill_amount
        );
    END IF;
END$$

DELIMITER ;

-- Trigger 2: Monitor Excess Expenditure
DELIMITER $$

CREATE TRIGGER trg_monitor_excess_expenditure
AFTER INSERT ON ra_bills
FOR EACH ROW
BEGIN
    DECLARE aa_amt DECIMAL(15,2);
    DECLARE total_exp DECIMAL(15,2);
    DECLARE has_approval INT;
    DECLARE excess_pct DECIMAL(10,2);
    
    -- Get AA amount for this work
    SELECT aa_amount INTO aa_amt
    FROM works_master
    WHERE work_id = NEW.work_id;
    
    -- Calculate excess percentage
    SET excess_pct = ((NEW.cumulative_expenditure - aa_amt) / aa_amt) * 100;
    
    -- Early warning at 95% of AA
    IF NEW.cumulative_expenditure >= (aa_amt * 0.95) 
       AND NEW.cumulative_expenditure < aa_amt THEN
        
        INSERT INTO red_flag_alerts (
            alert_type, work_id, severity, description, amount_involved
        ) VALUES (
            'Approaching AA Limit',
            NEW.work_id,
            'MEDIUM',
            CONCAT('Expenditure at ', ROUND(excess_pct + 100, 2), 
                   '% of AA. Only ', ROUND(aa_amt - NEW.cumulative_expenditure, 2), 
                   ' remaining'),
            NEW.cumulative_expenditure
        );
    
    -- Alert when 110% exceeded without approval
    ELSEIF NEW.cumulative_expenditure > (aa_amt * 1.10) THEN
        
        -- Check if approval exists
        SELECT COUNT(*) INTO has_approval
        FROM approval_records
        WHERE work_id = NEW.work_id 
          AND approval_type = 'Excess Expenditure';
        
        IF has_approval = 0 THEN
            INSERT INTO red_flag_alerts (
                alert_type, work_id, severity, description, amount_involved
            ) VALUES (
                'Excess Expenditure Without Approval',
                NEW.work_id,
                'HIGH',
                CONCAT('Expenditure exceeds AA by ', ROUND(excess_pct, 2), 
                       '% without approval. Excess amount: Rs.', 
                       ROUND(NEW.cumulative_expenditure - aa_amt, 2)),
                NEW.cumulative_expenditure - aa_amt
            );
        END IF;
    END IF;
END$$

DELIMITER ;

-- Trigger 3: Monitor Work Delays
DELIMITER $$

CREATE TRIGGER trg_monitor_work_delays
AFTER UPDATE ON works_master
FOR EACH ROW
BEGIN
    DECLARE days_delayed INT;
    DECLARE last_activity_date DATE;
    
    -- Calculate delay if work not completed
    IF NEW.actual_completion_date IS NULL 
       AND NEW.stipulated_completion_date < CURRENT_DATE THEN
        
        SET days_delayed = DATEDIFF(CURRENT_DATE, NEW.stipulated_completion_date);
        
        -- Get last payment date
        SELECT MAX(bill_date) INTO last_activity_date
        FROM ra_bills
        WHERE work_id = NEW.work_id;
        
        -- High priority alert for severe delays
        IF days_delayed > 365 THEN
            INSERT INTO red_flag_alerts (
                alert_type, work_id, severity, description, amount_involved
            ) VALUES (
                'Severe Delay',
                NEW.work_id,
                'HIGH',
                CONCAT('Work delayed by ', days_delayed, ' days (>1 year). ',
                       'Last activity: ', COALESCE(last_activity_date, 'Unknown')),
                NEW.contract_amount
            );
        
        -- Medium priority for moderate delays
        ELSEIF days_delayed > 90 THEN
            INSERT INTO red_flag_alerts (
                alert_type, work_id, severity, description, amount_involved
            ) VALUES (
                'Moderate Delay',
                NEW.work_id,
                'MEDIUM',
                CONCAT('Work delayed by ', days_delayed, ' days. ',
                       'Stipulated completion: ', NEW.stipulated_completion_date),
                NEW.contract_amount
            );
        END IF;
        
        -- Additional alert for stalled works
        IF DATEDIFF(CURRENT_DATE, last_activity_date) > 180 THEN
            INSERT INTO red_flag_alerts (
                alert_type, work_id, severity, description
            ) VALUES (
                'Stalled Work',
                NEW.work_id,
                'HIGH',
                CONCAT('No payment activity for ', 
                       DATEDIFF(CURRENT_DATE, last_activity_date), ' days')
            );
        END IF;
    END IF;
END$$

DELIMITER ;

-- Trigger 4: Prevent Work Splitting
DELIMITER $$

CREATE TRIGGER trg_prevent_work_splitting
BEFORE INSERT ON agreement_register
FOR EACH ROW
BEGIN
    DECLARE similar_works_count INT DEFAULT 0;
    DECLARE combined_amount DECIMAL(15,2) DEFAULT 0;
    DECLARE location_match VARCHAR(100);
    DECLARE alert_message TEXT;
    
    -- Extract location from new work
    SET location_match = CASE 
        WHEN NEW.work_name LIKE '%Deoni%' THEN '%Deoni%'
        WHEN NEW.work_name LIKE '%Nilanga%' THEN '%Nilanga%'
        WHEN NEW.work_name LIKE '%Court%' THEN '%Court%'
        ELSE NULL
    END;
    
    -- Check for similar works by same contractor in same year
    IF location_match IS NOT NULL THEN
        SELECT 
            COUNT(*),
            SUM(agreement_amount) + NEW.agreement_amount
        INTO similar_works_count, combined_amount
        FROM agreement_register
        WHERE contractor_name = NEW.contractor_name
            AND award_year = NEW.award_year
            AND work_name LIKE location_match
            AND agreement_amount < 1000000
            AND DATEDIFF(CURRENT_DATE, award_date) <= 90;
        
        -- Alert if potential splitting detected
        IF similar_works_count >= 1 
           AND NEW.agreement_amount < 1000000 
           AND combined_amount > 1000000 THEN
            
            SET alert_message = CONCAT(
                'POTENTIAL WORK SPLITTING DETECTED: ',
                'Contractor: ', NEW.contractor_name, ' | ',
                'Similar works found: ', similar_works_count, ' | ',
                'Combined value: Rs.', combined_amount, ' (Exceeds 10L threshold) | ',
                'This work: Rs.', NEW.agreement_amount
            );
            
            -- Log to alerts table
            INSERT INTO red_flag_alerts (
                alert_type,
                severity,
                description,
                amount_involved
            ) VALUES (
                'Work Splitting',
                'HIGH',
                alert_message,
                combined_amount
            );
        END IF;
    END IF;
END$$

DELIMITER ;

-- Trigger 5: Enforce Centage Recovery
DELIMITER $$

CREATE TRIGGER trg_enforce_centage_recovery
BEFORE INSERT ON deposit_expenditure
FOR EACH ROW
BEGIN
    DECLARE required_centage DECIMAL(15,2);
    DECLARE work_aa_amount DECIMAL(15,2);
    
    -- Calculate required centage (5% of bill amount)
    SET required_centage = NEW.bill_amount * 0.05;
    
    -- Get AA amount
    SELECT aa_amount INTO work_aa_amount
    FROM deposit_works
    WHERE deposit_work_id = NEW.deposit_work_id;
    
    -- Auto-populate centage if missing
    IF NEW.centage_amount IS NULL OR NEW.centage_amount = 0 THEN
        SET NEW.centage_amount = required_centage;
    END IF;
    
    -- Alert if centage is less than required (with 1% tolerance)
    IF NEW.bill_amount > 0 AND NEW.centage_amount < (required_centage * 0.99) THEN
        
        INSERT INTO red_flag_alerts (
            alert_type,
            deposit_work_id,
            severity,
            description,
            amount_involved
        ) VALUES (
            'Centage Not Recovered',
            NEW.deposit_work_id,
            'MEDIUM',
            CONCAT('Bill amount: Rs.', NEW.bill_amount, 
                   ' | Expected centage: Rs.', ROUND(required_centage, 2),
                   ' | Actual centage: Rs.', ROUND(NEW.centage_amount, 2),
                   ' | Shortage: Rs.', ROUND(required_centage - NEW.centage_amount, 2)),
            required_centage - NEW.centage_amount
        );
    END IF;
    
    -- Update deposit works table centage
    UPDATE deposit_works
    SET centage_amount = COALESCE(centage_amount, 0) + NEW.centage_amount
    WHERE deposit_work_id = NEW.deposit_work_id;
    
END$$

DELIMITER ;

-- Trigger 6: Monitor Unspent Balance
DELIMITER $$

CREATE TRIGGER trg_monitor_unspent_balance
AFTER UPDATE ON deposit_works
FOR EACH ROW
BEGIN
    DECLARE grace_period_days INT DEFAULT 30;
    
    -- Check if work just got completed
    IF NEW.work_status = 'Completed' AND OLD.work_status != 'Completed' THEN
        
        -- Set completion date if not set
        IF NEW.completion_date IS NULL THEN
            UPDATE deposit_works
            SET completion_date = CURRENT_DATE
            WHERE deposit_work_id = NEW.deposit_work_id;
        END IF;
        
        -- Alert if significant balance remains
        IF NEW.balance_with_ddo > 100000 THEN
            
            INSERT INTO red_flag_alerts (
                alert_type,
                deposit_work_id,
                severity,
                description,
                amount_involved
            ) VALUES (
                'Unspent Balance - Return Required',
                NEW.deposit_work_id,
                'MEDIUM',
                CONCAT('Work marked completed with unspent balance of Rs.', 
                       ROUND(NEW.balance_with_ddo, 2),
                       '. Balance must be returned to ', NEW.user_department,
                       ' within ', grace_period_days, ' days.'),
                NEW.balance_with_ddo
            );
            
            -- Create pending action
            INSERT INTO pending_actions (
                action_type,
                work_id,
                due_date,
                priority,
                description
            ) VALUES (
                'Return Unspent Deposit',
                NEW.deposit_work_id,
                DATE_ADD(CURRENT_DATE, INTERVAL grace_period_days DAY),
                'HIGH',
                CONCAT('Return Rs.', ROUND(NEW.balance_with_ddo, 2), 
                       ' to ', NEW.user_department)
            );
        END IF;
    END IF;
END$$

DELIMITER ;

-- ============================================================================
-- VIEWS FOR RED FLAG ANALYSIS
-- ============================================================================

-- View 1: Fund Diversion Detection
CREATE OR REPLACE VIEW v_fund_diversion_analysis AS
WITH deposit_fund_analysis AS (
    SELECT 
        dw.deposit_work_id,
        dw.work_name,
        de.remark,
        de.bill_amount,
        de.agency_name,
        de.bill_date,
        CASE 
            WHEN LOWER(de.remark) LIKE '%unavoidable expenditure%' 
                AND LOWER(dw.work_name) NOT LIKE CONCAT('%', LOWER(de.agency_name), '%')
            THEN 'Potential Diversion'
            WHEN de.remark LIKE '%Road Subgrade%' 
                AND LOWER(dw.work_name) LIKE '%paver block%'
            THEN 'Different Work Type'
            ELSE 'Normal'
        END AS diversion_flag,
        dw.work_name AS approved_work,
        de.remark AS actual_work_done
    FROM deposit_works dw
    JOIN deposit_expenditure de ON dw.deposit_work_id = de.deposit_work_id
    WHERE dw.work_status = 'Completed' OR dw.total_expenditure > 0
),
diversion_cases AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY deposit_work_id ORDER BY bill_date) AS payment_sequence
    FROM deposit_fund_analysis
    WHERE diversion_flag != 'Normal'
)
SELECT 
    deposit_work_id,
    approved_work,
    remark AS work_actually_done,
    bill_amount,
    agency_name,
    diversion_flag,
    'Fund used for work different from approved scope' AS issue_description
FROM diversion_cases
ORDER BY bill_amount DESC;

-- View 2: Wasteful Survey Detection
CREATE OR REPLACE VIEW v_wasteful_survey_analysis AS
WITH survey_analysis AS (
    SELECT 
        w.work_id,
        w.work_name,
        w.aa_amount,
        SUM(CASE 
            WHEN LOWER(r.remark) LIKE '%survey%' 
            THEN r.gross_amount 
            ELSE 0 
        END) AS survey_expenditure,
        SUM(CASE 
            WHEN LOWER(r.remark) LIKE '%subgrade%' 
                OR LOWER(r.remark) LIKE '%construction%'
                OR LOWER(r.remark) LIKE '%completed%'
            THEN r.gross_amount 
            ELSE 0 
        END) AS construction_expenditure,
        SUM(r.gross_amount) AS total_expenditure,
        COUNT(r.bill_id) AS total_bills,
        MAX(r.bill_date) AS last_payment_date,
        DATEDIFF(CURRENT_DATE, MAX(r.bill_date)) AS days_since_last_payment
    FROM works_master w
    LEFT JOIN ra_bills r ON w.work_id = r.work_id
    GROUP BY w.work_id, w.work_name, w.aa_amount
),
wasteful_survey_cases AS (
    SELECT 
        *,
        (survey_expenditure / NULLIF(total_expenditure, 0)) * 100 AS survey_percentage,
        CASE 
            WHEN survey_expenditure > 0 
                AND construction_expenditure = 0 
                AND days_since_last_payment > 180
            THEN 'Wasteful Survey - No Construction'
            WHEN survey_expenditure > 0 
                AND (survey_expenditure / NULLIF(total_expenditure, 0)) > 0.50
            THEN 'Excessive Survey Costs'
            ELSE 'Normal'
        END AS wasteful_flag
    FROM survey_analysis
)
SELECT 
    work_id,
    work_name,
    survey_expenditure,
    construction_expenditure,
    total_expenditure,
    ROUND(survey_percentage, 2) AS survey_pct,
    days_since_last_payment,
    wasteful_flag
FROM wasteful_survey_cases
WHERE wasteful_flag != 'Normal'
ORDER BY survey_expenditure DESC;

-- View 3: Excess Expenditure Detection
CREATE OR REPLACE VIEW v_excess_expenditure_analysis AS
WITH expenditure_tracking AS (
    SELECT 
        w.work_id,
        w.work_name,
        w.aa_amount,
        w.contract_amount,
        r.bill_date,
        r.gross_amount,
        r.cumulative_expenditure,
        (r.cumulative_expenditure / w.aa_amount) * 100 AS aa_percentage_consumed,
        LAG(r.cumulative_expenditure) OVER (
            PARTITION BY w.work_id ORDER BY r.bill_date
        ) AS previous_cumulative,
        CASE 
            WHEN r.cumulative_expenditure > w.aa_amount 
                AND LAG(r.cumulative_expenditure) OVER (
                    PARTITION BY w.work_id ORDER BY r.bill_date
                ) <= w.aa_amount
            THEN 'AA Limit Crossed'
            ELSE 'Within Limit'
        END AS threshold_status
    FROM works_master w
    JOIN ra_bills r ON w.work_id = r.work_id
),
excess_detection AS (
    SELECT 
        work_id,
        work_name,
        aa_amount,
        MAX(cumulative_expenditure) AS total_expenditure,
        MAX(cumulative_expenditure) - aa_amount AS excess_amount,
        ((MAX(cumulative_expenditure) - aa_amount) / aa_amount) * 100 AS excess_percentage,
        COUNT(*) AS total_bills,
        MIN(CASE WHEN threshold_status = 'AA Limit Crossed' 
            THEN bill_date END) AS date_aa_exceeded
    FROM expenditure_tracking
    GROUP BY work_id, work_name, aa_amount
    HAVING MAX(cumulative_expenditure) > (aa_amount * 1.10)
)
SELECT 
    e.*,
    DATEDIFF(CURRENT_DATE, e.date_aa_exceeded) AS days_since_exceeded,
    'No approval found for excess expenditure' AS red_flag_description
FROM excess_detection e
LEFT JOIN approval_records a 
    ON e.work_id = a.work_id 
    AND a.approval_type = 'Excess Expenditure'
WHERE a.work_id IS NULL
ORDER BY excess_percentage DESC;

-- View 4: Work Delay Analysis
CREATE OR REPLACE VIEW v_work_delay_analysis AS
WITH work_timeline_analysis AS (
    SELECT 
        w.work_id,
        w.work_name,
        w.stipulated_completion_date,
        w.actual_completion_date,
        w.contract_amount,
        w.aa_amount,
        CASE 
            WHEN w.actual_completion_date IS NOT NULL
            THEN DATEDIFF(w.actual_completion_date, w.stipulated_completion_date)
            ELSE DATEDIFF(CURRENT_DATE, w.stipulated_completion_date)
        END AS delay_days,
        (SELECT SUM(gross_amount) FROM ra_bills WHERE work_id = w.work_id) AS total_paid,
        (SELECT COUNT(*) FROM ra_bills WHERE work_id = w.work_id) AS total_bills,
        (SELECT MAX(bill_date) FROM ra_bills WHERE work_id = w.work_id) AS last_payment_date,
        (SELECT remark FROM ra_bills WHERE work_id = w.work_id 
         ORDER BY bill_date DESC LIMIT 1) AS latest_status
    FROM works_master w
    WHERE w.stipulated_completion_date IS NOT NULL
),
delayed_works_summary AS (
    SELECT 
        t.*,
        DATEDIFF(CURRENT_DATE, t.last_payment_date) AS days_since_last_activity,
        CASE 
            WHEN t.delay_days > 365 THEN 'Severe Delay (>1 year)'
            WHEN t.delay_days > 180 THEN 'Major Delay (>6 months)'
            WHEN t.delay_days > 90 THEN 'Moderate Delay (>3 months)'
            WHEN t.delay_days > 0 THEN 'Minor Delay'
            ELSE 'On Track'
        END AS delay_category,
        (t.total_paid / NULLIF(t.aa_amount, 0)) * 100 AS budget_utilized_pct
    FROM work_timeline_analysis t
)
SELECT 
    work_id,
    work_name,
    stipulated_completion_date,
    actual_completion_date,
    delay_days,
    delay_category,
    last_payment_date,
    days_since_last_activity,
    latest_status,
    ROUND(budget_utilized_pct, 2) AS budget_utilized_pct,
    total_bills,
    contract_amount
FROM delayed_works_summary
WHERE delay_days > 0
ORDER BY delay_days DESC, contract_amount DESC;

-- View 5: Centage Recovery Analysis
CREATE OR REPLACE VIEW v_centage_recovery_analysis AS
WITH centage_analysis AS (
    SELECT 
        dw.deposit_work_id,
        dw.work_name,
        dw.user_department,
        dw.aa_amount,
        dw.total_expenditure,
        dw.centage_amount AS recorded_centage,
        dw.aa_amount * 0.05 AS expected_centage,
        (dw.aa_amount * 0.05) - COALESCE(dw.centage_amount, 0) AS centage_shortfall,
        (SELECT COUNT(*) FROM deposit_expenditure 
         WHERE deposit_work_id = dw.deposit_work_id) AS number_of_bills,
        dw.work_status,
        dw.completion_date
    FROM deposit_works dw
    WHERE dw.total_expenditure > 0
),
non_recovery_cases AS (
    SELECT 
        *,
        (COALESCE(recorded_centage, 0) / NULLIF(expected_centage, 0)) * 100 AS centage_recovery_pct,
        CASE 
            WHEN COALESCE(recorded_centage, 0) = 0
            THEN 'Complete Non-Recovery'
            WHEN COALESCE(recorded_centage, 0) < expected_centage * 0.50
            THEN 'Severe Under-Recovery (< 50%)'
            WHEN COALESCE(recorded_centage, 0) < expected_centage * 0.90
            THEN 'Partial Under-Recovery'
            ELSE 'Normal'
        END AS recovery_status
    FROM centage_analysis
)
SELECT 
    deposit_work_id,
    work_name,
    user_department,
    ROUND(aa_amount, 2) AS aa_amount,
    ROUND(total_expenditure, 2) AS total_spent,
    ROUND(expected_centage, 2) AS expected_centage_5pct,
    ROUND(COALESCE(recorded_centage, 0), 2) AS actual_centage_recovered,
    ROUND(centage_shortfall, 2) AS revenue_loss,
    ROUND(centage_recovery_pct, 2) AS recovery_percentage,
    number_of_bills,
    recovery_status,
    work_status
FROM non_recovery_cases
WHERE recovery_status != 'Normal'
ORDER BY centage_shortfall DESC;

-- View 6: Unspent Balance Analysis
CREATE OR REPLACE VIEW v_unspent_balance_analysis AS
WITH deposit_balance_analysis AS (
    SELECT 
        dw.deposit_work_id,
        dw.work_name,
        dw.user_department,
        dw.aa_amount,
        dw.total_received,
        dw.total_expenditure,
        dw.balance_with_ddo,
        dw.work_status,
        dw.completion_date,
        DATEDIFF(CURRENT_DATE, dw.completion_date) AS days_since_completion,
        (SELECT MAX(bill_date) FROM deposit_expenditure 
         WHERE deposit_work_id = dw.deposit_work_id) AS last_bill_date,
        (dw.balance_with_ddo / NULLIF(dw.total_received, 0)) * 100 AS unutilized_percentage
    FROM deposit_works dw
    WHERE dw.work_status = 'Completed'
),
unspent_violations AS (
    SELECT 
        *,
        CASE 
            WHEN balance_with_ddo > 500000 AND days_since_completion > 180
            THEN 'Critical - Large Balance Overdue (>6 months)'
            WHEN balance_with_ddo > 100000 AND days_since_completion > 90
            THEN 'High - Balance Not Returned (>3 months)'
            WHEN balance_with_ddo > 100000 AND days_since_completion > 30
            THEN 'Medium - Balance Pending Return'
            ELSE 'Normal'
        END AS violation_severity
    FROM deposit_balance_analysis
    WHERE balance_with_ddo > 100000
)
SELECT 
    deposit_work_id,
    work_name,
    user_department,
    ROUND(total_received, 2) AS amount_received,
    ROUND(total_expenditure, 2) AS amount_spent,
    ROUND(balance_with_ddo, 2) AS unspent_balance,
    ROUND(unutilized_percentage, 2) AS unutilized_pct,
    work_status,
    completion_date,
    last_bill_date,
    days_since_completion,
    violation_severity
FROM unspent_violations
WHERE violation_severity != 'Normal'
ORDER BY balance_with_ddo DESC, days_since_completion DESC;

-- ============================================================================
-- UTILITY STORED PROCEDURES
-- ============================================================================

-- Procedure to generate comprehensive red flag report
DELIMITER $$

CREATE PROCEDURE sp_generate_red_flag_report(
    IN p_start_date DATE,
    IN p_end_date DATE
)
BEGIN
    SELECT 
        alert_type,
        severity,
        COUNT(*) AS alert_count,
        SUM(amount_involved) AS total_amount,
        AVG(amount_involved) AS avg_amount
    FROM red_flag_alerts
    WHERE detected_date BETWEEN p_start_date AND p_end_date
    GROUP BY alert_type, severity
    ORDER BY severity, total_amount DESC;
END$$

DELIMITER ;

-- ============================================================================
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- ============================================================================

CREATE INDEX idx_work_id ON ra_bills(work_id);
CREATE INDEX idx_bill_date ON ra_bills(bill_date);
CREATE INDEX idx_deposit_work_id ON deposit_expenditure(deposit_work_id);
CREATE INDEX idx_work_status ON works_master(work_status);
CREATE INDEX idx_completion_date ON works_master(stipulated_completion_date);
CREATE INDEX idx_contractor ON agreement_register(contractor_name);
CREATE INDEX idx_award_year ON agreement_register(award_year);

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

SELECT 'Database initialization completed successfully!' AS status,
       'All tables, triggers, views, and procedures have been created.' AS message;