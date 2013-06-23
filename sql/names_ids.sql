--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: names_ids; Type: TABLE; Schema: public; Owner: donb; Tablespace: 
--

CREATE TABLE names_ids (
    string_id character varying(8) NOT NULL,
    super_name_id character varying(8),
    name_seq_no smallint,
    name_id character varying(8) NOT NULL
);


ALTER TABLE public.names_ids OWNER TO donb;

--
-- Data for Name: names_ids; Type: TABLE DATA; Schema: public; Owner: donb
--

COPY names_ids (string_id, super_name_id, name_seq_no, name_id) FROM stdin;
\.


--
-- Name: names_pkey1; Type: CONSTRAINT; Schema: public; Owner: donb; Tablespace: 
--

ALTER TABLE ONLY names_ids
    ADD CONSTRAINT names_pkey1 PRIMARY KEY (name_id);


--
-- Name: names_insert_before; Type: TRIGGER; Schema: public; Owner: donb
--

CREATE TRIGGER names_insert_before BEFORE INSERT ON names_ids FOR EACH ROW EXECUTE PROCEDURE create_function_name_id();


--
-- PostgreSQL database dump complete
--

