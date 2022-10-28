import psycopg2
from flask import Flask, render_template, request

app = Flask(__name__)
connect = psycopg2.connect("dbname=tutorial user=postgres password=5877")
cur = connect.cursor()


@app.route('/')
def main():
    return render_template("main.html")


@app.route('/return', methods=['post'])
def re_turn():
    return render_template("main.html")


@app.route('/print_table', methods=['post'])
def print_table():
    cur.execute("SELECT * from users;")
    result = cur.fetchall()

    return render_template("print_table.html",users=result)


@app.route('/register', methods=['post'])
def register():
    id = request.form["id"]
    password = request.form["password"]
    send = request.form["send"]

    cur.execute("SELECT * from users;")
    result = cur.fetchall()

    if (send == "login"):
        for i in result:
            if i[0] == id and i[1] == password:
                return render_template("login_success.html")


        return render_template("login_fail.html")
    else:

        for i in result:
            if i[0] == id:
                return render_template("ID_collision.html")
            else:
                cur.execute("INSERT INTO users VALUES('{}', '{}');".format(id, password))
                connect.commit()
                return render_template("sign_up_success.html")


if __name__ == '__main__':
    app.run()
    
