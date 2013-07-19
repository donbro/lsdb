-- Rule: insert_strings ON strings

-- DROP RULE insert_strings ON strings;

CREATE OR REPLACE RULE insert_strings AS
    ON INSERT TO strings
   WHERE (EXISTS ( SELECT 1
           FROM strings
          WHERE strings.string::text = new.string::text)) DO INSTEAD  SELECT strings.str_id, 
    strings.string, strings.str_ts
   FROM strings
  WHERE strings.string::text = new.string::text;
