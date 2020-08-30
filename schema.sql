
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS courses CASCADE;
DROP TABLE IF EXISTS pages CASCADE;
DROP TABLE IF EXISTS assignments CASCADE;
DROP TABLE IF EXISTS content;
DROP TABLE IF EXISTS course_rights;
DROP TABLE IF EXISTS options;
DROP TABLE IF EXISTS progression;


CREATE TABLE users (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT, security_level INTEGER);
CREATE TABLE courses (id SERIAL PRIMARY KEY, title TEXT, owner INTEGER, created_at TIMESTAMP, visible BOOLEAN, content TEXT);
CREATE TABLE pages (id SERIAL PRIMARY KEY, title TEXT, content TEXT, course_id INTEGER REFERENCES courses ON DELETE CASCADE, modified TIMESTAMP, visible BOOLEAN);
CREATE TABLE assignments (id SERIAL PRIMARY KEY, title TEXT, assignment TEXT, type TEXT, answer INTEGER, course_id INTEGER, page_id INTEGER, order_number INTEGER);
CREATE TABLE content (content TEXT, course_id INTEGER REFERENCES courses ON DELETE CASCADE, page_id INTEGER REFERENCES PAGES ON DELETE CASCADE, order_number INTEGER, content_type TEXT);
CREATE TABLE course_rights (course_id INTEGER REFERENCES courses ON DELETE CASCADE, user_id INTEGER, can_read BOOLEAN);
CREATE TABLE options (id SERIAL PRIMARY KEY, option TEXT, question_id INTEGER REFERENCES assignments ON DELETE CASCADE, option_id INTEGER);
CREATE TABLE progression (assignment_id INTEGER, user_id INTEGER REFERENCES users ON DELETE CASCADE, answer_id INTEGER, correct BOOLEAN);
