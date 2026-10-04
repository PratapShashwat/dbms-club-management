import os

base_dir = r"backend\src\main\java\com\college\clubmanagement\controller"
templates_dir = r"backend\src\main\resources\templates"

# 1. Fix DashboardController isGenSec logic
dashboard_path = os.path.join(base_dir, "DashboardController.java")
with open(dashboard_path, 'r') as f: content = f.read()
content = content.replace('m.getClub() == null && m.getRole() != null', 'm.getRole() != null && "GenSec".equals(m.getRole().getTitle())')
with open(dashboard_path, 'w') as f: f.write(content)

# 2. Fix AdminController
admin_path = os.path.join(base_dir, "AdminController.java")
admin_code = """package com.college.clubmanagement.controller;

import com.college.clubmanagement.entity.*;
import com.college.clubmanagement.repository.*;
import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.stream.Collectors;

@Controller
public class AdminController {
    private final CouncilRepository councilRepository;
    private final StudentRepository studentRepository;
    private final ClubMembershipRepository membershipRepository;
    private final PorRoleRepository roleRepository;
    private final ClubRepository clubRepository;

    public AdminController(CouncilRepository councilRepository, StudentRepository studentRepository, 
                           ClubMembershipRepository membershipRepository, PorRoleRepository roleRepository,
                           ClubRepository clubRepository) {
        this.councilRepository = councilRepository;
        this.studentRepository = studentRepository;
        this.membershipRepository = membershipRepository;
        this.roleRepository = roleRepository;
        this.clubRepository = clubRepository;
    }

    @GetMapping("/superadmin")
    public String viewAdminDashboard(HttpSession session, Model model) {
        Boolean isSuperAdmin = (Boolean) session.getAttribute("IS_SUPER_ADMIN");
        if (isSuperAdmin == null || !isSuperAdmin) return "redirect:/?error=Unauthorized";
        
        model.addAttribute("councils", councilRepository.findAll());
        model.addAttribute("clubs", clubRepository.findAll());
        
        List<ClubMembership> allGensecs = membershipRepository.findAll().stream()
                .filter(m -> m.getRole() != null && "GenSec".equals(m.getRole().getTitle()))
                .collect(Collectors.toList());
        model.addAttribute("gensecs", allGensecs);

        return "superadmin";
    }

    @PostMapping("/admin/assign-gensec")
    public String assignGenSec(@RequestParam String rollNumber, @RequestParam Integer councilId, @RequestParam Integer clubId) {
        // Ensure only 1 GenSec per Council
        boolean councilHasGensec = membershipRepository.findAll().stream()
                .anyMatch(m -> m.getRole() != null && "GenSec".equals(m.getRole().getTitle()) && m.getRole().getCouncil().getCouncilId().equals(councilId));
        if(councilHasGensec) return "redirect:/superadmin?error=CouncilAlreadyHasGenSec";
        
        Student student = studentRepository.findById(rollNumber).orElseThrow();
        Council council = councilRepository.findById(councilId).orElseThrow();
        Club club = clubRepository.findById(clubId).orElseThrow();
        
        PorRole role = roleRepository.findAll().stream()
                .filter(r -> "GenSec".equals(r.getTitle()) && r.getClub().getClubId().equals(clubId))
                .findFirst().orElseGet(() -> {
                    PorRole newRole = new PorRole();
                    newRole.setTitle("GenSec");
                    newRole.setCouncil(council);
                    newRole.setClub(club);
                    newRole.setPermissionsJson("[\\"MANAGE_MEMBERS\\",\\"MANAGE_PORS\\",\\"CREATE_FORMS\\",\\"VIEW_EMAIL\\",\\"VIEW_PHONE\\"]");
                    return roleRepository.save(newRole);
                });

        // Ensure user is in the club
        ClubMembership cm = membershipRepository.findAll().stream()
                .filter(m -> m.getStudent().getRollNumber().equals(rollNumber) && m.getClub().getClubId().equals(clubId))
                .findFirst().orElseGet(() -> {
                    ClubMembership newCm = new ClubMembership();
                    newCm.setStudent(student);
                    newCm.setClub(club);
                    newCm.setAcademicYear("2026-2027");
                    return newCm;
                });
        cm.setRole(role);
        membershipRepository.save(cm);
        return "redirect:/superadmin?success=GenSecAssigned";
    }
    
    @PostMapping("/admin/remove-gensec")
    public String removeGenSec(@RequestParam Integer membershipId) {
        ClubMembership cm = membershipRepository.findById(membershipId).orElseThrow();
        cm.setRole(null);
        membershipRepository.save(cm);
        return "redirect:/superadmin?success=GenSecRemoved";
    }
}"""
with open(admin_path, 'w') as f: f.write(admin_code)

# 3. Fix Superadmin HTML
superadmin_html = """<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head><title>Super Admin Console</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"></head>
<body class="bg-light">
<nav class="navbar navbar-expand-lg navbar-dark bg-danger">
    <div class="container"><a class="navbar-brand" href="#">SuperAdmin Portal</a><a class="nav-link text-white" href="/">Back to Dashboard</a></div>
</nav>
<div class="container mt-5">
    <div th:if="${param.success}" class="alert alert-success">Action completed successfully!</div>
    <div th:if="${param.error}" class="alert alert-danger" th:text="${param.error}">Error</div>
    
    <div class="row">
        <!-- Assign GenSec -->
        <div class="col-md-6 mb-4">
            <div class="card shadow-sm h-100 border-danger">
                <div class="card-header bg-white"><h4 class="text-danger">Assign General Secretary</h4></div>
                <div class="card-body">
                    <form th:action="@{/admin/assign-gensec}" method="POST">
                        <div class="mb-3">
                            <label class="form-label">Student Roll Number</label>
                            <input type="text" class="form-control" name="rollNumber" required placeholder="e.g. 101">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Select Council</label>
                            <select class="form-select" name="councilId" required>
                                <option th:each="c : ${councils}" th:value="${c.councilId}" th:text="${c.name}"></option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Assign them to a Club within Council</label>
                            <select class="form-select" name="clubId" required>
                                <option th:each="c : ${clubs}" th:value="${c.clubId}" th:text="${c.name}"></option>
                            </select>
                        </div>
                        <button type="submit" class="btn btn-danger w-100">Appoint General Secretary</button>
                    </form>
                </div>
            </div>
        </div>
        
        <!-- Current GenSecs -->
        <div class="col-md-6 mb-4">
            <div class="card shadow-sm h-100">
                <div class="card-header"><h4 class="mb-0">Current General Secretaries</h4></div>
                <div class="card-body">
                    <ul class="list-group">
                        <li class="list-group-item d-flex justify-content-between align-items-center" th:each="g : ${gensecs}">
                            <div>
                                <strong th:text="${g.student.name}">Name</strong> (<span th:text="${g.student.rollNumber}"></span>)<br>
                                <small th:text="${g.role.council.name} + ' - ' + ${g.club.name}"></small>
                            </div>
                            <form th:action="@{/admin/remove-gensec}" method="POST">
                                <input type="hidden" name="membershipId" th:value="${g.membershipId}">
                                <button type="submit" class="btn btn-sm btn-outline-danger">Demote</button>
                            </form>
                        </li>
                        <li class="list-group-item text-muted" th:if="${gensecs.isEmpty()}">No GenSecs appointed yet.</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div></body></html>"""
with open(os.path.join(templates_dir, "superadmin.html"), 'w') as f: f.write(superadmin_html)

print("Bugfixes applied!")
