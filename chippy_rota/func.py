import sqlite3
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

class Database:
    def __init__(self,database):
        self.database = database

    def add_employee(self,name,surname): # untested
        con = sqlite3.connect(self.database)
        cursor = con.cursor()
        cursor.execute("INSERT INTO employees(name,surname) VALUES (?,?)", [name,surname])
        cursor.execute("INSERT INTO availability(employee_id,mon,tue,wed,thu,fri,sat,sun,max_shifts,max_hours) VALUES ((SELECT eid FROM employees WHERE name=? AND surname=?),'','','','','','','',0,0)",[name,surname])
        con.commit()
        con.close()
        return True
 
    def remove_employee(self,name,surname):
        con = sqlite3.connect(self.database)
        cursor = con.cursor()
        cursor.execute("DELETE FROM shifts WHERE employee_id=(SELECT eid FROM employees WHERE name=? AND surname=?)",[name,surname]) # deletes from shifts table
        cursor.execute("DELETE FROM availability WHERE employee_id=(SELECT eid FROM employees WHERE name=? AND surname=?)",[name,surname]) # deletes from availability table
        cursor.execute("DELETE FROM employees WHERE name=? AND surname=?",[name,surname]) # then finally deletes from employee table
        con.commit()
        con.close()
        return True

    def get_all_employees(self):
        con = sqlite3.connect(self.database)
        cursor = con.cursor()
        result = [list(tup) for tup in cursor.execute("SELECT name,surname FROM employees").fetchall()]
        con.close()
        return result

    def get_shift_info(self,name):
        con = sqlite3.connect(self.database)
        cursor = con.cursor()
        shift_data = [list(tup) for tup in cursor.execute("SELECT shift_id,day,start_time,end_time FROM shifts WHERE employee_id=(SELECT eid FROM employees WHERE name=?)",[name]).fetchall()]
        con.close()
        return shift_data
    
    def update_shifts(self,id,name,to_time,from_time,day):
        con = sqlite3.connect(self.database)
        cursor = con.cursor()
        cursor.execute("UPDATE shifts SET day=?,start_time=?,end_time=? WHERE employee_id=(SELECT eid FROM employees WHERE name=?) AND shift_id=?",[day,from_time,to_time,name,id])
        con.commit()
        con.close()
        return True
    
    def create_blank_shift(self,name):
        con = sqlite3.connect(self.database)
        cursor = con.cursor()
        cursor.execute("INSERT INTO shifts(employee_id,day,start_time,end_time) VALUES ((SELECT eid FROM employees WHERE name=?),?,?,?)",[name,"","",""])
        con.commit()
        con.close()
    
    def remove_shift(self,shift_id):
        con = sqlite3.connect(self.database)
        cursor = con.cursor()  
        cursor.execute("DELETE FROM shifts WHERE shift_id=?",[shift_id])
        con.commit()
        con.close()

    def update_availability(self,days,start,end,name,surname): 
        time_range = [f"{start[i]}-{end[i]}" for i in range(len(start))]
        con = sqlite3.connect(self.database)
        cursor = con.cursor()
        
        # RESETS ALL DAYS TO HAVE NO VALUE
        cursor.execute(f"UPDATE availability SET mon='',tue='',wed='',thu='',fri='',sat='' WHERE employee_id=(SELECT eid FROM employees WHERE name=? AND surname=?)",[name,surname])

        for i in range(len(days)):
            cursor.execute(f"UPDATE availability SET {days[i]}=? WHERE employee_id=(SELECT eid FROM employees WHERE name=? AND surname=?)",[time_range[i],name,surname])
        con.commit() # some error here. maybe use executemany from sqlite3??
        con.close()

    def update_max_shifts(self,name,new_max_amount):
        con = sqlite3.connect(self.database)
        cursor = con.cursor()
        cursor.execute("UPDATE availability SET max_shifts=? WHERE employee_id=(SELECT eid FROM employees WHERE name=?)",[new_max_amount,name])
        con.commit()
        con.close()

    def update_max_hours(self,name,new_max):
        con = sqlite3.connect(self.database)
        cursor = con.cursor()
        cursor.execute("UPDATE availability SET max_hours=? WHERE employee_id=(SELECT eid FROM employees WHERE name=?)",[new_max, name])
        con.commit()
        con.close()

    def get_all_availability_for_table(self):
        con = sqlite3.connect(self.database)
        cursor = con.cursor()
        result = [list(tup) for tup in cursor.execute("SELECT employee_id,mon,tue,wed,thu,fri,sat,max_shifts,max_hours FROM availability").fetchall()]
        for record in result:
            record[0] = " ".join(cursor.execute("SELECT name,surname FROM employees WHERE eid=?",[record[0]]).fetchall()[0])
        con.commit()
        con.close()
        return result

    def get_all_shifts_for_table(self):
        con = sqlite3.connect(self.database)
        cursor = con.cursor()
        # carry on from here
        result = [list(tup) for tup in cursor.execute("SELECT employee_id,day,start_time,end_time FROM shifts").fetchall()]
        new=[]
        for record in result:
            record[0] = "".join(cursor.execute("SELECT name,surname FROM employees WHERE eid=?",[record[0]]).fetchall()[0])
            record[2] = f"{record[2]}-{record[3]}"
            del record[3]
            new.append(record)
        con.close()
        return new
    # Make it so it reads the day from the stored value, then aligns it with the index a list so that
    # it can be aligned with the table on the index.html page.

    def get_user_availability(self,name,surname):
        con = sqlite3.connect(self.database)
        cursor = con.cursor()
        result = cursor.execute("SELECT mon,tue,wed,thu,fri,sat FROM availability WHERE employee_id=(SELECT eid FROM employees WHERE name=? AND surname=?)",[name,surname]).fetchall()[0]
        return result

    def name_surname_to_eid(self,name,surname):
        con = sqlite3.connect(self.database)
        cursor = con.cursor()
        eid = cursor.execute("SELECT eid FROM employees WHERE name=? AND surname=?",[name,surname]).fetchall()[0][0]
        con.close()
        return eid

    def eid_to_name_surname(self,eid):
        con = sqlite3.connect(self.database)
        cursor = con.cursor()
        name_surname = cursor.execute("SELECT name,surname FROM employees WHERE eid=?",eid).fetchall()[0]
        return name_surname

    def generate_shifts_from_availability(self): 
        con = sqlite3.connect(self.database)
        cursor = con.cursor()
        all_availability = self.get_all_availability()

        for availability in all_availability:
            max_shifts = availability[7:]
            #shifts = []
            #all_days = [availability[3:]] # includes all days including 
            #available_days = [day for day in all_days if day != ""]
            #for j in range(len(max_shifts)):
            #    shifts.append() # need to also add max hours to employees. :/ aj aj aj
    
        
        # al_employee_av must be type LIST
        # [[employee_name,employee_surname,"11:00-15:00","","","16:00-20:00","","",3]]
        # 2D list
        #  - each list will be data of an employee
        #  - index 0 will be employee name and index 1 employee surname, index 2 the max shifts to generate for the employee, 
        #    followed by indexes 3 to 8 which will be hours from monday to saturday
        pass