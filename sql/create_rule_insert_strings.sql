/* file: "create_rule_insert_strings.sql" */

--
-- Name: my_table_on_duplicate_ignore; Type: RULE; Schema: public; Owner: donb
--

drop rule if exists insert_strings on strings;

/*
    For ON INSERT rules, the original query (if not suppressed by INSTEAD) is done before any actions added by rules. 
 */

CREATE RULE insert_strings AS 
ON INSERT TO strings 


/* this qualification turns the INSERT on or off
    if the row exists or not.  Thus the duplicate entry exception
    never happens. */

WHERE (
    EXISTS (
        SELECT 1 FROM strings WHERE (
                (strings.string)::text = (new.string)::text and hey_there() 
                )
            )
      ) 


/* if we did "where true" here, the insert would never happen 
    and for a new insertion the select would not find a matching row. */
DO INSTEAD 
/* if this whole rule is "thrown into" the rewrite system 
    again, ie after the insert, then, afterwards, the exists 
    would be true, which is what we see. */
(
SELECT 
    strings.str_id , 
    strings.string,
    strings.str_ts,
    'rule on insert dup' as source
FROM 
    strings 
WHERE ((strings.string)::text = (new.string)::text);
--select 'hi' as groink;
)

/* at this point, "new" hasn't been through the trigger,
    so get the already inserted record(s) from the table
    which have been through the trigger. */


