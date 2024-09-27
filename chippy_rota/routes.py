from flask import Flask, request, session, render_template, url_for, redirect
from chippy_rota.func import Database
from chippy_rota.__init__ import get_db_name


app = Flask(__name__)
app.secret_key = "secret_and_secure_key" # not secure

DB = Database(get_db_name())


@app.route("/",methods=["GET","POST"])
def index():
    if request.method == "GET":
        all_employees = DB.get_all_employees()        
        return render_template("index.html", employee_list=all_employees)

@app.route("/make_employee",methods=["POST"])
def make_employee():
    name = request.form["name"]
    surname = request.form["surname"]
    DB.add_employee(name,surname)
    return redirect(url_for("index"))

@app.route("/remove_employee",methods=["POST"])
def remove_employee():
    name = request.form["name"]
    surname = request.form["surname"]
    DB.remove_employee(name,surname)
    return redirect(url_for("index"))

@app.route("/get_employee_shifts", methods=["POST"])
def get_employee_shifts():
    rjson = request.json
    employee_name = rjson["employee_name"]
    shifts = DB.get_shift_info(employee_name)
    print(shifts)
    return render_template("employee_shifts.html",name=employee_name,shifts=shifts)

@app.route("/update_shifts",methods=["POST"])
def update_shifts():
    shift_id = request.form["shift_id"]
    from_time = request.form["from_time"]
    to_time = request.form["to_time"]
    date = request.form["date"]
    name = request.form["employee_name"]
    DB.update_shifts(id=shift_id,name=name,to_time=to_time,from_time=from_time,day=date)
    return redirect(url_for("index"))

@app.route("/create_shift", methods=["POST"])
def create_shift():
    name = request.form["name"]
    DB.create_blank_shift(name)
    return redirect(url_for("index"))

@app.route("/remove_shift", methods=["POST"])
def remove_shift():
    shift_id = request.json["shift_id"]
    DB.remove_shift(shift_id)
    return redirect(url_for("index"))

@app.route("/add_availability", methods=["POST"])
def add_availability():
    rjson = request.json
    employee_name = rjson["employee_name"]
    return render_template("employee_availability.html", name=employee_name)

@app.route("/update_availability", methods=["POST"])
def update_availability():
    days = [request.form["mon"],request.form["tue"],request.form["wed"],request.form["thu"],request.form["fri"],request.form["sat"]]
    start = [request.form["monStart"],request.form["tueStart"],request.form["wedStart"],request.form["thuStart"],request.form["friStart"],request.form["satStart"]]
    end = [request.form["monStart"],request.form["tueStart"],request.form["wedStart"],request.form["thuStart"],request.form["friStart"],request.form["satStart"]]
    time_range = [f"{start[i]-end[i]}" for i in range(len(start))]
    selected_days = []
    for day in days:
        if day == True:
            selected_days.append([index(day),day,time_range[index(day)]])
    print(selected_days) # CARRY ON FROM HERE
    




@app.route("/max_shifts", methods=["POST"])
def max_shifts():
    if "stage2" in request.form:
        name = request.form["name"]
        amount = request.form["max-shifts-input"]
        DB.update_max_shifts(name,amount)
        return redirect(url_for("index"))
        
    else:
        name = request.json["employee_name"]
        return render_template("max_shifts.html",name=name)


def generate_rota_message():
    pass