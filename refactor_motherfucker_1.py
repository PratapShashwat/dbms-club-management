import os

base_dir = r"backend\src\main\java\com\college\clubmanagement"
controller_dir = os.path.join(base_dir, "controller")
entity_dir = os.path.join(base_dir, "entity")
repo_dir = os.path.join(base_dir, "repository")
service_dir = os.path.join(base_dir, "service")
template_dir = r"backend\src\main\resources\templates"

# 1. SystemLog Entity & Repo & Service
with open(os.path.join(entity_dir, "SystemLog.java"), 'w') as f:
    f.write("""package com.college.clubmanagement.entity;
import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;
@Data
@Entity
@Table(name = "System_Log")
public class SystemLog {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer logId;
    private LocalDateTime timestamp;
    private String actor;
    private String action;
    @Column(length = 1000)
    private String details;
}""")

with open(os.path.join(repo_dir, "SystemLogRepository.java"), 'w') as f:
    f.write("""package com.college.clubmanagement.repository;
import com.college.clubmanagement.entity.SystemLog;
import org.springframework.data.jpa.repository.JpaRepository;
public interface SystemLogRepository extends JpaRepository<SystemLog, Integer> {}""")

with open(os.path.join(service_dir, "LoggingService.java"), 'w') as f:
    f.write("""package com.college.clubmanagement.service;
import com.college.clubmanagement.entity.SystemLog;
import com.college.clubmanagement.repository.SystemLogRepository;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
@Service
public class LoggingService {
    private final SystemLogRepository repo;
    public LoggingService(SystemLogRepository repo) { this.repo = repo; }
    public void log(String actor, String action, String details) {
        SystemLog log = new SystemLog();
        log.setTimestamp(LocalDateTime.now());
        log.setActor(actor);
        log.setAction(action);
        log.setDetails(details);
        repo.save(log);
    }
}""")

# 2. Update AdminController (Remove Club dropdown, check membership, add logs)
admin_code = """package com.college.clubmanagement.controller;
import com.college.clubmanagement.entity.*;
import com.college.clubmanagement.repository.*;
import com.college.clubmanagement.service.LoggingService;
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
    private final LoggingService loggingService;
    private final SystemLogRepository logRepository;

    public AdminController(CouncilRepository councilRepository, StudentRepository studentRepository, 
                           ClubMembershipRepository membershipRepository, PorRoleRepository roleRepository,
                           ClubRepository clubRepository, LoggingService loggingService, SystemLogRepository logRepository) {
        this.councilRepository = councilRepository;
        this.studentRepository = studentRepository;
        this.membershipRepository = membershipRepository;
        this.roleRepository = roleRepository;
        this.clubRepository = clubRepository;
        this.loggingService = loggingService;
        this.logRepository = logRepository;
    }

    @GetMapping("/superadmin")
    public String viewAdminDashboard(HttpSession session, Model model) {
        Boolean isSuperAdmin = (Boolean) session.getAttribute("IS_SUPER_ADMIN");
        if (isSuperAdmin == null || !isSuperAdmin) return "redirect:/?error=Unauthorized";
        
        model.addAttribute("councils", councilRepository.findAll());
        model.addAttribute("gensecs", membershipRepository.findAll().stream()
                .filter(m -> m.getRole() != null && "GenSec".equals(m.getRole().getTitle())).collect(Collectors.toList()));
        model.addAttribute("logs", logRepository.findAll().stream().sorted((a,b)->b.getTimestamp().compareTo(a.getTimestamp())).limit(50).collect(Collectors.toList()));
        return "superadmin";
    }

    @PostMapping("/admin/assign-gensec")
    public String assignGenSec(@RequestParam String rollNumber, @RequestParam Integer councilId) {
        List<ClubMembership> validMemberships = membershipRepository.findAll().stream()
                .filter(m -> m.getStudent().getRollNumber().equals(rollNumber) && m.getClub().getCouncil().getCouncilId().equals(councilId))
                .collect(Collectors.toList());
                
        if(validMemberships.isEmpty()) return "redirect:/superadmin?error=Student+must+belong+to+a+club+within+this+council+first!";
        
        boolean councilHasGensec = membershipRepository.findAll().stream()
                .anyMatch(m -> m.getRole() != null && "GenSec".equals(m.getRole().getTitle()) && m.getRole().getCouncil().getCouncilId().equals(councilId));
        if(councilHasGensec) return "redirect:/superadmin?error=Council+already+has+a+GenSec!";
        
        Council council = councilRepository.findById(councilId).orElseThrow();
        ClubMembership cm = validMemberships.get(0);
        Club club = cm.getClub();
        
        PorRole role = roleRepository.findAll().stream()
                .filter(r -> "GenSec".equals(r.getTitle()) && r.getClub().getClubId().equals(club.getClubId()))
                .findFirst().orElseGet(() -> {
                    PorRole newRole = new PorRole();
                    newRole.setTitle("GenSec");
                    newRole.setCouncil(council);
                    newRole.setClub(club);
                    newRole.setPermissionsJson("[\\"MANAGE_MEMBERS\\",\\"MANAGE_PORS\\",\\"CREATE_FORMS\\",\\"VIEW_EMAIL\\",\\"VIEW_PHONE\\"]");
                    return roleRepository.save(newRole);
                });
        cm.setRole(role);
        membershipRepository.save(cm);
        loggingService.log("SuperAdmin", "Assign GenSec", rollNumber + " appointed GenSec for Council " + council.getName());
        return "redirect:/superadmin?success=GenSecAssigned";
    }
    
    @PostMapping("/admin/remove-gensec")
    public String removeGenSec(@RequestParam Integer membershipId) {
        ClubMembership cm = membershipRepository.findById(membershipId).orElseThrow();
        String name = cm.getStudent().getName();
        cm.setRole(null);
        membershipRepository.save(cm);
        loggingService.log("SuperAdmin", "Remove GenSec", name + " demoted from GenSec");
        return "redirect:/superadmin?success=GenSecRemoved";
    }
}"""
with open(os.path.join(controller_dir, "AdminController.java"), 'w') as f: f.write(admin_code)

# 3. SuperAdmin HTML (Remove club dropdown, show logs)
superadmin_html = """<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head><title>Super Admin Console</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"></head>
<body class="bg-light">
<nav class="navbar navbar-expand-lg navbar-dark bg-danger">
    <div class="container"><a class="navbar-brand" href="#">SuperAdmin Portal</a><a class="nav-link text-white" href="/">Back to Dashboard</a></div>
</nav>
<div class="container mt-5">
    <!-- ERROR TOAST/BOX -->
    <div th:if="${param.error}" class="alert alert-danger fw-bold shadow-sm" th:text="${param.error}"></div>
    <div th:if="${param.success}" class="alert alert-success fw-bold shadow-sm" th:text="${param.success}"></div>
    
    <div class="row">
        <div class="col-md-6 mb-4">
            <div class="card shadow-sm border-danger h-100">
                <div class="card-header bg-white"><h4 class="text-danger">Assign General Secretary</h4></div>
                <div class="card-body">
                    <p class="text-muted small">Student MUST already belong to a club in the Council.</p>
                    <form th:action="@{/admin/assign-gensec}" method="POST">
                        <div class="mb-3"><input type="text" class="form-control" name="rollNumber" required placeholder="Student Roll No"></div>
                        <div class="mb-3">
                            <select class="form-select" name="councilId" required>
                                <option th:each="c : ${councils}" th:value="${c.councilId}" th:text="${c.name}"></option>
                            </select>
                        </div>
                        <button type="submit" class="btn btn-danger w-100">Appoint General Secretary</button>
                    </form>
                </div>
            </div>
        </div>
        <div class="col-md-6 mb-4">
            <div class="card shadow-sm h-100">
                <div class="card-header"><h4 class="mb-0">Current General Secretaries</h4></div>
                <div class="card-body">
                    <ul class="list-group">
                        <li class="list-group-item d-flex justify-content-between align-items-center" th:each="g : ${gensecs}">
                            <div><strong th:text="${g.student.name}"></strong> (<span th:text="${g.student.rollNumber}"></span>)<br><small th:text="${g.role.council.name} + ' - ' + ${g.club.name}"></small></div>
                            <form th:action="@{/admin/remove-gensec}" method="POST"><input type="hidden" name="membershipId" th:value="${g.membershipId}"><button type="submit" class="btn btn-sm btn-outline-danger">Demote</button></form>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
        <div class="col-md-12">
            <div class="card shadow-sm">
                <div class="card-header bg-dark text-white"><h5>System Operation Logs</h5></div>
                <div class="card-body" style="max-height: 400px; overflow-y: auto;">
                    <table class="table table-sm table-hover">
                        <thead><tr><th>Time</th><th>Actor</th><th>Action</th><th>Details</th></tr></thead>
                        <tbody><tr th:each="l : ${logs}"><td th:text="${l.timestamp}"></td><td th:text="${l.actor}"></td><td th:text="${l.action}"></td><td th:text="${l.details}"></td></tr></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div></body></html>"""
with open(os.path.join(template_dir, "superadmin.html"), 'w') as f: f.write(superadmin_html)

print("Phase 1/3 written.")
