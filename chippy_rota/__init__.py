import sqlite3
import os
import yaml
from chippy_rota.func import Database,get_db_name,get_admin_details

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
        cursor.execute("""CREATE TABLE shifts(
                       employee_id INT,
                       day TEXT,
                       start_time TEXT,
                       end_time TEXT,
                       shift_id INTEGER PRIMARY KEY,
                       FOREIGN KEY (employee_id) REFERENCES employees(eid)
                       )""")
        cursor.execute("""CREATE TABLE availability(
                       employee_id INT,
                       mon TEXT,
                       tue TEXT,
                       wed TEXT,
                       thu TEXT,
                       fri TEXT,
                       sat TEXT,
                       sun TEXT,
                       max_shifts INT,
                       FOREIGN KEY (employee_id) REFERENCES employees(eid)
                       )""")
        con.commit()
        con.close()
        print("db created")

        # creates default admin details
        DB = Database(get_db_name())
        ADMIN_USER,ADMIN_SURNAME,ADMIN_PASSWORD = get_admin_details()
        #DB.add_employee(ADMIN_USER,ADMIN_SURNAME)


    from chippy_rota.routes import app
    app.run(host="0.0.0.0", port="5000",debug=True)