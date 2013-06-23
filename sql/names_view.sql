--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

--
-- Name: names; Type: VIEW; Schema: public; Owner: donb
--

CREATE VIEW names AS
    SELECT 
        name_strings.string AS name, 
        super_strings.string AS super_name, 
        names_ids.name_seq_no, 
        names_ids.name_id 
    FROM 
        (
            (strings name_strings JOIN names_ids ON (
                (
                    (name_strings.string_id)::text = (names_ids.string_id)::text)
                )
            ) 
            
            JOIN 
            
            strings super_strings ON (
                (
                    (names_ids.super_name_id)::text = (super_strings.string_id)::text
                )
                    
            )
        );


ALTER TABLE public.names OWNER TO donb;
