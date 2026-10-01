import os

base_dir = r"backend\src\main\java\com\college\clubmanagement"
controller_dir = os.path.join(base_dir, "controller")
template_dir = r"backend\src\main\resources\templates"

admin_controller_code = """package com.college.clubmanagement.controller;

import com.college.clubmanagement.entity.*;
import com.college.clubmanagement.repository.*;
import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

import java.util.List;

@Controller
public class AdminController {

    private final ClubRepository clubRepository;
    private final PorRoleRepository roleRepository;
    private final ClubMembershipRepository membershipRepository;
    private final StudentRepository studentRepository;

    public AdminController(ClubRepository clubRepository, PorRoleRepository roleRepository,
                           ClubMembershipRepository membershipRepository, StudentRepository studentRepository) {
        this.clubRepository = clubRepository;
        this.roleRepository = roleRepository;
        this.membershipRepository = membershipRepository;
        this.studentRepository = studentRepository;
    }

    @GetMapping("/superadmin")
    public String viewSuperAdmin(HttpSession session, Model model) {
        Boolean isSuper = (Boolean) session.getAttribute("IS_SUPER_ADMIN");
        if (isSuper == null || !isSuper) {
            return "redirect:/"; // Block non-admins
        }

        model.addAttribute("clubs", clubRepository.findAll());
        model.addAttribute("roles", roleRepository.findAll());
        model.addAttribute("memberships", membershipRepository.findAll());
        
        return "superadmin";
    }

    @PostMapping("/superadmin/toggle-recruitment")
    public String toggleRecruitment(@RequestParam Integer clubId) {
        Club club = clubRepository.findById(clubId).orElseThrow();
        club.setIsRecruiting(!club.getIsRecruiting());
        clubRepository.save(club);
        return "redirect:/superadmin?success=ClubUpdated";
    }

    @PostMapping("/superadmin/assign-por")
    public String assignPor(@RequestParam String rollNumber, @RequestParam Integer roleId, @RequestParam Integer clubId) {
        Student student = studentRepository.findById(rollNumber).orElseThrow(() -> new RuntimeException("Student not found"));
        PorRole role = roleRepository.findById(roleId).orElseThrow();
        Club club = clubRepository.findById(clubId).orElseThrow();

        ClubMembership cm = new ClubMembership();
        cm.setStudent(student);
        cm.setClub(club);
        cm.setRole(role);
        cm.setAcademicYear("2026-2027");
        membershipRepository.save(cm);

        return "redirect:/superadmin?success=PorAssigned";
    }
}
"""
with open(os.path.join(controller_dir, "AdminController.java"), 'w') as f: f.write(admin_controller_code)

superadmin_html = """<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <title>Super Admin Console</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">

<nav class="navbar navbar-expand-lg navbar-dark bg-danger">
    <div class="container">
        <a class="navbar-brand" href="#">SuperAdmin Portal</a>
        <a class="nav-link text-white" href="/">Back to Dashboard</a>
    </div>
</nav>

<div class="container mt-5">
    
    <div th:if="${param.success}" class="alert alert-success">Action completed successfully!</div>

    <div class="row">
        <!-- Manage Clubs -->
        <div class="col-md-6 mb-4">
            <div class="card shadow-sm h-100 border-danger">
                <div class="card-header bg-white"><h4 class="text-danger">Manage Clubs</h4></div>
                <div class="card-body">
                    <table class="table table-sm table-hover">
                        <thead><tr><th>ID</th><th>Name</th><th>Recruiting?</th><th>Action</th></tr></thead>
                        <tbody>
                            <tr th:each="club : ${clubs}">
                                <td th:text="${club.clubId}"></td>
                                <td th:text="${club.name}"></td>
                                <td>
                                    <span th:if="${club.isRecruiting}" class="text-success">Yes</span>
                                    <span th:unless="${club.isRecruiting}" class="text-danger">No</span>
                                </td>
                                <td>
                                    <form th:action="@{/superadmin/toggle-recruitment}" method="POST">
                                        <input type="hidden" name="clubId" th:value="${club.clubId}">
                                        <button type="submit" class="btn btn-sm btn-outline-danger">Toggle</button>
                                    </form>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Assign POR -->
        <div class="col-md-6 mb-4">
            <div class="card shadow-sm h-100 border-danger">
                <div class="card-header bg-white"><h4 class="text-danger">Assign / Override POR</h4></div>
                <div class="card-body">
                    <form th:action="@{/superadmin/assign-por}" method="POST">
                        <div class="mb-3">
                            <label class="form-label">Student Roll Number</label>
                            <input type="text" class="form-control" name="rollNumber" required placeholder="e.g. 24075074">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Target Club</label>
                            <select class="form-select" name="clubId" required>
                                <option th:each="club : ${clubs}" th:value="${club.clubId}" th:text="${club.name}"></option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Assign Role (Requires Database Roles)</label>
                            <select class="form-select" name="roleId" required>
                                <option th:each="role : ${roles}" th:value="${role.roleId}" th:text="${role.title}"></option>
                                <option th:if="${roles.isEmpty()}" value="" disabled>No roles created yet!</option>
                            </select>
                        </div>
                        <button type="submit" class="btn btn-danger w-100">Force Assign POR</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
</body>
</html>"""
with open(os.path.join(template_dir, "superadmin.html"), 'w') as f: f.write(superadmin_html)

# Let's also update dashboard.html to point the SuperAdmin banner to /superadmin instead of /admin
dashboard_path = os.path.join(template_dir, "dashboard.html")
with open(dashboard_path, 'r') as f:
    dash_content = f.read()
dash_content = dash_content.replace('href="/admin" class="btn btn-sm btn-dark ms-3"', 'href="/superadmin" class="btn btn-sm btn-dark ms-3"')
with open(dashboard_path, 'w') as f:
    f.write(dash_content)

print("AdminController and superadmin.html generated successfully!")
