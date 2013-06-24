/* file: "create_rule_insert_strings.sql" */

--
-- Name: my_table_on_duplicate_ignore; Type: RULE; Schema: public; Owner: donb
--

drop rule if exists insert_strings on strings;

CREATE RULE insert_strings AS 
ON INSERT TO strings 

WHERE (
    EXISTS (
        SELECT 1 FROM strings WHERE (
                (strings.string)::text = (new.string)::text
                )
            )
      ) 

DO INSTEAD 

SELECT 
    strings.str_id , 
    strings.string,
    strings.str_ts,
    'rule on insert dup' as source
FROM 
    strings 
WHERE ((strings.string)::text = (new.string)::text);


