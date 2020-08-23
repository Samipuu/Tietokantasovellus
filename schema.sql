CREATE TABLE assignments (id SERIAL PRIMARY KEY, title TEXT, assignment TEXT, type TEXT, answer INTEGER, course_id INTEGER, page_id INTEGER, order_number INTEGER);
CREATE TABLE content (content TEXT, course_id INTEGER, page_id INTEGER, order_number INTEGER, content_type TEXT);
CREATE TABLE course_rights (course_id INTEGER, user_id INTEGER, can_read BOOLEAN);
CREATE TABLE courses (id SERIAL PRIMARY KEY, title TEXT, owner INTEGER, created_ad TIMESTAMP, visible BOOLEAN, content TEXT);
CREATE TABLE options (id SERIAL PRIMARY KEY, option TEXT, question_id INTEGER, option_id INTEGER);
CREATE TABLE pages (id SERIAL PRIMARY KEY, title TEXT, content TEXT, course_id INTEGER, modified TIMESTAMP, visible BOOLEAN);
CREATE TABLE progreassion (assignment_id INTEGER, user_id INTEGER, answer_id INTEGER, correct BOOLEAN);
CREATE TABLE users (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT, security_level INTEGER);
