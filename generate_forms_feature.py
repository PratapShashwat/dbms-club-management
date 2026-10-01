import os

base_dir = r"backend\src\main\java\com\college\clubmanagement"
controller_dir = os.path.join(base_dir, "controller")
template_dir = r"backend\src\main\resources\templates"

# 1. Update FormsController.java to handle dynamic forms correctly
forms_controller_code = """package com.college.clubmanagement.controller;

import com.college.clubmanagement.entity.*;
import com.college.clubmanagement.repository.*;
import com.college.clubmanagement.service.ClubManagementService;
import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.stream.Collectors;

@Controller
public class FormsController {

    private final DynamicFormRepository dynamicFormRepository;
    private final FormSubmissionRepository formSubmissionRepository;
    private final StudentRepository studentRepository;
    private final ClubRepository clubRepository;
    private final ClubManagementService clubManagementService;

    public FormsController(DynamicFormRepository dynamicFormRepository,
                           FormSubmissionRepository formSubmissionRepository,
                           StudentRepository studentRepository,
                           ClubRepository clubRepository,
                           ClubManagementService clubManagementService) {
        this.dynamicFormRepository = dynamicFormRepository;
        this.formSubmissionRepository = formSubmissionRepository;
        this.studentRepository = studentRepository;
        this.clubRepository = clubRepository;
        this.clubManagementService = clubManagementService;
    }

    @GetMapping("/form/{id}")
    public String viewForm(@PathVariable Integer id, Model model, HttpSession session) {
        String rollNumber = (String) session.getAttribute("USER_ROLL");
        if (rollNumber == null) return "redirect:/login";

        DynamicForm form = dynamicFormRepository.findById(id).orElseThrow();
        model.addAttribute("form", form);
        
        // Basic check if already submitted
        boolean alreadySubmitted = formSubmissionRepository.findAll().stream()
                .anyMatch(s -> s.getDynamicForm().getFormId().equals(id) && s.getStudent().getRollNumber().equals(rollNumber));
        model.addAttribute("alreadySubmitted", alreadySubmitted);

        return "dynamic-form";
    }

    @PostMapping("/form/{id}/submit")
    public String submitForm(@PathVariable Integer id, @RequestParam String answersJson, HttpSession session) {
        String rollNumber = (String) session.getAttribute("USER_ROLL");
        if (rollNumber == null) return "redirect:/login";

        Student student = studentRepository.findById(rollNumber).orElseThrow();
        DynamicForm form = dynamicFormRepository.findById(id).orElseThrow();

        FormSubmission submission = new FormSubmission();
        submission.setDynamicForm(form);
        submission.setStudent(student);
        submission.setAnswersJson(answersJson);
        submission.setStatus("Pending");
        formSubmissionRepository.save(submission);

        return "redirect:/club/" + form.getClub().getClubId() + "?success=FormSubmitted";
    }

    @PostMapping("/club/{clubId}/create-form")
    public String createForm(@PathVariable Integer clubId, @RequestParam String title, @RequestParam String formType, @RequestParam String targetAudience, @RequestParam String questionsJson) {
        Club club = clubRepository.findById(clubId).orElseThrow();
        DynamicForm form = new DynamicForm();
        form.setClub(club);
        form.setTitle(title);
        form.setFormType(formType);
        form.setTargetAudience(targetAudience);
        form.setQuestionsJson(questionsJson);
        dynamicFormRepository.save(form);
        return "redirect:/club/" + clubId + "?success=FormCreated";
    }

    // Secretary View Submissions
    @GetMapping("/club/{clubId}/submissions")
    public String viewSubmissions(@PathVariable Integer clubId, Model model, HttpSession session) {
        if (session.getAttribute("USER_ROLL") == null) return "redirect:/login";

        Club club = clubRepository.findById(clubId).orElseThrow();
        model.addAttribute("club", club);

        List<FormSubmission> pendingSubmissions = formSubmissionRepository.findAll().stream()
                .filter(s -> s.getDynamicForm().getClub().getClubId().equals(clubId) && "Pending".equals(s.getStatus()))
                .collect(Collectors.toList());
        model.addAttribute("pendingForms", pendingSubmissions);

        return "submissions";
    }

    @PostMapping("/admin/approve/{id}")
    public String approve(@PathVariable Integer id) {
        FormSubmission sub = formSubmissionRepository.findById(id).orElseThrow();
        Integer clubId = sub.getDynamicForm().getClub().getClubId();
        clubManagementService.approveSubmission(id);
        return "redirect:/club/" + clubId + "/submissions?success=Approved";
    }
    
    @PostMapping("/admin/reject/{id}")
    public String reject(@PathVariable Integer id) {
        FormSubmission sub = formSubmissionRepository.findById(id).orElseThrow();
        Integer clubId = sub.getDynamicForm().getClub().getClubId();
        clubManagementService.rejectSubmission(id);
        return "redirect:/club/" + clubId + "/submissions?success=Rejected";
    }
}
"""
with open(os.path.join(controller_dir, "FormsController.java"), 'w') as f: f.write(forms_controller_code)


# 2. HTML View for dynamic form
dynamic_form_html = """<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <title th:text="${form.title}">Form</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">

<div class="container mt-5">
    <div class="card shadow-sm mx-auto" style="max-width: 600px;">
        <div class="card-header bg-primary text-white">
            <h3 th:text="${form.title}">Form Title</h3>
            <p class="mb-0" th:text="'Target: ' + ${form.targetAudience} + ' | Type: ' + ${form.formType}"></p>
        </div>
        <div class="card-body">
            
            <div th:if="${alreadySubmitted}" class="alert alert-success">
                You have already submitted this form!
                <a th:href="@{/club/{id}(id=${form.club.clubId})}" class="btn btn-sm btn-success ms-2">Back to Club</a>
            </div>

            <form th:unless="${alreadySubmitted}" th:action="@{/form/{id}/submit(id=${form.formId})}" method="POST">
                
                <div class="alert alert-info">
                    <strong>Questions:</strong> <br>
                    <code th:text="${form.questionsJson}"></code>
                </div>

                <div class="mb-3">
                    <label class="form-label">Write your answers below (as JSON or structured text)</label>
                    <textarea class="form-control" name="answersJson" rows="5" required placeholder='e.g. {"Why join?": "I love coding", "Experience": "None"}'></textarea>
                </div>

                <button type="submit" class="btn btn-primary w-100">Submit Application</button>
            </form>
        </div>
    </div>
</div>
</body>
</html>"""
with open(os.path.join(template_dir, "dynamic-form.html"), 'w') as f: f.write(dynamic_form_html)


# 3. HTML View for Secretary to see Submissions
submissions_html = """<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <title>Manage Submissions</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">

<div class="container mt-5">
    <a th:href="@{/club/{id}(id=${club.clubId})}" class="btn btn-secondary mb-3">&larr; Back to Club</a>
    
    <h3 class="mb-4">Pending Form Submissions</h3>
    
    <div class="alert alert-info" th:if="${pendingForms.isEmpty()}">No pending submissions right now!</div>

    <div class="card shadow-sm mb-3" th:each="sub : ${pendingForms}">
        <div class="card-body d-flex justify-content-between align-items-center">
            <div>
                <h5 class="card-title text-primary" th:text="${sub.student.name} + ' - ' + ${sub.dynamicForm.title}"></h5>
                <p class="mb-0 text-muted">Answers: <span th:text="${sub.answersJson}"></span></p>
            </div>
            <div>
                <form th:action="@{/admin/approve/{id}(id=${sub.submissionId})}" method="POST" class="d-inline">
                    <button type="submit" class="btn btn-success">Approve</button>
                </form>
                <form th:action="@{/admin/reject/{id}(id=${sub.submissionId})}" method="POST" class="d-inline">
                    <button type="submit" class="btn btn-danger">Reject</button>
                </form>
            </div>
        </div>
    </div>
</div>
</body>
</html>"""
with open(os.path.join(template_dir, "submissions.html"), 'w') as f: f.write(submissions_html)


# 4. Update club.html to include Create Form and View Submissions buttons
club_path = os.path.join(template_dir, "club.html")
with open(club_path, 'r') as f:
    club_html_content = f.read()

# Insert the Secretary controls panel
secretary_panel = """
    <!-- Secretary Controls -->
    <div class="card shadow-sm mb-4 border-warning">
        <div class="card-header bg-white"><h4 class="text-warning">Secretary Controls</h4></div>
        <div class="card-body">
            <a th:href="@{/club/{id}/submissions(id=${club.clubId})}" class="btn btn-outline-warning mb-3">View Pending Submissions</a>
            <hr>
            <h5>Create New Form</h5>
            <form th:action="@{/club/{id}/create-form(id=${club.clubId})}" method="POST">
                <div class="row">
                    <div class="col-md-3 mb-2"><input type="text" class="form-control" name="title" placeholder="Form Title" required></div>
                    <div class="col-md-3 mb-2"><input type="text" class="form-control" name="formType" placeholder="Type (e.g. MEMBERSHIP)" required></div>
                    <div class="col-md-3 mb-2"><input type="text" class="form-control" name="targetAudience" placeholder="Audience (e.g. ALL)" required></div>
                    <div class="col-md-3 mb-2"><input type="text" class="form-control" name="questionsJson" placeholder='["Q1", "Q2"]' required></div>
                </div>
                <button type="submit" class="btn btn-warning w-100">Publish Form</button>
            </form>
        </div>
    </div>
"""

# Insert right after the header card
club_html_content = club_html_content.replace('<div class="row">', secretary_panel + '\n    <div class="row">')

with open(club_path, 'w') as f: f.write(club_html_content)

print("Forms functionality fully implemented!")
