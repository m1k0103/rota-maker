import sqlite3
import os
import yaml

def get_db_name():
    with open("config.yaml") as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)
        DB_NAME = conf["database_name"]
        return DB_NAME
    
def get_admin_details():
    with open("config.yaml", "r") as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)
        ADMIN_USERNAME = conf["admin_username"]
        ADMIN_PASSWORD = conf["admin_password"]
        ADMIN_SURNAME = conf["admin_surname"]
        return ADMIN_USERNAME, ADMIN_SURNAME, ADMIN_PASSWORD


def start():
    #creates the config.yaml file
    if "config.yaml" not in os.listdir():
        data = dict(admin_username='ADMIN',
                    admin_surname='admin',
                    admin_password='AdminPassword1234',
                    database_name='database.db')
        with open("config.yaml", "w+") as cfg:
            yaml.dump(data,cfg,default_flow_style=False)
    else:
        pass

    DB_NAME = get_db_name()

    if DB_NAME not in os.listdir():
        db = open(f"./{DB_NAME}", "w+")
        db.close()

        con = sqlite3.connect(DB_NAME)
        cursor = con.cursor()
    
        cursor.execute("""CREATE TABLE employees(
                       eid INTEGER PRIMARY KEY,
                       name TEXT,
                       surname TEXT
                       )""")
        cursor.execute("""CREATE TABLE availability(
                       employee_id INT,
                       day TEXT,
                       start_time TEXT,
                       end_time TEXT,
                       shift_id INTEGER PRIMARY KEY,
                       FOREIGN KEY (employee_id) REFERENCES employees(eid)
                       )""")
        con.commit()

        # creates default admin details
        ADMIN_USER,ADMIN_SURNAME,ADMIN_PASSWORD = get_admin_details()
        cursor.execute("INSERT INTO employees(name,surname) VALUES (?,?)", [ADMIN_USER,ADMIN_SURNAME])

        con.commit()
        con.close()
        print("db created")

    from chippy_rota.routes import app
    app.run(host="0.0.0.0", port="5000",debug=True)