-- file: "path_from_name_id.sql"

drop function path_from_name_id( string_id text);

CREATE FUNCTION path_from_name_id( string_id text) RETURNS VARCHAR AS $$

        SELECT '::' || path FROM
--        SELECT * FROM
        (

            WITH RECURSIVE pathto(path,  id) AS (
                /* non-recursive term  */
                SELECT 'non-recursive: '||CAST (strings.string AS text),  names_ids.super_name_id 
                    FROM names_ids, strings 
                    WHERE names_ids.string_id = $1 
                    and names_ids.string_id = strings.string_id
                UNION
                /* recursive term  (here the recursive term can contain a reference to the query's own output. ) */
                SELECT pathto.path || ':' || strings.string ,  names_ids.super_name_id
                    FROM names_ids, pathto , strings
                    WHERE names_ids.string_id = pathto.id
                    and names_ids.string_id = strings.string_id
            )

            SELECT * FROM pathto

        ) AS pathto(path,  id)

        --WHERE id = 1
        ;

        $$ 
        LANGUAGE 'sql';


/*
The general form of a recursive WITH query is 
    a non-recursive term, then 
    UNION (or UNION ALL), then 
    a recursive term, where only the recursive term can contain a reference to the query's own output. 

Such a query is executed as follows:

Evaluate the non-recursive term. For UNION (but not UNION ALL), discard duplicate rows. Include all remaining rows in the result of the recursive query, and also place them in a temporary working table.

So long as the working table is not empty, repeat these steps:

Evaluate the recursive term, substituting the current contents of the working table for the recursive self-reference. For UNION (but not UNION ALL), discard duplicate rows and rows that duplicate any previous result row. Include all remaining rows in the result of the recursive query, and also place them in a temporary intermediate table.

Replace the contents of the working table with the contents of the intermediate table, then empty the intermediate table.

WITH RECURSIVE included_parts(sub_part, part, quantity) AS (
    SELECT sub_part, part, quantity FROM parts WHERE part = 'our_product'
  UNION ALL
    SELECT p.sub_part, p.part, p.quantity
    FROM included_parts pr, parts p
    WHERE p.part = pr.sub_part
  )
SELECT sub_part, SUM(quantity) as total_quantity
FROM included_parts
GROUP BY sub_part

*/


/*
             Table "names_ids"

 string_id     | character varying(10) | not null
 super_name_id | character varying(10) | 
 name_seq_no   | smallint              | 
 name_id       | character varying(8)  | not null

             Table "strings"

 string_id | character varying(10)  | not null
 string    | character varying(256) | not null
 string_ts | tsvector               | 

*/
