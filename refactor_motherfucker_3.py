import os

base_dir = r"backend\src\main\java\com\college\clubmanagement"
controller_dir = os.path.join(base_dir, "controller")
template_dir = r"backend\src\main\resources\templates"

club_code = """package com.college.clubmanagement.controller;
import com.college.clubmanagement.entity.*;
import com.college.clubmanagement.repository.*;
import com.college.clubmanagement.service.LoggingService;
import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.stream.Collectors;
import java.util.Optional;

@Controller
public class ClubController {
    private final ClubRepository clubRepository;
    private final VerticalRepository verticalRepository;
    private final ClubMembershipRepository membershipRepository;
    private final DynamicFormRepository formRepository;
    private final StudentRepository studentRepository;
    private final PorRoleRepository roleRepository;
    private final ClubRoomAllocationRepository roomAllocationRepository;
    private final LoggingService loggingService;

    public ClubController(ClubRepository clubRepository, VerticalRepository verticalRepository,
                          ClubMembershipRepository membershipRepository, DynamicFormRepository formRepository,
                          StudentRepository studentRepository, PorRoleRepository roleRepository,
                          ClubRoomAllocationRepository roomAllocationRepository, LoggingService loggingService) {
        this.clubRepository = clubRepository;
        this.verticalRepository = verticalRepository;
        this.membershipRepository = membershipRepository;
        this.formRepository = formRepository;
        this.studentRepository = studentRepository;
        this.roleRepository = roleRepository;
        this.roomAllocationRepository = roomAllocationRepository;
        this.loggingService = loggingService;
    }

    @GetMapping("/club/{id}")
    public String viewClub(@PathVariable Integer id, Model model, HttpSession session) {
        String rollNumber = (String) session.getAttribute("USER_ROLL");
        if (rollNumber == null) return "redirect:/login";

        Club club = clubRepository.findById(id).orElseThrow();
        model.addAttribute("club", club);
        
        Optional<ClubRoomAllocation> alloc = roomAllocationRepository.findAll().stream().filter(a -> a.getClub().getClubId().equals(id)).findFirst();
        model.addAttribute("allocatedRoom", alloc.orElse(null));

        model.addAttribute("verticals", verticalRepository.findAll().stream().filter(v -> v.getClub().getClubId().equals(id)).collect(Collectors.toList()));
        model.addAttribute("forms", formRepository.findAll().stream().filter(f -> f.getClub().getClubId().equals(id)).collect(Collectors.toList()));
        model.addAttribute("clubRoles", roleRepository.findAll().stream().filter(r -> r.getClub().getClubId().equals(id) && !"GenSec".equalsIgnoreCase(r.getTitle())).collect(Collectors.toList()));

        List<ClubMembership> allMembers = membershipRepository.findAll().stream().filter(m -> m.getClub() != null && m.getClub().getClubId().equals(id)).collect(Collectors.toList());
        
        boolean isCouncilGenSec = membershipRepository.findAll().stream().anyMatch(m -> m.getStudent().getRollNumber().equals(rollNumber) && m.getRole() != null && "GenSec".equals(m.getRole().getTitle()) && m.getRole().getCouncil().getCouncilId().equals(club.getCouncil().getCouncilId()));
        Boolean isSuperAdmin = (Boolean) session.getAttribute("IS_SUPER_ADMIN");
        boolean isSuper = (isSuperAdmin != null && isSuperAdmin);

        ClubMembership myMembership = allMembers.stream().filter(m -> m.getStudent().getRollNumber().equals(rollNumber)).findFirst().orElse(null);
        
        boolean isMember = myMembership != null || isCouncilGenSec || isSuper;
        model.addAttribute("isMember", isMember);

        if (isMember) {
            model.addAttribute("allMembers", allMembers);
            boolean canCreateForms = false, canEditMembers = false, canEditPors = false;
            if (isCouncilGenSec || isSuper) {
                canCreateForms = true; canEditMembers = true; canEditPors = true;
            } else if (myMembership != null && myMembership.getRole() != null && myMembership.getRole().getPermissionsJson() != null) {
                String p = myMembership.getRole().getPermissionsJson();
                canCreateForms = p.contains("CREATE_FORMS"); canEditMembers = p.contains("MANAGE_MEMBERS"); canEditPors = p.contains("MANAGE_PORS");
            }
            model.addAttribute("canCreateForms", canCreateForms); model.addAttribute("canEditMembers", canEditMembers); model.addAttribute("canEditPors", canEditPors);
            model.addAttribute("myCreatedForms", formRepository.findAll().stream().filter(f -> f.getClub().getClubId().equals(id) && f.getCreatedBy() != null && f.getCreatedBy().getRollNumber().equals(rollNumber)).collect(Collectors.toList()));
        }
        return "club";
    }

    @PostMapping("/club/{id}/add-member")
    public String addMember(@PathVariable Integer id, @RequestParam String rollNumber, HttpSession session) {
        boolean existsMember = membershipRepository.findAll().stream().anyMatch(m -> m.getClub() != null && m.getClub().getClubId().equals(id) && m.getStudent().getRollNumber().equals(rollNumber) && m.getRole() == null);
        if (existsMember) return "redirect:/club/" + id + "?error=Already+a+member!";
        
        ClubMembership cm = new ClubMembership();
        cm.setStudent(studentRepository.findById(rollNumber).orElseThrow());
        cm.setClub(clubRepository.findById(id).orElseThrow());
        cm.setAcademicYear("2026-2027");
        membershipRepository.save(cm);
        loggingService.log(session.getAttribute("USER_ROLL").toString(), "Add Member", rollNumber + " added to Club " + id);
        return "redirect:/club/" + id + "?success=Added";
    }

    @PostMapping("/club/{id}/assign-por")
    public String assignPor(@PathVariable Integer id, @RequestParam String rollNumber, @RequestParam Integer roleId, HttpSession session) {
        PorRole role = roleRepository.findById(roleId).orElseThrow();
        if("GenSec".equalsIgnoreCase(role.getTitle())) return "redirect:/club/" + id + "?error=Cannot+modify+GenSecs+from+Club+View!";
        
        boolean hasAnyMembership = membershipRepository.findAll().stream().anyMatch(m -> m.getClub() != null && m.getClub().getClubId().equals(id) && m.getStudent().getRollNumber().equals(rollNumber));
        if(!hasAnyMembership) return "redirect:/club/" + id + "?error=Student+must+be+a+member+first!";
        
        ClubMembership emptyMem = membershipRepository.findAll().stream().filter(m -> m.getClub() != null && m.getClub().getClubId().equals(id) && m.getStudent().getRollNumber().equals(rollNumber) && m.getRole() == null).findFirst().orElse(null);
        if(emptyMem != null) {
            emptyMem.setRole(role); membershipRepository.save(emptyMem);
        } else {
            ClubMembership newCm = new ClubMembership();
            newCm.setStudent(studentRepository.findById(rollNumber).orElseThrow());
            newCm.setClub(clubRepository.findById(id).orElseThrow());
            newCm.setRole(role); newCm.setAcademicYear("2026-2027");
            membershipRepository.save(newCm);
        }
        loggingService.log(session.getAttribute("USER_ROLL").toString(), "Assign POR", rollNumber + " given " + role.getTitle());
        return "redirect:/club/" + id + "?success=PorAssigned";
    }
    
    @PostMapping("/club/{id}/remove-por")
    public String removePor(@PathVariable Integer id, @RequestParam String rollNumber, @RequestParam Integer membershipId, HttpSession session) {
        ClubMembership cm = membershipRepository.findById(membershipId).orElseThrow();
        if(cm.getRole() != null && "GenSec".equalsIgnoreCase(cm.getRole().getTitle())) return "redirect:/club/" + id + "?error=Cannot+demote+GenSecs!";
        cm.setRole(null);
        membershipRepository.save(cm);
        loggingService.log(session.getAttribute("USER_ROLL").toString(), "Demote POR", rollNumber + " demoted in club " + id);
        return "redirect:/club/" + id + "?success=PorDemoted";
    }
}"""
with open(os.path.join(controller_dir, "ClubController.java"), 'w') as f: f.write(club_code)

auth_code = """package com.college.clubmanagement.controller;
import com.college.clubmanagement.entity.ClubMembership;
import com.college.clubmanagement.entity.Student;
import com.college.clubmanagement.repository.ClubMembershipRepository;
import com.college.clubmanagement.repository.StudentRepository;
import com.college.clubmanagement.service.LoggingService;
import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.stream.Collectors;

@Controller
public class AuthController {
    private final StudentRepository studentRepository;
    private final ClubMembershipRepository membershipRepository;
    private final LoggingService loggingService;
    
    public AuthController(StudentRepository studentRepository, ClubMembershipRepository membershipRepository, LoggingService loggingService) {
        this.studentRepository = studentRepository;
        this.membershipRepository = membershipRepository;
        this.loggingService = loggingService;
    }

    @GetMapping("/login") public String loginPage() { return "login"; }
    @GetMapping("/register") public String registerPage() { return "register"; }
    @GetMapping("/logout") public String logout(HttpSession session) { session.invalidate(); return "redirect:/login"; }

    @PostMapping("/login")
    public String loginSubmit(@RequestParam String rollNumber, @RequestParam String password, HttpSession session) {
        if ("superadmin".equals(rollNumber) && "superadmin".equals(password)) {
            session.setAttribute("USER_ROLL", "0"); session.setAttribute("USER_NAME", "Super Admin"); session.setAttribute("IS_SUPER_ADMIN", true);
            return "redirect:/";
        }
        Student student = studentRepository.findById(rollNumber).orElse(null);
        if (student != null && student.getPassword() != null && student.getPassword().equals(password)) {
            session.setAttribute("USER_ROLL", student.getRollNumber()); session.setAttribute("USER_NAME", student.getName());
            return "redirect:/";
        }
        return "redirect:/login?error=InvalidCredentials";
    }

    @GetMapping("/profile")
    public String viewProfile(HttpSession session, Model model) {
        String rollNumber = (String) session.getAttribute("USER_ROLL");
        if (rollNumber == null) return "redirect:/login";
        model.addAttribute("student", studentRepository.findById(rollNumber).orElseThrow());
        model.addAttribute("memberships", membershipRepository.findAll().stream().filter(m -> m.getStudent().getRollNumber().equals(rollNumber)).collect(Collectors.toList()));
        return "profile";
    }

    @PostMapping("/user/resign")
    public String resign(@RequestParam Integer membershipId, HttpSession session) {
        String rollNumber = (String) session.getAttribute("USER_ROLL");
        ClubMembership cm = membershipRepository.findById(membershipId).orElseThrow();
        if(!cm.getStudent().getRollNumber().equals(rollNumber)) return "redirect:/profile?error=Unauthorized";
        if(cm.getRole() != null) {
            cm.setRole(null); membershipRepository.save(cm);
            loggingService.log(rollNumber, "Resign POR", "Resigned from POR");
            return "redirect:/profile?success=Resigned+from+POR";
        } else {
            membershipRepository.delete(cm);
            loggingService.log(rollNumber, "Leave Club", "Left Club " + cm.getClub().getName());
            return "redirect:/profile?success=Left+Club";
        }
    }
}"""
with open(os.path.join(controller_dir, "AuthController.java"), 'w') as f: f.write(auth_code)

club_html = """<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head><title>Club View</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"></head>
<body class="bg-light">
<nav class="navbar navbar-dark bg-dark"><div class="container"><a class="navbar-brand" th:text="${club.name}">Club</a><a class="nav-link text-white" href="/">Dashboard</a><a class="nav-link text-white" href="/profile">My Profile</a></div></nav>
<div class="container mt-4">
    <div th:if="${param.error}" class="alert alert-danger fw-bold shadow-sm" th:text="${param.error}"></div>
    <div th:if="${param.success}" class="alert alert-success fw-bold shadow-sm" th:text="${param.success}"></div>

    <div class="row">
        <div class="col-md-12 mb-4">
            <div class="card shadow-sm">
                <div class="card-body">
                    <h3 class="text-primary" th:text="${club.name}"></h3>
                    <h5>Allocated Room: <span class="badge bg-secondary" th:text="${allocatedRoom != null ? allocatedRoom.room.buildingName + ' ' + allocatedRoom.room.roomNumber : 'Not Assigned'}"></span></h5>
                    
                    <h5 class="mt-3">Available Verticals</h5>
                    <ul><li th:each="v : ${verticals}" th:text="${v.name}"></li></ul>

                    <h5>Available Forms</h5>
                    <ul class="list-group">
                        <li class="list-group-item d-flex justify-content-between align-items-center" th:each="form : ${forms}">
                            <span th:text="${form.title}"></span><a th:href="@{/form/{id}(id=${form.formId})}" class="btn btn-sm btn-primary">Fill Out</a>
                        </li>
                    </ul>
                </div>
            </div>
        </div>

        <div class="col-md-12" th:if="${isMember}">
            <div class="card shadow-sm border-info mb-4">
                <div class="card-header bg-info text-white"><h5>Member Portal: Club Directory</h5></div>
                <div class="card-body">
                    <table class="table table-sm">
                        <thead><tr><th>Name</th><th>Roll No</th><th>Vertical</th><th>POR</th><th th:if="${canEditPors}">Demote</th></tr></thead>
                        <tbody>
                            <tr th:each="m : ${allMembers}">
                                <td th:text="${m.student.name}"></td><td th:text="${m.student.rollNumber}"></td><td th:text="${m.vertical != null ? m.vertical.name : 'None'}"></td>
                                <td>
                                    <span class="badge bg-secondary" th:if="${m.role != null}" th:text="${m.role.title}"></span>
                                    <span class="badge bg-light text-dark" th:if="${m.role == null}">Member</span>
                                </td>
                                <td th:if="${canEditPors}">
                                    <form th:if="${m.role != null and m.role.title != 'GenSec'}" th:action="@{/club/{id}/remove-por(id=${club.clubId})}" method="POST">
                                        <input type="hidden" name="rollNumber" th:value="${m.student.rollNumber}">
                                        <input type="hidden" name="membershipId" th:value="${m.membershipId}">
                                        <button class="btn btn-sm btn-danger">Demote</button>
                                    </form>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="row">
                <div class="col-md-4" th:if="${canCreateForms}">
                    <div class="card shadow-sm border-warning h-100">
                        <div class="card-body">
                            <h5 class="text-warning">Float Forms</h5>
                            <a th:each="f : ${myCreatedForms}" th:href="@{/form/{id}/submissions(id=${f.formId})}" class="d-block mb-2" th:text="'View: ' + ${f.title}"></a>
                            <form th:action="@{/club/{id}/create-form(id=${club.clubId})}" method="POST">
                                <input type="text" class="form-control form-control-sm mb-2" name="title" placeholder="Title" required>
                                <input type="text" class="form-control form-control-sm mb-2" name="formType" placeholder="Type" required>
                                <select class="form-select form-select-sm mb-2" name="targetAudience" required><option value="ALL">All Students</option><option value="THIS_CLUB">Club Members</option></select>
                                <textarea class="form-control form-control-sm mb-2" name="questionsJson" placeholder='["Question 1?"]' required></textarea>
                                <button type="submit" class="btn btn-sm btn-warning w-100">Publish Form</button>
                            </form>
                        </div>
                    </div>
                </div>

                <div class="col-md-4" th:if="${canEditMembers}">
                    <div class="card shadow-sm border-primary h-100">
                        <div class="card-body">
                            <h5 class="text-primary">Edit Memberships</h5>
                            <form th:action="@{/club/{id}/add-member(id=${club.clubId})}" method="POST" class="d-flex gap-2 mb-2"><input type="text" class="form-control form-control-sm" name="rollNumber" placeholder="Roll No" required><button class="btn btn-sm btn-primary">Add</button></form>
                        </div>
                    </div>
                </div>

                <div class="col-md-4" th:if="${canEditPors}">
                    <div class="card shadow-sm border-primary h-100">
                        <div class="card-body">
                            <h5 class="text-primary">Assign POR</h5>
                            <form th:action="@{/club/{id}/assign-por(id=${club.clubId})}" method="POST" class="d-flex flex-column gap-2 mb-2">
                                <input type="text" class="form-control form-control-sm" name="rollNumber" placeholder="Roll No" required>
                                <select class="form-select form-select-sm" name="roleId" required><option th:each="r : ${clubRoles}" th:value="${r.roleId}" th:text="${r.title}"></option></select>
                                <button class="btn btn-sm btn-primary">Assign POR</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div></body></html>"""
with open(os.path.join(template_dir, "club.html"), 'w') as f: f.write(club_html)

profile_html = """<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head><title>My Profile</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"></head>
<body class="bg-light">
<nav class="navbar navbar-dark bg-dark"><div class="container"><a class="navbar-brand">My Profile</a><a class="nav-link text-white" href="/">Dashboard</a></div></nav>
<div class="container mt-4">
    <div th:if="${param.error}" class="alert alert-danger fw-bold shadow-sm" th:text="${param.error}"></div>
    <div th:if="${param.success}" class="alert alert-success fw-bold shadow-sm" th:text="${param.success}"></div>
    <div class="card shadow-sm mb-4">
        <div class="card-body">
            <h3><span th:text="${student.name}"></span> (<span th:text="${student.rollNumber}"></span>)</h3>
            <p><strong>Branch:</strong> <span th:text="${student.branch}"></span> | <strong>Year:</strong> <span th:text="${student.graduationYear}"></span></p>
        </div>
    </div>
    
    <div class="card shadow-sm border-danger">
        <div class="card-header bg-danger text-white"><h5>My Memberships & Resignations</h5></div>
        <div class="card-body">
            <ul class="list-group">
                <li class="list-group-item d-flex justify-content-between align-items-center" th:each="m : ${memberships}">
                    <div><strong th:text="${m.club.name}"></strong> <span class="badge bg-primary" th:if="${m.role != null}" th:text="${m.role.title}"></span><span class="badge bg-secondary" th:if="${m.role == null}">Member</span></div>
                    <form th:action="@{/user/resign}" method="POST" th:if="${m.role == null or m.role.title != 'GenSec'}">
                        <input type="hidden" name="membershipId" th:value="${m.membershipId}">
                        <button type="submit" class="btn btn-sm btn-outline-danger" th:text="${m.role != null ? 'Resign POR' : 'Leave Club'}"></button>
                    </form>
                    <span class="text-danger small" th:if="${m.role != null and m.role.title == 'GenSec'}">SuperAdmin must demote GenSecs.</span>
                </li>
            </ul>
        </div>
    </div>
</div></body></html>"""
with open(os.path.join(template_dir, "profile.html"), 'w') as f: f.write(profile_html)

print("Phase 3/3 written.")
