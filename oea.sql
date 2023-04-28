DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS programs;
DROP TABLE IF EXISTS modules;
DROP TABLE IF EXISTS program_status;
DROP TABLE IF EXISTS assessment_status;

CREATE TABLE users (user_id INTEGER, user_name TEXT, user_email TEXT, user_status TEXT);

CREATE TABLE programs (program_id TEXT, program_name TEXT, program_description TEXT, program_availability TEXT);

CREATE TABLE modules (module_id TEXT, program_id TEXT, module_name TEXT, content_type TEXT, content_link TEXT, module_index INTEGER);

CREATE TABLE program_status (user_id INTEGER, program_id TEXT, user_program_status TEXT);

CREATE TABLE assessment_status (user_id INTEGER, module_id TEXT, user_assessment_status INTEGER);

INSERT INTO users (user_id, user_name, user_email, user_status) VALUES (1, 'oeadevuser', 'oeadevuser@gmail.com', 'admin');
INSERT INTO users (user_id, user_name, user_email, user_status) VALUES (2, 'oeadevuser-student', 'oeadevuser@gmail.com', 'student');

INSERT INTO programs (program_id, program_name, program_description, program_availability) VALUES ('p1', 'Tree Ambassador 101', 'Description', 'all');
INSERT INTO program_status (user_id, program_id, user_program_status) VALUES (2, 'p1', 'available');

INSERT INTO modules (module_id, program_id, module_name, content_type, content_link, module_index) VALUES ('m1', 'p1', 'M1 Instructions', 'text', 'https://docs.google.com/document/d/1PP-GiTqVcvJYpqVUxQ_bXSsru6H200l39RovL0AhYgw/edit?usp=sharing', 1);
INSERT INTO modules (module_id, program_id, module_name, content_type, content_link, module_index) VALUES ('m2', 'p1', 'Module 1 Learning Exercise', 'assessment', 'https://docs.google.com/forms/d/e/1FAIpQLScGFPXzgFiIaIc5R7NQW_OvINY7y7xc4UHHhIIkt-4AJ-TZoQ/viewform', 2);

INSERT INTO assessment_status(user_id, module_id, user_assessment_status) VALUES (2, 'm2', 0);

