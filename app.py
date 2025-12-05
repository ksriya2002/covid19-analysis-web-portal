from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId
import random
import plotly.graph_objs as go
from plotly.offline import plot

app = Flask(__name__)

# ✅ MongoDB connection
client = MongoClient("mongodb+srv://covidadmin:covid123@covidcluster.ewmllvf.mongodb.net/?retryWrites=true&w=majority",
                    tls=True,
                    tlsAllowInvalidCertificates=True)
db = client["covid_mitigation_db"]

# Convert all citizen_id values to int
for doc in db["Citizens"].find():
    try:
        cid = int(doc["citizen_id"])
        db["Citizens"].update_one(
            {"_id": doc["_id"]},
            {"$set": {"citizen_id": cid}}
        )
    except Exception as e:  
        print(f"Skipped document {doc['_id']}: {e}")

@app.route("/")
def home():
    # Chart 1: Vaccine Type Distribution (Pie Chart)
    vaccine_data = db["Vaccinations"].aggregate([
        {"$group": {"_id": "$vaccine_type", "count": {"$sum": 1}}}
    ])
    labels1, values1 = [], []
    for item in vaccine_data:
        labels1.append(item["_id"])
        values1.append(item["count"])
    fig1 = go.Figure(data=[go.Pie(
        labels=labels1,
        values=values1,
        hoverinfo='label+value+percent',
        textinfo='label+percent',
        marker=dict(line=dict(color='#000000', width=1))
    )])
    fig1.update_layout(title="Vaccine Type Distribution")
    chart1 = plot(fig1, output_type="div", include_plotlyjs=False)

    # Chart 2: Citizen Count by State (Bar Chart)
    state_data = db["Citizens"].aggregate([
        {"$group": {"_id": "$state", "count": {"$sum": 1}}}
    ])
    labels2, values2 = [], []
    for item in state_data:
        labels2.append(item["_id"])
        values2.append(item["count"])
    fig2 = go.Figure([go.Bar(
        x=labels2,
        y=values2,
        text=values2,
        textposition='outside',
        marker_color='rgba(54, 162, 235, 0.7)',
        hovertemplate='State: %{x}<br>Citizens: %{y}<extra></extra>'
    )])
    fig2.update_layout(
        title="Citizen Count by State",
        xaxis_title="State",
        yaxis_title="Citizens",
        yaxis=dict(dtick=1)
    )
    chart2 = plot(fig2, output_type="div", include_plotlyjs=False)

    # Chart 3: Vaccine Dose Distribution (Grouped Bar Chart)
    dose_data = db["Vaccinations"].aggregate([
        {"$group": {"_id": {"dose": "$dose_number", "type": "$vaccine_type"}, "count": {"$sum": 1}}}
    ])
    dose_mapping = {}
    for entry in dose_data:
        dose = str(entry["_id"]["dose"])
        vaccine = entry["_id"]["type"]
        count = entry["count"]
        if vaccine not in dose_mapping:
            dose_mapping[vaccine] = {}
        dose_mapping[vaccine][dose] = count

    doses = sorted({d for v in dose_mapping.values() for d in v})
    traces = []
    for vaccine, dose_counts in dose_mapping.items():
        y_values = [dose_counts.get(d, 0) for d in doses]
        traces.append(go.Bar(name=vaccine, x=doses, y=y_values))

    fig3 = go.Figure(data=traces)
    fig3.update_layout(
        title="Vaccine Dose Count by Type",
        xaxis_title="Dose Number",
        yaxis_title="Count",
        barmode='group'
    )
    chart3 = plot(fig3, output_type="div", include_plotlyjs=False)

    return render_template("home.html", chart1=chart1, chart2=chart2, chart3=chart3)

# -------------------- Citizens --------------------
# View all citizens
@app.route("/citizens")
def view_citizens():
    citizens = list(db["Citizens"].find().sort("citizen_id", 1))
    return render_template("citizens.html", citizens=citizens)

# Add new citizen
@app.route("/citizen/add", methods=["POST"])
def add_citizen():
    data = request.form
    new_citizen = {
        "citizen_id": int(data["citizen_id"]),
        "first_name": data["first_name"],
        "last_name": data["last_name"],
        "age": int(data["age"]),
        "gender": data["gender"],
        "state": data["state"],
        "country": data["country"]
    }
    db["Citizens"].insert_one(new_citizen)
    return redirect(url_for("view_citizens"))

# Edit citizen
@app.route("/citizen/edit/<int:citizen_id>", methods=["GET", "POST"])
def edit_citizen(citizen_id):
    if request.method == "POST":
        data = request.form
        db["Citizens"].update_one(
            {"citizen_id": citizen_id},
            {"$set": {
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "age": int(data["age"]),
                "gender": data["gender"],
                "state": data["state"],
                "country": data["country"]
            }}
        )
        return redirect(url_for("view_citizens"))

    citizen = db["Citizens"].find_one({"citizen_id": citizen_id})
    if not citizen:
        return f"No citizen found with ID {citizen_id}", 404
    return render_template("edit_citizen.html", citizen=citizen)

# Delete citizen
@app.route("/citizen/delete/<int:citizen_id>")
def delete_citizen(citizen_id):
    db["Citizens"].delete_one({"citizen_id": citizen_id})
    return redirect(url_for("view_citizens"))

# -------------------- Vaccinations --------------------
@app.route("/vaccinations")
def view_vaccinations():
    vaccinations = list(db["Vaccinations"].find())
    return render_template("vaccinations.html", vaccinations=vaccinations)

@app.route("/vaccination/add", methods=["POST"])
def add_vaccination():
    data = request.form
    new_vaccination = {
        "citizen_id": data["citizen_id"],
        "vaccine_type": data["vaccine_type"],
        "dose_number": int(data["dose_number"]),
        "date_administered": data["date_administered"],
        "administered_by": data["administered_by"],
        "location": data["location"]
    }
    db["Vaccinations"].insert_one(new_vaccination)
    return redirect(url_for("view_vaccinations"))

@app.route("/vaccination/edit/<id>", methods=["GET", "POST"])
def edit_vaccination(id):
    if request.method == "POST":
        data = request.form
        db["Vaccinations"].update_one({"_id": ObjectId(id)}, {
            "$set": {
                "citizen_id": data["citizen_id"],
                "vaccine_type": data["vaccine_type"],
                "dose_number": int(data["dose_number"]),
                "date_administered": data["date_administered"],
                "administered_by": data["administered_by"],
                "location": data["location"]
            }
        })
        return redirect(url_for("view_vaccinations"))

    # 🔴 This line is crucial
    vaccination = db["Vaccinations"].find_one({"_id": ObjectId(id)})
    return render_template("edit_vaccination.html", vaccination=vaccination)


@app.route("/vaccination/delete/<id>")
def delete_vaccination(id):
    db["Vaccinations"].delete_one({"_id": ObjectId(id)})
    return redirect(url_for("view_vaccinations"))



# -------------------- COVID Cases --------------------
@app.route("/covid_cases")
def view_covid_cases():
    covid_cases = list(db["COVID_Cases"].find())
    return render_template("covid_cases.html", covid_cases=covid_cases)

@app.route("/covid_case/add", methods=["POST"])
def add_covid_case():
    data = request.form
    new_case = {
        "citizen_id": data["citizen_id"],
        "date_positive": data["date_positive"],
        "severity": data["severity"],
        "hospitalized": data["hospitalized"],
        "recovery_status": data["recovery_status"],
        "date_updated": data["date_updated"]
    }
    db["COVID_Cases"].insert_one(new_case)
    return redirect(url_for("view_covid_cases"))

@app.route("/covid_case/edit/<id>", methods=["GET", "POST"])
def edit_covid_case(id):
    if request.method == "POST":
        data = request.form
        db["COVID_Cases"].update_one({"_id": ObjectId(id)}, {
            "$set": {
                "citizen_id": data["citizen_id"],
                "date_positive": data["date_positive"],
                "severity": data["severity"],
                "hospitalized": data["hospitalized"],
                "recovery_status": data["recovery_status"],
                "date_updated": data["date_updated"]
            }
        })
        return redirect(url_for("view_covid_cases"))

    case = db["COVID_Cases"].find_one({"_id": ObjectId(id)})
    return render_template("edit_covid_case.html", case=case)

@app.route("/covid_case/delete/<id>")
def delete_covid_case(id):
    db["COVID_Cases"].delete_one({"_id": ObjectId(id)})
    return redirect(url_for("view_covid_cases"))


# -------------------- Hospitals --------------------
@app.route("/hospitals")
def view_hospitals():
    hospitals = list(db["Hospitals"].find())
    return render_template("hospitals.html", hospitals=hospitals)

@app.route("/hospital/add", methods=["POST"])
def add_hospital():
    data = request.form
    new_hospital = {
        "name": data["name"],
        "location": data["location"],
        "capacity": int(data["capacity"]),
        "available_beds": int(data["available_beds"]),
        "contact_info": data["contact_info"]
    }
    db["Hospitals"].insert_one(new_hospital)
    return redirect(url_for("view_hospitals"))

@app.route("/hospital/edit/<id>", methods=["GET", "POST"])
def edit_hospital(id):
    if request.method == "POST":
        data = request.form
        db["Hospitals"].update_one({"_id": ObjectId(id)}, {
            "$set": {
                "name": data["name"],
                "location": data["location"],
                "capacity": int(data["capacity"]),
                "available_beds": int(data["available_beds"]),
                "contact_info": data["contact_info"]
            }
        })
        return redirect(url_for("view_hospitals"))

    hospital = db["Hospitals"].find_one({"_id": ObjectId(id)})
    return render_template("edit_hospital.html", hospital=hospital)

@app.route("/hospital/delete/<id>")
def delete_hospital(id):
    db["Hospitals"].delete_one({"_id": ObjectId(id)})
    return redirect(url_for("view_hospitals"))

# -------------------- Testing Centers --------------------
@app.route("/testing_centers")
def view_testing_centers():
    testing_centers = list(db["Testing_Centers"].find())
    return render_template("testing_centers.html", testing_centers=testing_centers)

@app.route("/testing_center/add", methods=["POST"])
def add_testing_center():
    data = request.form
    new_center = {
        "name": data["name"],
        "location": data["location"],
        "test_type": data["test_type"],
        "test_date": data["test_date"],
        "citizen_id": data["citizen_id"],
        "result": data["result"],
        "administered_by": data["administered_by"]
    }
    db["Testing_Centers"].insert_one(new_center)
    return redirect(url_for("view_testing_centers"))

@app.route("/testing_center/edit/<id>", methods=["GET", "POST"])
def edit_testing_center(id):
    if request.method == "POST":
        data = request.form
        db["Testing_Centers"].update_one({"_id": ObjectId(id)}, {
            "$set": {
                "name": data["name"],
                "location": data["location"],
                "test_type": data["test_type"],
                "test_date": data["test_date"],
                "citizen_id": data["citizen_id"],
                "result": data["result"],
                "administered_by": data["administered_by"]
            }
        })
        return redirect(url_for("view_testing_centers"))

    center = db["Testing_Centers"].find_one({"_id": ObjectId(id)})
    return render_template("edit_testing_center.html", center=center)

@app.route("/testing_center/delete/<id>")
def delete_testing_center(id):
    db["Testing_Centers"].delete_one({"_id": ObjectId(id)})
    return redirect(url_for("view_testing_centers"))


# -------------------- Awareness Programs --------------------
@app.route("/awareness_programs")
def view_awareness_programs():
    programs = list(db["Awareness_Programs"].find())
    return render_template("awareness_programs.html", programs=programs)

@app.route("/awareness_program/add", methods=["POST"])
def add_awareness_program():
    data = request.form
    participants = [p.strip() for p in data["participants"].split(",")]
    new_program = {
        "name": data["name"],
        "date": data["date"],
        "location": data["location"],
        "description": data["description"],
        "conducted_by": data["conducted_by"],
        "participants": participants
    }
    db["Awareness_Programs"].insert_one(new_program)
    return redirect(url_for("view_awareness_programs"))
@app.route("/awareness_program/edit/<id>", methods=["GET", "POST"])
def edit_awareness_program(id):
    if request.method == "POST":
        data = request.form
        participants = [p.strip() for p in data["participants"].split(",")]
        db["Awareness_Programs"].update_one({"_id": ObjectId(id)}, {
            "$set": {
                "name": data["name"],
                "date": data["date"],
                "location": data["location"],
                "description": data["description"],
                "conducted_by": data["conducted_by"],
                "participants": participants
            }
        })
        return redirect(url_for("view_awareness_programs"))

    program = db["Awareness_Programs"].find_one({"_id": ObjectId(id)})
    return render_template("edit_awareness_program.html", program=program)

@app.route("/awareness_program/delete/<id>")
def delete_awareness_program(id):
    db["Awareness_Programs"].delete_one({"_id": ObjectId(id)})
    return redirect(url_for("view_awareness_programs"))


# -------------------- Insights Queries --------------------
@app.route("/insight/vaccinated_tested_awareness")
def vaccinated_tested_awareness():
    selected_state = request.args.get("state")
    citizens = {str(c["citizen_id"]): c for c in db["Citizens"].find()}
    vaccinated_ids = {str(v["citizen_id"]) for v in db["Vaccinations"].find()}
    negative_test_ids = {str(t["citizen_id"]) for t in db["Testing_Centers"].find({"result": "Negative"})}

    result = []
    for program in db["Awareness_Programs"].find():
        for participant_id in program.get("participants", []):
            if participant_id in vaccinated_ids and participant_id in negative_test_ids:
                citizen = citizens.get(participant_id)
                if citizen and (not selected_state or citizen["state"] == selected_state):
                    result.append({
                        "First Name": citizen["first_name"],
                        "Last Name": citizen["last_name"],
                        "Program Name": program["name"],
                        "Test Result": "Negative",
                        "Vaccination Status": "Vaccinated"
                    })

    all_states = sorted(set(c["state"] for c in citizens.values()))

    return render_template("insight_table.html", title="Vaccinated, Tested Negative, and Attended Awareness Program",
                           data=result, states=all_states, selected_state=selected_state)

@app.route("/insight/hospital_positive_cases")
def hospital_positive_cases():
    selected_state = request.args.get("state")
    citizens = {str(c["citizen_id"]): c for c in db["Citizens"].find()}
    hospitalized_case_ids = {str(c["citizen_id"]) for c in db["COVID_Cases"].find({"hospitalized": "Yes"})}
    hospitals = list(db["Hospitals"].find())

    result = []
    for test in db["Testing_Centers"].find({"result": "Positive"}):
        citizen_id = str(test["citizen_id"])
        if citizen_id in hospitalized_case_ids:
            citizen = citizens.get(citizen_id)
            if citizen and (not selected_state or citizen["state"] == selected_state):
                random_hospital = random.choice(hospitals)
                result.append({
                    "First Name": citizen["first_name"],
                    "Last Name": citizen["last_name"],
                    "Hospital Name": random_hospital["name"],
                    "Available Beds": random_hospital["available_beds"]
                })

    all_states = sorted(set(c["state"] for c in citizens.values()))

    return render_template("insight_table.html", title="Hospitals Treating Positive Cases",
                           data=result, states=all_states, selected_state=selected_state)

@app.route("/insight/positive_hospitalized_vaccine")
def positive_hospitalized_vaccine():
    selected_vaccine = request.args.get("vaccine")
    citizens = {str(c["citizen_id"]): c for c in db["Citizens"].find()}
    hospitalized_case_ids = {str(c["citizen_id"]) for c in db["COVID_Cases"].find({"hospitalized": "Yes"})}

    result = []
    for vax in db["Vaccinations"].find():
        citizen_id = str(vax["citizen_id"])
        if citizen_id in hospitalized_case_ids:
            citizen = citizens.get(citizen_id)
            if citizen and (not selected_vaccine or vax["vaccine_type"] == selected_vaccine):
                result.append({
                    "First Name": citizen["first_name"],
                    "Last Name": citizen["last_name"],
                    "Vaccine Type": vax["vaccine_type"],
                    "Dose Number": vax["dose_number"],
                    "Hospitalized": "Yes"
                })

    all_vaccines = sorted(set(v["vaccine_type"] for v in db["Vaccinations"].find()))

    return render_template("insight_table.html", title="Positive, Hospitalized, and Vaccinated Citizens",
                           data=result, vaccines=all_vaccines, selected_vaccine=selected_vaccine)

@app.route("/insight/vaccinated_then_positive")
def vaccinated_then_positive():
    selected_state = request.args.get("state")
    citizens = {str(c["citizen_id"]): c for c in db["Citizens"].find()}
    vaccinated_ids = {str(v["citizen_id"]) for v in db["Vaccinations"].find()}

    result = []
    for test in db["Testing_Centers"].find({"result": "Positive"}):
        citizen_id = str(test.get("citizen_id"))
        if citizen_id in vaccinated_ids:
            citizen = citizens.get(citizen_id)
            if citizen and (not selected_state or citizen["state"] == selected_state):
                result.append({
                    "First Name": citizen["first_name"],
                    "Last Name": citizen["last_name"],
                    "State": citizen["state"],
                    "Test Date": test["test_date"],
                    "Test Result": test["result"],
                    "Vaccination Status": "Vaccinated"
                })

    all_states = sorted(set(c["state"] for c in citizens.values()))

    return render_template("insight_table.html", title="Vaccinated Citizens Who Tested Positive",
                           data=result, states=all_states, selected_state=selected_state)

# -------------------- Run App --------------------
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5001)


