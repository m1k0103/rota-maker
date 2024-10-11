import sqlite3
import yaml
import calendar
import random
import math
import datetime

def date_to_week_day(date):
    try:
        year,month,day = [int(i) for i in date.split('-')]
    except:
        return ""
    day_num = calendar.weekday(year,month,day)
    days = ["mon","tue","wed","thu","fri","sat"]
    return days[day_num]

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

    def create_shift_gen(self,name,day,start_time,end_time):
        con = sqlite3.connect(self.database)
        cur = con.cursor()
        cur.execute("INSERT INTO shifts(employee_id,day,start_time,end_time) VALUES ((SELECT eid FROM employees WHERE name=?),?,?,?)",[name,day,start_time,end_time])
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
        result = [list(tup) for tup in cursor.execute("SELECT employee_id,day,start_time,end_time FROM shifts").fetchall()] # all employee data
        
        days = ["mon","tue","wed","thu","fri","sat"]
        for_table = []
        
        for i in range(len(result)):
            namesurname = result[i][0] = " ".join(list(cursor.execute("SELECT name,surname FROM employees WHERE eid=?",[result[i][0]]).fetchall()[0]))
            if len(result[i][1]) == 3:
                stored_day = result[i][1]
            else:
                stored_day = date_to_week_day(result[i][1])
            timerange = f"{result[i][2]}-{result[i][3]}"
        
            for_table.append([namesurname,"","","","","",""])
            if stored_day == '':
                pass
            else:
                for_table[i][days.index(stored_day)+1] = timerange
        con.close()
        return for_table


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
        days = ["mon","tue","wed","thu","fri","sat"]

        con = sqlite3.connect(self.database)
        cursor = con.cursor()
        cursor.execute("DELETE FROM shifts")
        con.commit()
        con.close()

        all_availability = self.get_all_availability_for_table()

        for emp_av in all_availability:
            em_name = emp_av[0].split(" ")[0]
            print(em_name)
            em_max_hours = emp_av[8]
            remaining_shift_hours = datetime.timedelta(hours=int(em_max_hours))
            em_max_shifts = emp_av[7]
            try:
                avg_hrs_per_shift = math.ceil(em_max_hours / em_max_shifts)
            except :
                print("not divisible by 0")
                break
            stored_days = emp_av[1:][:-2]
            print(stored_days)
            for i in range(len(stored_days)):
                if stored_days[i] == "": # if no availability for the day, then it skips the day
                    pass
                else: # if availability on the day is present
                    time_range = stored_days[i]
                    avail_start_time, avail_end_time = time_range.split("-")
                    shift_start = str(datetime.timedelta(hours=int(avail_start_time.split(":")[0]),minutes=int(avail_start_time.split(":")[1])))
                    shift_end = str(datetime.timedelta(hours=int(avail_start_time.split(":")[0]),minutes=int(avail_start_time.split(":")[1])) + datetime.timedelta(hours=avg_hrs_per_shift))
                    
                    #make it so that time is subracted
                    shift_length = datetime.datetime.strptime(shift_end, '%H:%M:%S')-datetime.datetime.strptime(shift_start, '%H:%M:%S')
                    if remaining_shift_hours - shift_length == datetime.timedelta(hours=0,minutes=0,days=0):
                        self.create_shift_gen(em_name,days[stored_days.index(stored_days[i])],shift_start, str(datetime.datetime.strptime(shift_start, '%H:%M:%S')+remaining_shift_hours).split(" ")[1])
                        break # replace break with something else. like a jump statement???
                    elif remaining_shift_hours - shift_length < datetime.timedelta(hours=0,minutes=0,days=0):
                        self.create_shift_gen(em_name,days[stored_days.index(stored_days[i])],shift_start,str(datetime.datetime.strptime(shift_end, '%H:%M:%S')+remaining_shift_hours).split(" ")[1])
                        remaining_shift_hours -= shift_length
                        continue
                    elif remaining_shift_hours - shift_length > datetime.timedelta(hours=0,minutes=0,seconds=0):
                        self.create_shift_gen(em_name,days[stored_days.index(stored_days[i])],shift_start,str(datetime.datetime.strptime(shift_start, '%H:%M:%S')+shift_length).split(" ")[1])
                        remaining_shift_hours -= shift_length
                        continue

                    #self.create_shift_gen(em_name,days[stored_days.index(stored_days[i])],shift_start,shift_end)
                    stored_days[i] = "" #sets the day to be nothing in the list just so other shifts can be created properly
        
        # al_employee_av must be type LIST
        # [[eid,"11:00-15:00","","","16:00-20:00","","",3,5]]
        pass