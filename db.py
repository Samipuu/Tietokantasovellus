from app import app
from flask_sqlalchemy import SQLAlchemy
from os import getenv

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

def get_courses():
	result = db.session.execute("SELECT * FROM courses")
	courses = result.fetchall()
	return courses

def create_course(title, content):
	sql = "INSERT INTO courses (title, content, created_at) VALUES (:title, :content, NOW()) RETURNING id"
	result = db.session.execute(sql, {"title":title, "content":content})
	db.session.commit()
	course_id = result.fetchone()[0]
	return course_id

def create_course_page(title, content, course_id, qtitle, answer, answeropt, question):
	sql = "INSERT INTO pages (title, course_id, modified) VALUES (:title, :course_id, NOW()) RETURNING ID"
	result = db.session.execute(sql, {"title":title, "course_id":course_id})
	page_id = result.fetchone()[0]
	i = 0
	x = 0
	for assignment in qtitle:
		sql = "INSERT INTO assignments (title, answer, course_id, page_id) VALUES (:title, :answer, :course_id, :page_id) RETURNING ID"
		question_id = db.session.execute(sql, {"title":assignment, "answer":answer[x], "course_id":course_id, "page_id":page_id})
		qid = question_id.fetchone()[0]
		x += 1
		for y in range(x-1, x*3-1):
			option = str(answeropt[y])
			sql = "INSERT INTO options (option, question_id) VALUES :option, :question_id"
			db.session.execute(sql, {"option":option, "question_id":qid})
	for text in content:
		print (text)
		i += 1
		sql = "INSERT INTO content (content, course_id, page_id, order_number) VALUES (:content, :course_id, :page_id, :order_number)"
		db.session.execute(sql, {"content":text, "course_id":course_id, "page_id":page_id, "order_number":i})
	db.session.commit()
	return page_id	

def get_course(id):
	sql = "SELECT title, content FROM courses WHERE id=:id"
	result = db.session.execute(sql, {"id":id})
	list = result.fetchall()
	return list

def get_materials(id):
	sql = "SELECT title, id FROM pages WHERE course_id=:id"
	result = db.session.execute(sql, {"id":id})
	materials = result.fetchall()
	return materials

def get_material(course_id, page_id):
	sql = "SELECT c.content, title, order_number FROM content C LEFT JOIN pages P ON C.course_id=P.course_id AND C.page_id = P.id WHERE C.course_id=:course_id AND page_id=:page_id"
	result = db.session.execute(sql, {"course_id":course_id, "page_id":page_id})
	materials = result.fetchall()
	print(materials)
	return materials


