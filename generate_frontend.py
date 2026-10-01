import os

controller_dir = r"backend\src\main\java\com\college\clubmanagement\controller"
template_dir = r"backend\src\main\resources\templates"

os.makedirs(controller_dir, exist_ok=True)
os.makedirs(template_dir, exist_ok=True)

controller_code = """package com.college.clubmanagement.controller;

import com.college.clubmanagement.entity.Club;
import com.college.clubmanagement.repository.ClubRepository;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

import java.util.List;

@Controller
public class DashboardController {

    private final ClubRepository clubRepository;

    public DashboardController(ClubRepository clubRepository) {
        this.clubRepository = clubRepository;
    }

    @GetMapping("/")
    public String viewDashboard(Model model) {
        List<Club> allClubs = clubRepository.findAll();
        model.addAttribute("clubs", allClubs);
        return "dashboard";
    }
}
"""

dashboard_html = """<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <title>College Club Management</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">

<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container">
        <a class="navbar-brand" href="/">Club Management System</a>
        <div class="collapse navbar-collapse">
            <ul class="navbar-nav ms-auto">
                <li class="nav-item">
                    <a class="nav-link active" href="/">Dashboard</a>
                </li>
            </ul>
        </div>
    </div>
</nav>

<div class="container mt-5">
    <h2 class="mb-4">Welcome to the Student Dashboard</h2>
    
    <div class="row">
        <!-- Display Clubs dynamically from Database -->
        <div class="col-md-4 mb-4" th:each="club : ${clubs}">
            <div class="card h-100 shadow-sm">
                <div class="card-body">
                    <h5 class="card-title text-primary" th:text="${club.name}">Club Name</h5>
                    <p class="card-text">
                        <strong>Council:</strong> <span th:text="${club.council != null ? club.council.name : 'N/A'}"></span><br>
                        <strong>Recruiting:</strong> 
                        <span th:if="${club.isRecruiting}" class="badge bg-success">Yes</span>
                        <span th:unless="${club.isRecruiting}" class="badge bg-secondary">No</span>
                    </p>
                    <a href="#" class="btn btn-outline-primary btn-sm">View Details</a>
                    <a href="#" th:if="${club.isRecruiting}" class="btn btn-primary btn-sm">Apply Now</a>
                </div>
            </div>
        </div>
        
        <!-- Empty state -->
        <div class="col-12" th:if="${clubs.isEmpty()}">
            <div class="alert alert-info">
                No clubs are currently registered in the database.
            </div>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

with open(os.path.join(controller_dir, "DashboardController.java"), "w") as f:
    f.write(controller_code)

with open(os.path.join(template_dir, "dashboard.html"), "w") as f:
    f.write(dashboard_html)

print("Generated DashboardController.java and dashboard.html")
