import psycopg2
from flask import Flask, render_template, request

app = Flask(__name__)
connect = psycopg2.connect("dbname=tradingsite user=junsun password=0000")
cur = connect.cursor()  # create cursor

current_user = ["", "", ""]  # [id, balance, rating]
best = ["", "", ""]  # best [category, buyer, seller]
selected_item = ["", "", "", "", ""]  # [code, name, price, stock, seller]


@ app.route('/')
def main():
    return render_template("main.html")


@ app.route('/return', methods=['post'])
def re_turn():
    return render_template("main.html")


@ app.route('/login_success', methods=['post'])
def re_turn_login_success():
    return render_template("login_success.html")


@ app.route('/print_table', methods=['post'])
def print_table():
    cur.execute("SELECT * FROM users;")
    result = cur.fetchall()

    return render_template("print_table.html", users=result)


@ app.route('/register', methods=['post'])
def register():
    id = request.form["id"]
    password = request.form["password"]
    send = request.form["send"]
    current_user[0] = request.form["id"]

    cur.execute("SELECT * FROM users;")
    result = cur.fetchall()
    if send == "login":
        login = False
        for user in result:
            if user[0] == id and user[1] == password:
                login = True
                break
        if login:
            cur.execute("SELECT * FROM items;")
            items = cur.fetchall()
            cur.execute(
                "select n.type, count(*) as best from (select b.type from trades a inner join category b on a.code = b.code ) as n group by n.type order by best desc limit 1;")
            best_category = cur.fetchall()
            best[0] = best_category[0][0]
            cur.execute(
                "select buyer, sum(trade_price) from trades group by buyer order by sum(trade_price) desc")
            best_buyer = cur.fetchall()
            best[1] = best_buyer[0][0]
            cur.execute(
                "select seller, sum(trade_price) from trades group by seller order by sum(trade_price) desc")
            best_seller = cur.fetchall()
            best[2] = best_seller[0][0]
            cur.execute(
                "select balance, rating from account where id='{}';".format(id))
            user_info = cur.fetchall()
            current_user[1] = user_info[0][0]
            current_user[2] = user_info[0][1]
            return render_template("login_success.html", items=items, current_user=current_user, best=best)
        else:
            return render_template("login_fail.html")
    else:  # sign up
        success = True
        for user in result:
            if id == user[0]:
                success = False
                break
        if success:
            cur.execute(
                "INSERT INTO users VALUES('{}', '{}');".format(id, password))
            cur.execute(
                "INSERT INTO account VALUES('{}', 10000, 'beginner');".format(id))
            connect.commit()
            return render_template("sign_up_success.html")
        else:
            return render_template("ID_collision.html")


@ app.route('/admin_function', methods=['post'])
def admin_function():
    send = request.form["send"]

    if send == "users info":
        cur.execute(
            "SELECT a.id, a.password, b.balance, b.rating FROM users a INNER JOIN account b ON a.id=b.id;")
        users = cur.fetchall()
        return render_template("print_users.html", users=users)
    elif send == "trades info":
        cur.execute("SELECT * FROM trades;")
        trades = cur.fetchall()
        return render_template("print_trades.html", trades=trades)


@ app.route('/item_add', methods=['post'])
def item_add():
    send = request.form["add"]
    if send == "add":
        cur.execute("SELECT * FROM category;")
        category = cur.fetchall()
        return render_template("item_add.html", category=category)


@ app.route('/return_to_register', methods=['post'])
def return_to_register():
    send = request.form["send"]
    if send == "return" or send == "cancel":
        cur.execute("SELECT * FROM items;")
        items = cur.fetchall()
        return render_template("login_success.html", items=items,
                               current_user=current_user, best=best)
    elif send == "add":
        code = request.form["code"]
        name = request.form["name"]
        price = request.form["price"]
        stock = request.form["stock"]
        cur.execute("SELECT * FROM items")
        items = cur.fetchall()
        find = False
        for item in items:
            if item[0] == code and item[1] == name and item[2] == int(price) and item[4] == current_user[0]:
                find = True
                stock = int(stock) + item[3]
                stock = str(stock)
                cur.execute("UPDATE items SET stock={} WHERE code='{}' and name='{}' and price={} and seller='{}'".format(
                    stock, code, name, price, current_user[0]))
                connect.commit()
                break
        if not find:
            cur.execute("INSERT INTO items VALUES('{}', '{}', {}, {}, '{}');".format(
                code, name, price, stock, current_user[0]))
            connect.commit()
        cur.execute("SELECT * FROM items;")
        items = cur.fetchall()
        return render_template("login_success.html", items=items,
                               current_user=current_user, best=best)


@ app.route('/item_buy', methods=['post'])
def item_buy():
    selected_item[0] = request.form["code"]
    selected_item[1] = request.form["name"]
    selected_item[2] = request.form["price"]
    selected_item[3] = request.form["stock"]
    selected_item[4] = request.form["seller"]
    if current_user[0] == selected_item[4]:
        return render_template("error.html", current_user=current_user, message="자신의 물건은 구매할 수 없습니다.", page="return_to_register")
    return render_template("item_buy.html", item=selected_item, current_user=current_user)


@ app.route('/item_buying', methods=['post'])
def item_buying():
    send = request.form["send"]
    if send == "buy":
        cur.execute(
            "select rating from account where id='{}'".format(current_user[0]))
        rating = cur.fetchall()
        cur.execute(
            "select discount from rating_info where rating='{}'".format(rating[0][0]))
        discount = cur.fetchall()
        stock = int(request.form["stock"])
        total_price = stock*int(selected_item[2])
        discount_price = stock * \
            int(selected_item[2])*float((discount[0][0])/100)
        seller = request.form["seller"]
        price = request.form["price"]
        if stock > int(selected_item[3]):
            return render_template("error.html", current_user=current_user, message="개수가 부족합니다.", page="return_to_item_buy")
        elif total_price > float(current_user[1]):
            return render_template("error.html", current_user=current_user, message="잔액이 부족합니다."+str(stock*int(selected_item[2])*(100-float(discount[0][0])))+str(float(current_user[1])), page="return_to_item_buy")
        else:
            return render_template("confirm_buying.html", current_user=current_user, total_price=total_price, discount_price=discount_price, stock=stock, seller=seller)

    elif send == "cancel":
        cur.execute("SELECT * FROM items;")
        items = cur.fetchall()
        return render_template("login_success.html", items=items,
                               current_user=current_user, best=best)


@ app.route('/return_to_item_buy', methods=['post'])
def return_to_item_buy():
    return render_template("item_buy.html", item=selected_item, current_user=current_user)


@ app.route('/confirm_buying', methods=['post'])
def confirm_buying():
    send = request.form["send"]
    # 0일때 삭제 구현하기
    if send == "confirm":

        cur.execute(
            "select rating from account where id='{}'".format(current_user[0]))
        rating = cur.fetchall()
        cur.execute(
            "select discount from rating_info where rating='{}'".format(rating[0][0]))
        discount = cur.fetchall()
        stock = int(request.form["stock"])
        total_price = stock*int(selected_item[2])
        discount_price = stock * \
            int(selected_item[2])*(((100-float(discount[0][0]))/100))

        new_balance = str(
            float(current_user[1])-stock*int(selected_item[2])*(((100-float(discount[0][0]))/100)))
        cur.execute("UPDATE account SET balance={} WHERE id='{}'".format(
            new_balance, current_user[0]))

        seller = request.form["seller"]
        cur.execute("UPDATE account SET balance=balance+{} WHERE id='{}'".format(
            total_price, seller))

        cur.execute(
            "SELECT balance FROM account WHERE id='{}'".format(current_user[0]))
        cur_balance = cur.fetchall()
        cur.execute(
            "SELECT balance FROM account WHERE id='{}'".format(seller))
        sel_balance = cur.fetchall()
        cur.execute(
            "SELECT rating, condition FROM rating_info ORDER BY condition desc")
        conditions = cur.fetchall()
        for condition in conditions:
            if int(condition[1]) <= float(cur_balance[0][0]):
                cur.execute("UPDATE account SET rating='{}' WHERE id='{}'".format(
                    condition[0], current_user[0]))
                break
        for condition in conditions:
            if int(condition[1]) <= float(sel_balance[0][0]):
                cur.execute("UPDATE account SET rating='{}' WHERE id='{}'".format(
                    condition[0], seller))
                break

        cur.execute("SELECT stock FROM items WHERE code='{}' and name='{}' and price={} and seller='{}'".format(
            selected_item[0], selected_item[1], selected_item[2], seller))
        cur_stock = cur.fetchall()[0][0]

        cur.execute("INSERT INTO trades VALUES('{}', '{}', '{}', {});".format(
            current_user[0], seller, selected_item[0], total_price))

        if int(cur_stock)-stock == 0:
            cur.execute("DELETE FROM items WHERE code='{}' and name='{}' and price={} and seller='{}'".format(
                selected_item[0], selected_item[1], selected_item[2], seller))
        else:
            cur.execute("UPDATE items SET stock=stock-{} WHERE code='{}' and name='{}' and price={} and seller='{}'".format(
                stock, selected_item[0], selected_item[1], selected_item[2], seller))

        connect.commit()
        cur.execute("SELECT * FROM items;")
        items = cur.fetchall()
        cur.execute(
            "select balance, rating from account where id='{}';".format(current_user[0]))
        user_info = cur.fetchall()
        current_user[1] = user_info[0][0]
        current_user[2] = user_info[0][1]
        cur.execute(
            "select n.type, count(*) as best from (select b.type from trades a inner join category b on a.code = b.code ) as n group by n.type order by best desc limit 1;")
        best_category = cur.fetchall()
        best[0] = best_category[0][0]
        cur.execute(
            "select buyer, sum(trade_price) from trades group by buyer order by sum(trade_price) desc")
        best_buyer = cur.fetchall()
        best[1] = best_buyer[0][0]
        cur.execute(
            "select seller, sum(trade_price) from trades group by seller order by sum(trade_price) desc")
        best_seller = cur.fetchall()
        best[2] = best_seller[0][0]
        return render_template("login_success.html", current_user=current_user, best=best, items=items)
    elif send == "cancel":
        return render_template("item_buy.html", current_user=current_user, item=selected_item)


if __name__ == '__main__':
    app.run(debug=True)
