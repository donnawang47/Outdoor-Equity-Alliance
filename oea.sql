SELECT
	pg_terminate_backend(pg_stat_activity.pid)
FROM
	pg_stat_activity
WHERE
	pg_stat_activity.datname = 'oea'
	AND pid <> pg_backend_pid();

DROP TABLE IF EXISTS users;
CREATE TABLE users (user_id INTEGER GENERATED ALWAYS AS IDENTITY, user_name TEXT DEFAULT NULL, user_email TEXT DEFAULT NULL, user_status TEXT);

DROP TABLE IF EXISTS programs;
CREATE TABLE programs (program_id TEXT, program_name TEXT DEFAULT NULL, description TEXT DEFAULT NULL, program_availability TEXT DEFAULT 'none');

DROP TABLE IF EXISTS modules;
CREATE TABLE modules (module_id TEXT, program_id TEXT, module_name TEXT, content_type TEXT, content_link TEXT, module_index INTEGER);

