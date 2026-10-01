import os

controller_dir = r"backend\src\main\java\com\college\clubmanagement\controller"
template_dir = r"backend\src\main\resources\templates"

controller_code = """package com.college.clubmanagement.controller;

import com.college.clubmanagement.entity.Club;
import com.college.clubmanagement.entity.FormMembership;
import com.college.clubmanagement.entity.Student;
import com.college.clubmanagement.entity.Vertical;
import com.college.clubmanagement.repository.ClubRepository;
import com.college.clubmanagement.repository.FormMembershipRepository;
import com.college.clubmanagement.repository.StudentRepository;
import com.college.clubmanagement.repository.VerticalRepository;
import com.college.clubmanagement.service.ClubManagementService;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Controller
public class FormsController {

    private final ClubRepository clubRepository;
    private final VerticalRepository verticalRepository;
    private final StudentRepository studentRepository;
    private final FormMembershipRepository formMembershipRepository;
    private final ClubManagementService clubManagementService;

    public FormsController(ClubRepository clubRepository,
                           VerticalRepository verticalRepository,
                           StudentRepository studentRepository,
                           FormMembershipRepository formMembershipRepository,
                           ClubManagementService clubManagementService) {
        this.clubRepository = clubRepository;
        this.verticalRepository = verticalRepository;
        this.studentRepository = studentRepository;
        this.formMembershipRepository = formMembershipRepository;
        this.clubManagementService = clubManagementService;
    }

    @GetMapping("/apply/{clubId}")
    public String viewApplyForm(@PathVariable Integer clubId, Model model) {
        Club club = clubRepository.findById(clubId).orElseThrow();
        // Just find verticals for this club (assuming we had a findByClub method, for now fetch all and filter in memory for simplicity)
        List<Vertical> verticals = verticalRepository.findAll().stream().filter(v -> v.getClub().getClubId().equals(clubId)).toList();
        
        model.append("club", club);
        model.addAttribute("verticals", verticals);
        return "apply";
    }

    @PostMapping("/apply/{clubId}")
    public String submitApplication(@PathVariable Integer clubId,
                                    @RequestParam String rollNumber,
                                    @RequestParam(required = false) Integer verticalId,
                                    @RequestParam String statementOfPurpose,
                                    @RequestParam String academicYear) {
        
        // Dummy check: ensure student exists, if not, create a dummy one for testing
        Student student = studentRepository.findById(rollNumber).orElseGet(() -> {
            Student s = new Student();
            s.setRollNumber(rollNumber);
            s.setName("Test Student");
            return studentRepository.save(s);
        });

        Club club = clubRepository.findById(clubId).orElseThrow();
        Vertical vertical = verticalId != null ? verticalRepository.findById(verticalId).orElse(null) : null;

        FormMembership form = new FormMembership();
        form.setApplicant(student);
        form.setClub(club);
        form.setVertical(vertical);
        form.setStatementOfPurpose(statementOfPurpose);
        form.setAcademicYear(academicYear);
        form.setStatus("Pending");
        formMembershipRepository.save(form);

        return "redirect:/?success=true";
    }

    @GetMapping("/admin")
    public String viewAdminDashboard(Model model) {
        List<FormMembership> pendingForms = formMembershipRepository.findAll().stream()
                .filter(f -> "Pending".equals(f.getStatus()))
                .toList();
        model.addAttribute("pendingForms", pendingForms);
        return "admin";
    }

    @PostMapping("/admin/approve-membership/{formId}")
    public String approveMembership(@PathVariable Integer formId) {
        clubManagementService.approveMembershipForm(formId);
        return "redirect:/admin?approved=true";
    }

    @PostMapping("/admin/reject-membership/{formId}")
    public String rejectMembership(@PathVariable Integer formId) {
        clubManagementService.rejectMembershipForm(formId);
        return "redirect:/admin?rejected=true";
    }
}
"""

apply_html = """<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <title>Apply for Club</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">

<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container">
        <a class="navbar-brand" href="/">Club Management System</a>
        <div class="collapse navbar-collapse">
            <ul class="navbar-nav ms-auto">
                <li class="nav-item">
                    <a class="nav-link" href="/">Dashboard</a>
                </li>
            </ul>
        </div>
    </div>
</nav>

<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card shadow-sm">
                <div class="card-header bg-white">
                    <h4 class="mb-0">Application Form: <span th:text="${club.name}" class="text-primary"></span></h4>
                </div>
                <div class="card-body">
                    <form th:action="@{/apply/{id}(id=${club.clubId})}" method="POST">
                        <div class="mb-3">
                            <label for="rollNumber" class="form-label">Roll Number</label>
                            <input type="text" class="form-control" id="rollNumber" name="rollNumber" required placeholder="e.g. 24075074">
                        </div>
                        
                        <div class="mb-3">
                            <label for="verticalId" class="form-label">Select Vertical (Optional)</label>
                            <select class="form-select" id="verticalId" name="verticalId">
                                <option value="">-- No specific vertical --</option>
                                <option th:each="v : ${verticals}" th:value="${v.verticalId}" th:text="${v.name}"></option>
                            </select>
                        </div>

                        <div class="mb-3">
                            <label for="academicYear" class="form-label">Academic Year</label>
                            <input type="text" class="form-control" id="academicYear" name="academicYear" value="2026-2027" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="statementOfPurpose" class="form-label">Statement of Purpose</label>
                            <textarea class="form-control" id="statementOfPurpose" name="statementOfPurpose" rows="4" required placeholder="Why do you want to join this club?"></textarea>
                        </div>
                        
                        <button type="submit" class="btn btn-primary w-100">Submit Application</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
</body>
</html>
"""

admin_html = """<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <title>Admin Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">

<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
        <a class="navbar-brand" href="/admin">Admin Portal</a>
        <div class="collapse navbar-collapse">
            <ul class="navbar-nav ms-auto">
                <li class="nav-item">
                    <a class="nav-link" href="/">Student View</a>
                </li>
            </ul>
        </div>
    </div>
</nav>

<div class="container mt-5">
    <h2 class="mb-4">Pending Membership Applications</h2>
    
    <div th:if="${param.approved}" class="alert alert-success">Application Approved Successfully!</div>
    <div th:if="${param.rejected}" class="alert alert-danger">Application Rejected.</div>

    <div class="table-responsive">
        <table class="table table-bordered table-hover bg-white shadow-sm">
            <thead class="table-light">
                <tr>
                    <th>Form ID</th>
                    <th>Roll Number</th>
                    <th>Club</th>
                    <th>Vertical</th>
                    <th>Statement of Purpose</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <tr th:each="form : ${pendingForms}">
                    <td th:text="${form.formId}"></td>
                    <td th:text="${form.applicant.rollNumber}"></td>
                    <td th:text="${form.club.name}"></td>
                    <td th:text="${form.vertical != null ? form.vertical.name : 'N/A'}"></td>
                    <td th:text="${form.statementOfPurpose}"></td>
                    <td>
                        <form th:action="@{/admin/approve-membership/{id}(id=${form.formId})}" method="POST" class="d-inline">
                            <button type="submit" class="btn btn-sm btn-success">Approve</button>
                        </form>
                        <form th:action="@{/admin/reject-membership/{id}(id=${form.formId})}" method="POST" class="d-inline">
                            <button type="submit" class="btn btn-sm btn-danger">Reject</button>
                        </form>
                    </td>
                </tr>
                <tr th:if="${pendingForms.isEmpty()}">
                    <td colspan="6" class="text-center text-muted">No pending applications right now.</td>
                </tr>
            </tbody>
        </table>
    </div>
</div>
</body>
</html>
"""

with open(os.path.join(controller_dir, "FormsController.java"), "w") as f:
    f.write(controller_code)

with open(os.path.join(template_dir, "apply.html"), "w") as f:
    f.write(apply_html)

with open(os.path.join(template_dir, "admin.html"), "w") as f:
    f.write(admin_html)

print("Generated FormsController, apply.html, and admin.html")

