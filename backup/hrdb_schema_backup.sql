--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: count_in_department(character varying); Type: FUNCTION; Schema: public; Owner: hradmin
--

CREATE FUNCTION public.count_in_department(dept character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN (SELECT COUNT(*) FROM professional_info WHERE department = dept);
END;
$$;


ALTER FUNCTION public.count_in_department(dept character varying) OWNER TO hradmin;

--
-- Name: get_highest_salary(); Type: FUNCTION; Schema: public; Owner: hradmin
--

CREATE FUNCTION public.get_highest_salary() RETURNS numeric
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN (SELECT MAX(current_salary) FROM professional_info);
END;
$$;


ALTER FUNCTION public.get_highest_salary() OWNER TO hradmin;

--
-- Name: log_professional_delete(); Type: FUNCTION; Schema: public; Owner: hradmin
--

CREATE FUNCTION public.log_professional_delete() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO salary_log(emp_id, old_salary, new_salary, action, deleted_at)
    VALUES (OLD.emp_id, OLD.current_salary, NULL, 'delete', NOW());
    RETURN OLD;
END;
$$;


ALTER FUNCTION public.log_professional_delete() OWNER TO hradmin;

--
-- Name: log_salary_update(); Type: FUNCTION; Schema: public; Owner: hradmin
--

CREATE FUNCTION public.log_salary_update() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.current_salary <> OLD.current_salary THEN
        INSERT INTO salary_log (emp_id, old_salary, new_salary)
        VALUES (OLD.emp_id, OLD.current_salary, NEW.current_salary);
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.log_salary_update() OWNER TO hradmin;

--
-- Name: promote_employee(integer, character varying, numeric); Type: FUNCTION; Schema: public; Owner: hradmin
--

CREATE FUNCTION public.promote_employee(p_emp_id integer, new_designation character varying, salary_raise numeric) RETURNS text
    LANGUAGE plpgsql
    AS $$
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
$$;


ALTER FUNCTION public.promote_employee(p_emp_id integer, new_designation character varying, salary_raise numeric) OWNER TO hradmin;

--
-- Name: upsert_professional_info(integer, character varying, character varying, numeric, numeric, numeric, text[], double precision); Type: FUNCTION; Schema: public; Owner: hradmin
--

CREATE FUNCTION public.upsert_professional_info(p_emp_id integer, p_department character varying, p_designation character varying, p_current_salary numeric, p_previous_salary numeric, p_last_increment numeric, p_skills text[], p_rating double precision) RETURNS text
    LANGUAGE plpgsql
    AS $$
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
$$;


ALTER FUNCTION public.upsert_professional_info(p_emp_id integer, p_department character varying, p_designation character varying, p_current_salary numeric, p_previous_salary numeric, p_last_increment numeric, p_skills text[], p_rating double precision) OWNER TO hradmin;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: employee; Type: TABLE; Schema: public; Owner: hradmin
--

CREATE TABLE public.employee (
    emp_id integer NOT NULL,
    first_name character varying(50) NOT NULL,
    last_name character varying(50) NOT NULL,
    dob date,
    gender character varying(10),
    email character varying(100),
    phone character varying(20),
    hire_date date DEFAULT CURRENT_DATE
);


ALTER TABLE public.employee OWNER TO hradmin;

--
-- Name: employee_emp_id_seq; Type: SEQUENCE; Schema: public; Owner: hradmin
--

CREATE SEQUENCE public.employee_emp_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.employee_emp_id_seq OWNER TO hradmin;

--
-- Name: employee_emp_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: hradmin
--

ALTER SEQUENCE public.employee_emp_id_seq OWNED BY public.employee.emp_id;


--
-- Name: professional_info; Type: TABLE; Schema: public; Owner: hradmin
--

CREATE TABLE public.professional_info (
    emp_id integer NOT NULL,
    designation character varying(100),
    department character varying(100),
    current_salary numeric(10,2),
    previous_salary numeric(10,2),
    last_increment numeric(10,2),
    skills text[],
    performance_rating double precision
);


ALTER TABLE public.professional_info OWNER TO hradmin;

--
-- Name: experienced_employees; Type: VIEW; Schema: public; Owner: hradmin
--

CREATE VIEW public.experienced_employees AS
 SELECT e.emp_id,
    concat(e.first_name, ' ', e.last_name) AS name,
    p.designation,
    date_part('year'::text, age((e.hire_date)::timestamp with time zone)) AS experience,
    p.current_salary AS salary
   FROM (public.employee e
     JOIN public.professional_info p ON ((e.emp_id = p.emp_id)))
  WHERE (date_part('year'::text, age((e.hire_date)::timestamp with time zone)) > (3)::double precision);


ALTER VIEW public.experienced_employees OWNER TO hradmin;

--
-- Name: low_performers; Type: VIEW; Schema: public; Owner: hradmin
--

CREATE VIEW public.low_performers AS
 SELECT pi.emp_id,
    pi.designation,
    pi.performance_rating,
    concat(e.first_name, ' ', e.last_name) AS name
   FROM (public.professional_info pi
     JOIN public.employee e ON ((e.emp_id = pi.emp_id)))
  WHERE (pi.performance_rating <= (2)::double precision);


ALTER VIEW public.low_performers OWNER TO hradmin;

--
-- Name: promotion_candidates; Type: VIEW; Schema: public; Owner: hradmin
--

CREATE VIEW public.promotion_candidates AS
 SELECT concat(e.first_name, ' ', e.last_name) AS name,
    pi.emp_id,
    pi.designation,
    pi.performance_rating
   FROM (public.professional_info pi
     JOIN public.employee e ON ((e.emp_id = pi.emp_id)))
  WHERE ((pi.performance_rating >= (4)::double precision) AND (pi.current_salary < (70000)::numeric));


ALTER VIEW public.promotion_candidates OWNER TO hradmin;

--
-- Name: salary_log; Type: TABLE; Schema: public; Owner: hradmin
--

CREATE TABLE public.salary_log (
    log_id integer NOT NULL,
    emp_id integer,
    old_salary numeric,
    new_salary numeric,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    action text DEFAULT 'update'::text,
    deleted_at timestamp without time zone
);


ALTER TABLE public.salary_log OWNER TO hradmin;

--
-- Name: salary_log_log_id_seq; Type: SEQUENCE; Schema: public; Owner: hradmin
--

CREATE SEQUENCE public.salary_log_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.salary_log_log_id_seq OWNER TO hradmin;

--
-- Name: salary_log_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: hradmin
--

ALTER SEQUENCE public.salary_log_log_id_seq OWNED BY public.salary_log.log_id;


--
-- Name: top_earners_per_department; Type: VIEW; Schema: public; Owner: hradmin
--

CREATE VIEW public.top_earners_per_department AS
 SELECT emp_id,
    designation,
    department,
    current_salary,
    previous_salary,
    last_increment,
    skills,
    performance_rating,
    dept_rank
   FROM ( SELECT professional_info.emp_id,
            professional_info.designation,
            professional_info.department,
            professional_info.current_salary,
            professional_info.previous_salary,
            professional_info.last_increment,
            professional_info.skills,
            professional_info.performance_rating,
            rank() OVER (PARTITION BY professional_info.department ORDER BY professional_info.current_salary DESC) AS dept_rank
           FROM public.professional_info) sub
  WHERE (dept_rank = 1);


ALTER VIEW public.top_earners_per_department OWNER TO hradmin;

--
-- Name: employee emp_id; Type: DEFAULT; Schema: public; Owner: hradmin
--

ALTER TABLE ONLY public.employee ALTER COLUMN emp_id SET DEFAULT nextval('public.employee_emp_id_seq'::regclass);


--
-- Name: salary_log log_id; Type: DEFAULT; Schema: public; Owner: hradmin
--

ALTER TABLE ONLY public.salary_log ALTER COLUMN log_id SET DEFAULT nextval('public.salary_log_log_id_seq'::regclass);


--
-- Name: employee employee_pkey; Type: CONSTRAINT; Schema: public; Owner: hradmin
--

ALTER TABLE ONLY public.employee
    ADD CONSTRAINT employee_pkey PRIMARY KEY (emp_id);


--
-- Name: professional_info professional_info_pkey; Type: CONSTRAINT; Schema: public; Owner: hradmin
--

ALTER TABLE ONLY public.professional_info
    ADD CONSTRAINT professional_info_pkey PRIMARY KEY (emp_id);


--
-- Name: salary_log salary_log_pkey; Type: CONSTRAINT; Schema: public; Owner: hradmin
--

ALTER TABLE ONLY public.salary_log
    ADD CONSTRAINT salary_log_pkey PRIMARY KEY (log_id);


--
-- Name: idx_current_salary; Type: INDEX; Schema: public; Owner: hradmin
--

CREATE INDEX idx_current_salary ON public.professional_info USING btree (current_salary);


--
-- Name: idx_department; Type: INDEX; Schema: public; Owner: hradmin
--

CREATE INDEX idx_department ON public.professional_info USING btree (department);


--
-- Name: idx_rating; Type: INDEX; Schema: public; Owner: hradmin
--

CREATE INDEX idx_rating ON public.professional_info USING btree (performance_rating);


--
-- Name: professional_info trg_log_delete; Type: TRIGGER; Schema: public; Owner: hradmin
--

CREATE TRIGGER trg_log_delete BEFORE DELETE ON public.professional_info FOR EACH ROW EXECUTE FUNCTION public.log_professional_delete();


--
-- Name: professional_info trg_salary_update; Type: TRIGGER; Schema: public; Owner: hradmin
--

CREATE TRIGGER trg_salary_update AFTER UPDATE ON public.professional_info FOR EACH ROW EXECUTE FUNCTION public.log_salary_update();


--
-- Name: professional_info professional_info_emp_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: hradmin
--

ALTER TABLE ONLY public.professional_info
    ADD CONSTRAINT professional_info_emp_id_fkey FOREIGN KEY (emp_id) REFERENCES public.employee(emp_id);


--
-- Name: salary_log salary_log_emp_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: hradmin
--

ALTER TABLE ONLY public.salary_log
    ADD CONSTRAINT salary_log_emp_id_fkey FOREIGN KEY (emp_id) REFERENCES public.employee(emp_id);


--
-- PostgreSQL database dump complete
--

