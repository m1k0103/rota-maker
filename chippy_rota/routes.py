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

@app.route("/get_employee_details", methods=["POST"])
def get_employee_details():
    rjson = request.json
    employee_name = rjson["employee_name"]
    shifts = DB.get_shift_info(employee_name)
    print(shifts)
    return render_template("employee_details.html",name=employee_name,shifts=shifts)

@app.route("/update_rota",methods=["POST"])
def update_rota():
    shift_id = request.form["shift_id"]
    from_time = request.form["from_time"]
    to_time = request.form["to_time"]
    date = request.form["date"]
    name = request.form["employee_name"]
    DB.update_rota(id=shift_id,name=name,to_time=to_time,from_time=from_time,day=date)
    return redirect(url_for("index"))

@app.route("/create_shift", methods=["POST"])
def create_shift():
    name = request.form["name"]
    DB.create_blank_shift(name)
    return redirect(url_for("index"))

def generate_rota_message():
    pass