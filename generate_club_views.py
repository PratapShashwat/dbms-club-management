import os

base_dir = r"backend\src\main\java\com\college\clubmanagement"
controller_dir = os.path.join(base_dir, "controller")
template_dir = r"backend\src\main\resources\templates"

# 1. Create ClubController.java
club_controller_code = """package com.college.clubmanagement.controller;

import com.college.clubmanagement.entity.*;
import com.college.clubmanagement.repository.*;
import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

import java.util.List;
import java.util.stream.Collectors;

@Controller
public class ClubController {

    private final ClubRepository clubRepository;
    private final EventRepository eventRepository;
    private final ClubRoomAllocationRepository roomAllocationRepository;
    private final ClubMembershipRepository membershipRepository;
    private final DynamicFormRepository formRepository;

    public ClubController(ClubRepository clubRepository, EventRepository eventRepository,
                          ClubRoomAllocationRepository roomAllocationRepository,
                          ClubMembershipRepository membershipRepository,
                          DynamicFormRepository formRepository) {
        this.clubRepository = clubRepository;
        this.eventRepository = eventRepository;
        this.roomAllocationRepository = roomAllocationRepository;
        this.membershipRepository = membershipRepository;
        this.formRepository = formRepository;
    }

    @GetMapping("/club/{id}")
    public String viewClub(@PathVariable Integer id, Model model, HttpSession session) {
        if (session.getAttribute("USER_ROLL") == null) return "redirect:/login";

        Club club = clubRepository.findById(id).orElseThrow();
        model.addAttribute("club", club);

        // Fetch related data
        List<Event> events = eventRepository.findAll().stream()
                .filter(e -> e.getClub() != null && e.getClub().getClubId().equals(id))
                .collect(Collectors.toList());
        model.addAttribute("events", events);

        List<ClubRoomAllocation> rooms = roomAllocationRepository.findAll().stream()
                .filter(r -> r.getClub() != null && r.getClub().getClubId().equals(id))
                .collect(Collectors.toList());
        model.addAttribute("rooms", rooms);

        List<ClubMembership> pors = membershipRepository.findAll().stream()
                .filter(m -> m.getClub() != null && m.getClub().getClubId().equals(id))
                .filter(m -> m.getRole() != null) // Only show people with a POR Role
                .collect(Collectors.toList());
        model.addAttribute("pors", pors);

        List<DynamicForm> forms = formRepository.findAll().stream()
                .filter(f -> f.getClub() != null && f.getClub().getClubId().equals(id))
                .collect(Collectors.toList());
        model.addAttribute("forms", forms);

        return "club";
    }
}
"""
with open(os.path.join(controller_dir, "ClubController.java"), 'w') as f: f.write(club_controller_code)

# 2. Create club.html
club_html = """<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <title>Club Profile</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">

<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
        <a class="navbar-brand" href="/">DBMS Club Portal</a>
        <a class="nav-link text-white" href="/">Back to Dashboard</a>
    </div>
</nav>

<div class="container mt-5">
    <div class="card shadow-sm mb-4">
        <div class="card-body">
            <h2 class="text-primary" th:text="${club.name}">Club Name</h2>
            <p><strong>Council:</strong> <span th:text="${club.council.name}"></span></p>
            <span th:if="${club.isRecruiting}" class="badge bg-success">Currently Recruiting!</span>
        </div>
    </div>

    <div class="row">
        <!-- Events & Rooms -->
        <div class="col-md-6 mb-4">
            <div class="card shadow-sm h-100">
                <div class="card-header bg-white"><h4>Events & Rooms</h4></div>
                <div class="card-body">
                    <h5>Allocated Rooms:</h5>
                    <ul class="list-group mb-4">
                        <li class="list-group-item" th:each="roomAlloc : ${rooms}">
                            Room ID: <span th:text="${roomAlloc.room.roomId}"></span> (Year: <span th:text="${roomAlloc.academicYear}"></span>)
                        </li>
                        <li class="list-group-item text-muted" th:if="${rooms.isEmpty()}">No rooms allocated yet.</li>
                    </ul>

                    <h5>Upcoming Events:</h5>
                    <ul class="list-group">
                        <li class="list-group-item" th:each="event : ${events}">
                            <strong th:text="${event.name}"></strong> - <span th:text="${event.eventDate}"></span>
                        </li>
                        <li class="list-group-item text-muted" th:if="${events.isEmpty()}">No events scheduled.</li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- POR Holders & Forms -->
        <div class="col-md-6 mb-4">
            <div class="card shadow-sm h-100">
                <div class="card-header bg-white"><h4>Administration & Applications</h4></div>
                <div class="card-body">
                    <h5>Current POR Holders:</h5>
                    <ul class="list-group mb-4">
                        <li class="list-group-item d-flex justify-content-between" th:each="por : ${pors}">
                            <span th:text="${por.student.name} + ' (' + ${por.student.rollNumber} + ')'"></span>
                            <span class="badge bg-primary rounded-pill" th:text="${por.role.title}"></span>
                        </li>
                        <li class="list-group-item text-muted" th:if="${pors.isEmpty()}">No PORs assigned yet.</li>
                    </ul>

                    <h5>Available Forms:</h5>
                    <ul class="list-group">
                        <li class="list-group-item d-flex justify-content-between align-items-center" th:each="form : ${forms}">
                            <span th:text="${form.title}">Form Title</span>
                            <a th:href="@{/form/{id}(id=${form.formId})}" class="btn btn-sm btn-outline-success">Fill Out</a>
                        </li>
                        <li class="list-group-item text-muted" th:if="${forms.isEmpty()}">No active forms available.</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div>
</body>
</html>"""
with open(os.path.join(template_dir, "club.html"), 'w') as f: f.write(club_html)

# 3. Update dashboard.html link
dashboard_path = os.path.join(template_dir, "dashboard.html")
with open(dashboard_path, 'r') as f:
    dash_content = f.read()
# Replace the placeholder text with a real clickable link
dash_content = dash_content.replace(
    '<span th:text="${club.name}">Club Name</span>',
    '<a th:href="@{/club/{id}(id=${club.clubId})}" th:text="${club.name}" class="text-decoration-none fw-bold">Club Name</a>'
)
with open(dashboard_path, 'w') as f:
    f.write(dash_content)

print("ClubController and club.html generated successfully!")
