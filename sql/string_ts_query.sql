/* file: "string_ts_query.sql" */


CREATE or replace 
FUNCTION string_ts_query(fullname text, pipeterms text)
RETURNS 
TABLE(name text,  len integer, string_id character varying(8), sub_match numeric , rank float4 , super_name text)
AS
$BODY$

select 
    a.string as name , 
    length(a.string) as len,
    a.string_id,
    case when fullname ilike '%' || a.string || '%' then 1.0 else 0.0 end as sub_match ,
    ts_rank_cd(a.string_ts, query, 8) AS rank ,
    b.string as super_name

--"select b.string as super_name from names_ids, strings b where names_ids.string_id = '" & string_id & "' and super_name_id = b.string_id;"

from 
    strings a
    LEFT OUTER JOIN names_ids
                 ON a.string_id      = names_ids.string_id,
    to_tsquery(pipeterms) query,
    --names_ids, 
    strings b

--INNER JOIN strings a, names_ids ON (names_ids.string_id = a.string_id)
where 
    query @@ a.string_ts
    -- and names_ids.string_id = a.string_id
    and super_name_id = b.string_id
order by 
    sub_match desc, rank desc, len desc

-- limit 10;


--CREATE FUNCTION dup(int) RETURNS TABLE(f1 int, f2 text)
--    AS $$ SELECT $1, CAST($1 AS text) || ' is text' $$
--        LANGUAGE SQL;


/*
  new.string_ts :=
     setweight(to_tsvector('pg_catalog.english', coalesce(new.title,'')), 'A') ||
     setweight(to_tsvector('pg_catalog.english', coalesce(new.body,'')), 'D');
*/

$BODY$
LANGUAGE SQL; -- 'plpgsql' VOLATILE;

