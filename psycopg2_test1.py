import psycopg2

connect = psycopg2.connect("dbname=tutorial user=junsun password=0000")
cur = connect.cursor()  # create cursor

cur.execute(
    "CREATE TABLE users (id varchar(20), password varchar(20), primary key(id));")
cur.execute("INSERT INTO users VALUES('hyubjinlee', '0000');")

id = 'database'
password = 'postgres'
cur.execute("INSERT INTO users VALUES('{}', '{}');".format(id, password))

connect.commit()  # you must use connect.commit() when write data to PostgreSQL
