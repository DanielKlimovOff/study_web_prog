from flask import Flask, render_template, request, url_for

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('index.html')

@app.get('/laba1')
def laba1():
    return render_template('laba1.html')

@app.post('/laba1')
def laba1_post():
    color = request.form['color']
    text = request.form['text']
    space = text.count(' ')
    return render_template('laba1_result.html', 
        color=color, text=text, space=space)

if __name__ == '__main__':
    app.run()
    url_for('static', filename='gradesdatabase.dumpfilesql')