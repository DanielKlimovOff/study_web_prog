from flask import Flask, render_template, request, url_for, make_response, send_file, redirect
import sqlite3
from random import randint

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('index.html')

@app.get('/laba1')
def laba1():
    response = make_response(render_template('laba1.html'))
    print(repr(request.cookies.get('fontsize')), repr(request.cookies.get('fontcolor')))
    # if not request.cookies.get('fontsize'):
    #     response.set_cookie('fontsize', '20', max_age=60*15)
    # if not request.cookies.get('fontcolor'):
    #     response.set_cookie('fontcolor', 'green', max_age=60*15)
    return response

@app.post('/laba1')
def laba1_post():
    fontcolor = request.form['color']
    text = request.form['text']
    space = text.count(' ')
    fontsize = request.form['fontsize']
    response = make_response(render_template('laba1_result.html', 
        text=text, space=space, fontsize=fontsize, fontcolor=fontcolor))
    response.set_cookie('fontsize', fontsize, max_age=60*15)
    response.set_cookie('fontcolor', fontcolor, max_age=60*15)
    return response

@app.get('/clear_cookies')
def clear_cookies():
    response = make_response(render_template('clear_cookies.html'))
    for cookie_name in request.cookies:
        response.set_cookie(cookie_name, '', expires=0)
    return response

@app.get('/save_to_file')
def save_to_file():
    f = open('static/cookies.txt', 'w')
    f.write(f'fontsize: {request.cookies.get("fontsize")}\nfontcolor: {request.cookies.get("fontcolor")}')
    f.close()
    return send_file('static/cookies.txt', as_attachment=True)

@app.get('/laba2')
def laba2():
    connection = sqlite3.connect('grades.db')
    cursor = connection.cursor()

    cursor.execute('select grades.id, students.name, courses.name as course, grades.ticket_number, grades.grade from grades join students on grades.student = students.id join courses on grades.course = courses.id;')
    table = cursor.fetchall()
    connection.commit()
    connection.close()

    response = make_response(render_template('laba2.html', table=table))
    return response


@app.get('/laba2_insert')
def laba2_insert_get():
    connection = sqlite3.connect('grades.db')
    cursor = connection.cursor()

    cursor.execute('select id from students order by id;')
    students = cursor.fetchall()
    cursor.execute('select id from courses order by id;')
    courses = cursor.fetchall()

    connection.commit()
    connection.close()

    students = [x[0] for x in students]
    courses = [x[0] for x in courses]

    response = make_response(render_template('laba2_insert.html', students=students, courses=courses))
    return response

@app.post('/laba2_insert')
def laba2_insert_post():
    connection = sqlite3.connect('grades.db')
    cursor = connection.cursor()

    cursor.execute('select max(id) from grades;')
    max_id_grade = cursor.fetchone()[0]
    print(max_id_grade)
    student = request.form['student']
    course = request.form['course']
    ticket_number = request.form['ticket_number']
    grade = request.form['grade']
    print(f'insert into grades values ({max_id_grade + 1}, {student}, {course}, {ticket_number}, {grade});')

    cursor.execute(f'insert into grades values ({max_id_grade + 1}, {student}, {course}, {ticket_number}, {grade});')

    connection.commit()
    connection.close()

    return redirect('laba2')

@app.get('/laba2_update<int:grade_id>')
def laba2_update_get(grade_id):
    connection = sqlite3.connect('grades.db')
    cursor = connection.cursor()

    cursor.execute('select id from students order by id;')
    students = cursor.fetchall()
    cursor.execute('select id from courses order by id;')
    courses = cursor.fetchall()

    cursor.execute(f'select * from grades where id = {grade_id};')
    grade_info = cursor.fetchone()
    stud_id = grade_info[1]
    course_id = grade_info[2]
    ticket_number_id = grade_info[3]
    grade_id = grade_info[4]

    connection.commit()
    connection.close()

    students = [x[0] for x in students]
    courses = [x[0] for x in courses]

    response = make_response(render_template('laba2_update.html',
     students=students, courses=courses, stud_id=stud_id, course_id=course_id,
      ticket_number_id=ticket_number_id, grade_id=grade_id))
    return response

@app.post('/laba2_update<int:grade_id>')
def laba2_update_post(grade_id):
    connection = sqlite3.connect('grades.db')
    cursor = connection.cursor()

    student = request.form['student']
    course = request.form['course']
    ticket_number = request.form['ticket_number']
    grade = request.form['grade']
    print(f'update grades set student={student}, course={course}'+
        'ticket_number={ticket_number}, grade={grade} where id={grade_id} ;')

    cursor.execute(f'update grades set student={student}, course={course},'+
        f'ticket_number={ticket_number}, grade={grade} where id={grade_id} ;')

    connection.commit()
    connection.close()

    return redirect('laba2')

@app.get('/laba2_delete<int:grade_id>')
def laba2_delete(grade_id):
    connection = sqlite3.connect('grades.db')
    cursor = connection.cursor()

    cursor.execute(f'delete from grades where id = {grade_id};')


    connection.commit()
    connection.close()

    return redirect('laba2')

@app.post('/laba2')
def laba2_select():
    connection = sqlite3.connect('grades.db')
    cursor = connection.cursor()

    where = request.form['select']
    cursor.execute(f'select grades.id, students.name, courses.name as course, grades.ticket_number, grades.grade from grades join students on grades.student = students.id join courses on grades.course = courses.id where {where};')
    table = cursor.fetchall()
    connection.commit()
    connection.close()

    response = make_response(render_template('laba2.html', table=table))
    return response

@app.get('/laba2_enter')
def laba2_enter():
    # if not request.cookies.get('fontsize'):
    
    response = make_response(render_template('laba2_enter.html'))
    return response


@app.post('/laba2_register')
def laba2_register():
    connection = sqlite3.connect('grades.db')
    cursor = connection.cursor()

    cursor.execute('select max(id) from users;')
    max_id = cursor.fetchone()[0]
    login = request.form['login']
    role = request.form['role']
    myhash = randint(1, 1000000)

    cursor.execute(f'insert into users values ({max_id + 1}, "{login}", {role}, {myhash});') 
    
    connection.commit()
    connection.close()

    response = make_response('', 301)
    response.headers['Location'] = 'laba2'
    response.set_cookie('laba2_hash', str(myhash), max_age=60*15)

    return response

@app.post('/laba2_login')
def laba2_login():
    connection = sqlite3.connect('grades.db')
    cursor = connection.cursor()

    login = request.form['login']
    cursor.execute('select login from users;')
    logins = cursor.fetchall()
    logins = [log[0] for log in logins]
    
    response = make_response('', 301)
    response.headers['Location'] = 'laba2'
    if login in logins:
        cursor.execute(f'select hash from users where login = "{login}";')
        myhash = cursor.fetchone()[0]
        response.set_cookie('laba2_hash', str(myhash), max_age=60*15)
        print('i am user', myhash, login)
    else:
        print('i am pussy')
    connection.commit()
    connection.close()
    return redirect('laba2')


if __name__ == '__main__':
    # app.run(host='172.17.5.139', port=5000)
    app.run(host='127.0.0.1', port=4000)
    url_for('static', filename='gradesdatabase.dumpfilesql')
