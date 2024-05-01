from flask import Flask, render_template, request, url_for, make_response, send_file, redirect
import sqlite3

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
    f.write(f'fontsize: {request.cookies.get('fontsize')}\nfontcolor: {request.cookies.get('fontcolor')}')
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

if __name__ == '__main__':
    # app.run(host='172.17.5.139', port=5000)
    app.run(host='127.0.0.1', port=4000)
    url_for('static', filename='gradesdatabase.dumpfilesql')
