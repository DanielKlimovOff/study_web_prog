from flask import Flask, render_template, request, url_for, make_response, send_file, redirect
import sqlite3
from random import randint
from PIL import Image, ImageDraw, ImageFont
from flask_simple_captcha import CAPTCHA
from flask_ckeditor import CKEditor
import json
#  форма для обратной сзвязи
from forms import ContactForm
import plotly.express as px

YOUR_CONFIG = {
    'SECRET_CAPTCHA_KEY': 'LONG_KEY',
    'CAPTCHA_LENGTH': 6,
    'CAPTCHA_DIGITS': True,
    'EXPIRE_SECONDS': 600,
    'BACKGROUND_COLOR': (255, 255, 255),
    'TEXT_COLOR': (0, 255, 0)
}


app = Flask(__name__)
app.config['SECRET_KEY'] = "12345"
ckeditor = CKEditor(app)

SIMPLE_CAPTCHA = CAPTCHA(config=YOUR_CONFIG)
app = SIMPLE_CAPTCHA.init_app(app)


def skibidi(name):
    connection = sqlite3.connect('grades.db')
    cursor = connection.cursor()

    cursor.execute(f'select count from visits where name = "{name}";')
    count = cursor.fetchone()[0]
    cursor.execute(f'update visits set count = {count + 1} where name = "{name}";')

    connection.commit()
    connection.close()


@app.route('/')
def main():
    skibidi('/')
    return render_template('index.html')

@app.get('/laba1')
def laba1():
    skibidi('/laba1')
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
    text = request.form.get('ckeditor')
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
    skibidi('/laba2')
    if not request.cookies.get('laba2_hash'):
        response = make_response('', 301)
        response.headers['Location'] = 'laba2_enter'
        return response

    connection = sqlite3.connect('grades.db')
    cursor = connection.cursor()

    cursor.execute('select grades.id, students.name, courses.name as course, grades.ticket_number, grades.grade from grades join students on grades.student = students.id join courses on grades.course = courses.id;')
    table = cursor.fetchall()
    myhash = request.cookies.get('laba2_hash')
    cursor.execute(f'select login, role from users where hash={myhash};')
    data = cursor.fetchone()
    login = data[0]
    role = data[1]

    if role == 0:
        role = 'Пользователь'
    elif role == 1:
        role = 'Администратор'
    elif role == 2:
        role = 'Владелец БД'
    else:
        role = 'Аноним'

    connection.commit()
    connection.close()


    response = make_response(render_template('laba2.html', table=table, login=login, role=role))
    return response


@app.get('/laba2_insert')
def laba2_insert_get():
    if not request.cookies.get('laba2_hash'):
        return "Вы не вошли в акаунт, у вас нет прав совершать действия с БД"

    connection = sqlite3.connect('grades.db')
    cursor = connection.cursor()

    myhash = request.cookies.get('laba2_hash')
    cursor.execute(f'select role from users where hash={myhash};')
    role = cursor.fetchone()[0]

    if role < 1:
        return 'Маловато прав у вас'

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
    if not request.cookies.get('laba2_hash'):
        return "Вы не вошли в акаунт, у вас нет прав совершать действия с БД"

    connection = sqlite3.connect('grades.db')
    cursor = connection.cursor()

    myhash = request.cookies.get('laba2_hash')
    cursor.execute(f'select role from users where hash={myhash};')
    role = cursor.fetchone()[0]

    if role < 1:
        return 'Маловато прав у вас'

    cursor.execute('select max(id) from grades;')
    max_id_grade = cursor.fetchone()[0]
    student = request.form['student']
    course = request.form['course']
    ticket_number = request.form['ticket_number']
    grade = request.form['grade']
    cursor.execute(f'insert into grades values ({max_id_grade + 1}, {student}, {course}, {ticket_number}, {grade});')

    connection.commit()
    connection.close()

    return redirect('laba2')

@app.get('/laba2_update<int:grade_id>')
def laba2_update_get(grade_id):
    if not request.cookies.get('laba2_hash'):
        return "Вы не вошли в акаунт, у вас нет прав совершать действия с БД"
    connection = sqlite3.connect('grades.db')
    cursor = connection.cursor()

    myhash = request.cookies.get('laba2_hash')
    cursor.execute(f'select role from users where hash={myhash};')
    role = cursor.fetchone()[0]

    if role < 1:
        return 'Маловато прав у вас'

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
    if not request.cookies.get('laba2_hash'):
        return "Вы не вошли в акаунт, у вас нет прав совершать действия с БД"
    connection = sqlite3.connect('grades.db')
    cursor = connection.cursor()

    myhash = request.cookies.get('laba2_hash')
    cursor.execute(f'select role from users where hash={myhash};')
    role = cursor.fetchone()[0]

    if role < 1:
        return 'Маловато прав у вас'

    student = request.form['student']
    course = request.form['course']
    ticket_number = request.form['ticket_number']
    grade = request.form['grade']
    cursor.execute(f'update grades set student={student}, course={course},'+
        f'ticket_number={ticket_number}, grade={grade} where id={grade_id} ;')

    connection.commit()
    connection.close()

    return redirect('laba2')

@app.get('/laba2_delete<int:grade_id>')
def laba2_delete(grade_id):
    if not request.cookies.get('laba2_hash'):
        return "Вы не вошли в акаунт, у вас нет прав совершать действия с БД"
        
    connection = sqlite3.connect('grades.db')
    cursor = connection.cursor()

    myhash = request.cookies.get('laba2_hash')
    cursor.execute(f'select role from users where hash={myhash};')
    role = cursor.fetchone()[0]

    if role < 2:
        return 'Маловато прав у вас'

    cursor.execute(f'delete from grades where id = {grade_id};')


    connection.commit()
    connection.close()

    return redirect('laba2')

@app.post('/laba2')
def laba2_select():
    if not request.cookies.get('laba2_hash'):
        response = make_response('', 301)
        response.headers['Location'] = 'laba2_enter'
        return response

    connection = sqlite3.connect('grades.db')
    cursor = connection.cursor()

    where = request.form['select']
    cursor.execute(f'select grades.id, students.name, courses.name as course, grades.ticket_number, grades.grade from grades join students on grades.student = students.id join courses on grades.course = courses.id where {where};')
    table = cursor.fetchall()

    myhash = request.cookies.get('laba2_hash')
    cursor.execute(f'select login, role from users where hash={myhash};')
    data = cursor.fetchone()
    login = data[0]
    role = data[1]

    if role == 0:
        role = 'Пользователь'
    elif role == 1:
        role = 'Администратор'
    elif role == 2:
        role = 'Владелец БД'
    else:
        role = 'Аноним'

    connection.commit()
    connection.close()


    response = make_response(render_template('laba2.html', table=table, login=login, role=role))
    return response

@app.get('/laba2_enter')
def laba2_enter():
    response = make_response(render_template('laba2_enter.html'))
    if request.cookies.get('laba2_hash'):
        connection = sqlite3.connect('grades.db')
        cursor = connection.cursor()

        myhash = request.cookies.get('laba2_hash')

        cursor.execute(f'select * from users where hash={myhash};')
        logins = cursor.fetchall()
        print('logins', logins)
        connection.commit()
        connection.close()

        if len(logins):
            response = make_response('', 301)
            response.headers['Location'] = 'laba2'
            return response
        else:
            for cookie_name in request.cookies:
                response.set_cookie(cookie_name, '', expires=0)
    
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
    print(login, logins)
    if login in logins:
        cursor.execute(f'select hash from users where login = "{login}";')
        myhash = cursor.fetchone()[0]
        response.set_cookie('laba2_hash', str(myhash), max_age=60*15)
        print('i am user', myhash, login)
    else:
        print('i am pussy')
    connection.commit()
    connection.close()
    return response

@app.post('/laba2_logout')
def laba2_logout():
    print('logout')
    response = make_response('', 301)
    response.headers['Location'] = 'laba2_enter'
    for cookie_name in request.cookies:
        response.set_cookie(cookie_name, '', expires=0)
    return response

@app.get('/laba3')
def laba3():
    skibidi('/laba3')
    new_captcha_dict = SIMPLE_CAPTCHA.create()
    response = make_response(render_template('laba3.html', captcha=new_captcha_dict))
    return response

@app.post('/laba3')
def laba3_post():
    c_hash = request.form.get('captcha-hash')
    c_text = request.form.get('captcha-text')

    if not SIMPLE_CAPTCHA.verify(c_text, c_hash):
        return f'Капча введена неверно'

    type_diagram = request.form['type_diagram']
    if type_diagram == 'student':
        connection = sqlite3.connect('grades.db')
        cursor = connection.cursor()

        cursor.execute('select DISTINCT students.name from grades join students on grades.student = students.id order by students.name;')
        students = cursor.fetchall()
        students = [s[0] for s in students]
        grades = []

        for stud in students:
            cursor.execute(f'select count(*) from grades join students on grades.student=students.id where students.name = "{stud}";')
            grades.append(cursor.fetchone()[0])

        connection.commit()
        connection.close()

        diagram = Image.new('RGB', (120 + 50 * max(grades), 70 * len(students)), 'white')
        draw = ImageDraw.Draw(diagram)
        font = ImageFont.truetype("static/arial.ttf", size=30)

        for i in range(len(students)):
            draw.rectangle((20, 20 + 70 * i, 50 * grades[i], 50 + 70*i), fill='green')
            draw.text((20, 20 + 70 * i), str(grades[i]) + ' - ' + students[i], font=font, fill='black')

        diagram.save('static/diagram.jpg')
    elif type_diagram == 'course':
        connection = sqlite3.connect('grades.db')
        cursor = connection.cursor()

        cursor.execute('select DISTINCT courses.name from grades join courses on grades.course = courses.id order by courses.name;')
        courses = cursor.fetchall()
        courses = [c[0] for c in courses]
        grades = []

        for cours in courses:
            cursor.execute(f'select count(*) from grades join courses on grades.course = courses.id where courses.name = "{cours}";')
            grades.append(cursor.fetchone()[0])

        print(courses, grades)

        connection.commit()
        connection.close()

        diagram = Image.new('RGB', (120 + 20 * max(grades), 70 * len(courses)), 'white')
        draw = ImageDraw.Draw(diagram)
        font = ImageFont.truetype("static/arial.ttf", size=30)

        for i in range(len(courses)):
            draw.rectangle((20, 20 + 70 * i, 20 * grades[i], 50 + 70*i), fill='green')
            draw.text((20, 20 + 70 * i), str(grades[i]) + ' - ' + courses[i], font=font, fill='black')

        diagram.save('static/diagram.jpg')

    return render_template('laba3_diagram.html')

@app.get('/laba4')
def laba4():
    skibidi('/laba4')
    form = ContactForm()

    return render_template("laba4.html",
                           title="index page",
                           form=form)

@app.route('/laba4send', methods=['POST'])
def send():
    form = ContactForm()
    if request.method == "POST":
        if form.validate_on_submit():
            #  отправить почту, записать в БД и т. д.
            return json.dumps({'success': 'true', 'msg': 'Ждите звонка!'})
        else:
            #  обработать ошибку
            return json.dumps({'success': 'false', 'msg': 'Ошибка на сервере!'})


@app.get('/rgr')
def rgr():
    skibidi('/rgr')

    connection = sqlite3.connect('grades.db')
    cursor = connection.cursor()

    cursor.execute(f'select count from visits;')
    count = cursor.fetchall()
    count = [x[0] for x in count]

    connection.commit()
    connection.close()

    print(count)

    x_data = ['/', '/laba1', '/laba2', '/laba3', '/laba4', '/rgr']
    y_data = count
    
    fig = px.line(x=x_data, y=y_data, title='График посещений страниц моего сайта')

    # Отображаем график на веб-странице
    graph_html = fig.to_html(full_html=False)

    return render_template('graph.html', graph=graph_html)
    # return render_template("laba4.html")

if __name__ == '__main__':
    app.run(host='172.17.5.120', port=5000)
    # app.run(host='127.0.0.1', port=4000)

