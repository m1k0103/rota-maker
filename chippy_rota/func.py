import sqlite3

class Database:
    def __init__(self,database):
        self.database = database

    def add_employee(self,name,surname): # untested
        con = sqlite3.connect(self.database)
        cursor = con.cursor()
        cursor.execute("INSERT INTO employees(name,surname,max_shifts) VALUES (?,?,0)", [name,surname])
        cursor.execute("INSERT INTO shifts(employee_id, day,start_time,end_time) VALUES ((SELECT eid FROM employees WHERE name=?),?,?,?)",[name,"none","none","none"])
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
        result = [list(tup) for tup in cursor.execute("SELECT name,surname,max_shifts FROM employees").fetchall()]
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
        cursor.execute("INSERT INTO shifts(employee_id,day,start_time,end_time) VALUES ((SELECT eid FROM employees WHERE name=?),?,?,?)",[name,"none,","none","none"])
        con.commit()
        con.close()
    
    def remove_shift(self,shift_id):
        con = sqlite3.connect(self.database)
        cursor = con.cursor()  
        cursor.execute("DELETE FROM shifts WHERE shift_id=?",[shift_id])
        con.commit()
        con.close()

    def update_availability(self,name):
        con = sqlite3.connect(self.database)
        cursor = con.cursor()     

    def update_max_shifts(self,name,new_max_amount):
        con = sqlite3.connect(self.database)
        cursor = con.cursor()
        cursor.execute("UPDATE employees SET max_shifts=? WHERE name=?",[new_max_amount,name])
        con.commit()
        con.close()


    def generate_shift_from_av(self,all_employee_av): # al_employee_av must be type LIST
        # [[employee_name,employee_surname,3,"11:00-15:00","","","16:00-20:00","",""]]
        # 2D list
        #  - each list will be data of an employee
        #  - index 0 will be employee name and index 1 employee surname, index 2 the max shifts to generate for the employee, 
        #    followed by indexes 3 to 8 which will be hours from monday to saturday
        pass