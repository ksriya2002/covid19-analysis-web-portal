# COVID-19 Mitigation Analysis Web Portal

A full-stack web application built using **Flask** and **MongoDB** to manage and analyze COVID-19-related information, including citizens, vaccinations, testing centers, hospitals, COVID cases, and awareness programs.  
The portal integrates CRUD functionality, database-driven analytics, and interactive dashboards to support COVID-19 tracking and decision-making.

---

## Project Overview

This system centralizes multiple COVID-19 data sources into a single platform where users can maintain records, analyze trends, and explore meaningful insights.  

The platform is designed as an analytical tool to help users understand vaccination progress, testing outcomes, hospital capacity, and awareness program participation using real-time data stored in MongoDB.

Key functionality includes:
- Maintaining records across six modules (Citizens, Vaccinations, COVID Cases, Hospitals, Testing Centers, Awareness Programs)  
- Visualizing vaccination and demographic trends using Plotly  
- Exploring analytical insights that combine data from multiple collections  
- Reviewing how vaccination status, testing results, and hospitalization patterns relate in real scenarios  

The application follows a modular architecture, separating routes, templates, visualizations, and database operations for clarity and maintainability.

---

## Project Preview

![Home Dashboard](dashboard_images/home_dashboard.png)

---

## Features

### ✔ CRUD Functionality  
Each module includes interfaces for adding, editing, deleting, and viewing records:

- Citizens  
- Vaccinations  
- COVID Cases  
- Hospitals  
- Testing Centers  
- Awareness Programs  

All operations interact directly with MongoDB, ensuring real-time updates across the system.

### ✔ Interactive Visualizations  
Visual charts are rendered using Plotly and include:

- Vaccine type distribution (pie chart)  
- Vaccine dose comparison (grouped bar chart)  

![Vaccine Pie Chart](dashboard_images/vaccine_type_chart.png)

*(Some charts and screens are not included here as screenshots but are available within the live application.)*

---

## Insight Queries

The portal includes several multi-collection insights such as:

### Vaccinated Citizens Who Tested Positive
![Insight](dashboard_images/vaccinated_tested_positive.png)

### Hospitals Treating Positive Cases
![Hospitals Insight](dashboard_images/hospitals_treating_cases.png)

These insights analyze relationships between vaccination records, test results, hospitalization data, and demographic factors.

---

## Technology Used

- **Flask (Python)** – Routing, backend logic  
- **MongoDB Atlas** – NoSQL database  
- **PyMongo** – Database communication  
- **Plotly** – Interactive visualizations  
- **HTML, CSS, Bootstrap** – Frontend UI  
- **Jinja2** – Template rendering  

---

## Folder Structure

```
/app.py
/static
    dashboard.png
/templates
    home.html
    citizens.html
    vaccinations.html
    covid_cases.html
    hospitals.html
    testing_centers.html
    awareness_programs.html
    insight_table.html
    edit_citizen.html
    edit_vaccination.html
    edit_covid_case.html
    edit_hospital.html
    edit_testing_center.html
    edit_awareness_program.html
/dashboard_images
    home_dashboard.png
    citizens_page.png
    vaccine_type_chart.png
    vaccinated_tested_positive.png
    hospitals_treating_cases.png
```

---

## Running the Application

### 1. Install necessary packages
```
pip install flask pymongo plotly dnspython
```

### 2. Add your MongoDB connection string  
Inside `app.py`:
```
client = MongoClient(
    "your_connection_string_here",
    tls=True,
    tlsAllowInvalidCertificates=True
)
db = client["covid_mitigation_db"]
```

### 3. Start the server
```
python3 app.py
```

Application will run at:
```
http://localhost:5001
```

---

## Contributions

My work on this project included:

- Implementing backend routes and CRUD operations for all modules  
- Designing database structure and integrating MongoDB Atlas  
- Creating frontend templates for forms, tables, and navigation  
- Developing Plotly-based dashboards and integrating them into Flask  
- Writing multi-collection insight logic and data filtering  
- Testing, debugging, and ensuring smooth end-to-end functionality  

This repository reflects my implementation work and the final structure of the project.

---

## Disclaimer
Only selected screenshots are included in this README. 
Additional visualizations and insights exist in the full application but are not displayed here for brevity.

---

## Contact

Email: **sriyareddy696@gmail.com**  
Feel free to reach out with any questions or feedback.

