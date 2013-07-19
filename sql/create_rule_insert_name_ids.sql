/* create_rule_insert_name_ids */

-- DROP RULE insert_strings ON strings;


-- name_ids (
--   name_str_id, 
--   supername_str_id, 
--   name_id, 
-- )

CREATE OR REPLACE RULE insert_name_ids AS
    ON INSERT TO name_ids
   WHERE (EXISTS ( SELECT 1
           FROM name_ids
          WHERE 
            name_ids.name_str_id::text = new.name_str_id::text
            and name_ids.supername_str_id::text = new.supername_str_id::text
          )) DO INSTEAD  
  SELECT name_ids.name_str_id, 
    name_ids.supername_str_id, name_ids.name_id
   FROM name_ids
  WHERE name_ids.name_str_id::text = new.name_str_id::text
            and name_ids.supername_str_id::text = new.supername_str_id::text
            ;
