import os

base_dir = r"backend\src\main\java\com\college\clubmanagement"
controller_dir = os.path.join(base_dir, "controller")
entity_dir = os.path.join(base_dir, "entity")
template_dir = r"backend\src\main\resources\templates"

# 1. Update Student.java with Password
student_java = """package com.college.clubmanagement.entity;
import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
@Table(name = "Student")
public class Student {
    @Id
    @Column(name = "Roll_Number", length = 20)
    private String rollNumber;

    @Column(name = "Name", nullable = false, length = 100)
    private String name;

    @Column(name = "Graduation_Year")
    private Integer graduationYear;

    @Column(name = "Branch", length = 50)
    private String branch;

    @Column(name = "Course", length = 50)
    private String course;

    @Column(name = "Email", nullable = false, unique = true, length = 100)
    private String email;
    
    @Column(name = "Phone_Number", length = 15)
    private String phoneNumber;
    
    @Column(name = "Password", length = 100)
    private String password;
}"""
with open(os.path.join(entity_dir, "Student.java"), 'w') as f: f.write(student_java)


# 2. Update AuthController.java (Password validation)
auth_code = """package com.college.clubmanagement.controller;

import com.college.clubmanagement.entity.Student;
import com.college.clubmanagement.repository.StudentRepository;
import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import java.util.Arrays;
import java.util.List;

@Controller
public class AuthController {
    
    private final StudentRepository studentRepository;
    
    public AuthController(StudentRepository studentRepository) {
        this.studentRepository = studentRepository;
    }

    @GetMapping("/login")
    public String viewLogin() {
        return "login";
    }

    @GetMapping("/register")
    public String viewRegister(Model model) {
        List<String> branches = Arrays.asList("CSE", "ECE", "EEE", "Mechanical", "Civil", "Chemical", "Metallurgy", "Mining", "Ceramic", "Pharmaceutics");
        model.addAttribute("branches", branches);
        return "register";
    }
    
    @PostMapping("/register")
    public String doRegister(Student student) {
        if(student.getPassword() == null || student.getPassword().isEmpty()) {
            student.setPassword(student.getRollNumber());
        }
        studentRepository.save(student);
        return "redirect:/login?success=Registered";
    }

    @PostMapping("/login")
    public String doLogin(@RequestParam String rollNumber, @RequestParam String password, HttpSession session, Model model) {
        if ("0".equals(rollNumber) && "0".equals(password)) {
            session.setAttribute("USER_ROLL", "0");
            session.setAttribute("USER_NAME", "Super Admin");
            session.setAttribute("IS_SUPER_ADMIN", true);
            return "redirect:/";
        }
        
        Student student = studentRepository.findById(rollNumber).orElse(null);
        if (student != null && student.getPassword() != null && student.getPassword().equals(password)) {
            session.setAttribute("USER_ROLL", student.getRollNumber());
            session.setAttribute("USER_NAME", student.getName());
            session.setAttribute("IS_SUPER_ADMIN", false);
            return "redirect:/";
        } else {
            model.addAttribute("error", "Invalid Roll Number or Password!");
            return "login";
        }
    }
    
    @GetMapping("/profile")
    public String viewProfile(@RequestParam(required=false) String rollNumber, HttpSession session, Model model) {
        String loggedInUser = (String) session.getAttribute("USER_ROLL");
        if(loggedInUser == null) return "redirect:/login";

        String targetRoll = (rollNumber != null) ? rollNumber : loggedInUser;
        Student student = studentRepository.findById(targetRoll).orElseThrow();
        model.addAttribute("student", student);
        model.addAttribute("isSelf", targetRoll.equals(loggedInUser));

        return "profile";
    }

    @GetMapping("/logout")
    public String logout(HttpSession session) {
        session.invalidate();
        return "redirect:/login";
    }
}"""
with open(os.path.join(controller_dir, "AuthController.java"), 'w') as f: f.write(auth_code)

# 3. Update CouncilController.java (GenSec Checks, POR Demotion)
council_code = """package com.college.clubmanagement.controller;

import com.college.clubmanagement.entity.*;
import com.college.clubmanagement.repository.*;
import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import java.util.Optional;

@Controller
public class CouncilController {

    private final ClubRepository clubRepository;
    private final PorRoleRepository roleRepository;
    private final ClubMembershipRepository membershipRepository;
    private final StudentRepository studentRepository;
    private final RoomRepository roomRepository;
    private final ClubRoomAllocationRepository roomAllocationRepository;
    private final CouncilRepository councilRepository;

    public CouncilController(ClubRepository clubRepository, PorRoleRepository roleRepository,
                           ClubMembershipRepository membershipRepository, StudentRepository studentRepository,
                           RoomRepository roomRepository, ClubRoomAllocationRepository roomAllocationRepository,
                           CouncilRepository councilRepository) {
        this.clubRepository = clubRepository;
        this.roleRepository = roleRepository;
        this.membershipRepository = membershipRepository;
        this.studentRepository = studentRepository;
        this.roomRepository = roomRepository;
        this.roomAllocationRepository = roomAllocationRepository;
        this.councilRepository = councilRepository;
    }

    @GetMapping("/gensec")
    public String viewGenSecDashboard(HttpSession session, Model model) {
        String rollNumber = (String) session.getAttribute("USER_ROLL");
        if (rollNumber == null) return "redirect:/login";

        Integer councilId = null;
        for (ClubMembership m : membershipRepository.findAll()) {
            if (m.getStudent().getRollNumber().equals(rollNumber) && m.getRole() != null && "GenSec".equalsIgnoreCase(m.getRole().getTitle())) {
                councilId = m.getRole().getCouncil().getCouncilId();
                break;
            }
        }
        
        if (councilId == null) return "redirect:/?error=NotGenSec";
        
        final Integer cid = councilId;

        List<Club> myClubs = clubRepository.findAll().stream()
                .filter(c -> c.getCouncil().getCouncilId().equals(cid)).collect(Collectors.toList());
        model.addAttribute("clubs", myClubs);

        model.addAttribute("roles", roleRepository.findAll().stream()
                .filter(r -> r.getCouncil().getCouncilId().equals(cid) && r.getClub() != null).collect(Collectors.toList()));
        
        model.addAttribute("memberships", membershipRepository.findAll().stream()
                .filter(m -> m.getClub() != null && m.getClub().getCouncil().getCouncilId().equals(cid) && m.getRole() != null)
                .collect(Collectors.toList()));

        model.addAttribute("rooms", roomRepository.findAll());
        model.addAttribute("allocations", roomAllocationRepository.findAll().stream()
                .filter(a -> a.getClub().getCouncil().getCouncilId().equals(cid)).collect(Collectors.toList()));

        return "gensec";
    }

    @PostMapping("/gensec/create-role")
    public String createRole(@RequestParam Integer clubId, @RequestParam String title, 
                             @RequestParam(required=false) boolean canEditMembers, 
                             @RequestParam(required=false) boolean canEditPors, 
                             @RequestParam(required=false) boolean canFloatForms,
                             @RequestParam(required=false) boolean canViewEmail,
                             @RequestParam(required=false) boolean canViewPhone) {
        
        List<String> perms = new ArrayList<>();
        if(canEditMembers) perms.add("\\"MANAGE_MEMBERS\\"");
        if(canEditPors) perms.add("\\"MANAGE_PORS\\"");
        if(canFloatForms) perms.add("\\"CREATE_FORMS\\"");
        if(canViewEmail) perms.add("\\"VIEW_EMAIL\\"");
        if(canViewPhone) perms.add("\\"VIEW_PHONE\\"");
        
        String json = "[" + String.join(",", perms) + "]";

        Club club = clubRepository.findById(clubId).orElseThrow();
        PorRole role = new PorRole();
        role.setClub(club);
        role.setCouncil(club.getCouncil());
        role.setTitle(title);
        role.setPermissionsJson(json);
        roleRepository.save(role);
        return "redirect:/gensec?success=RoleCreated";
    }
    
    @PostMapping("/gensec/assign-por")
    public String assignPor(@RequestParam String rollNumber, @RequestParam Integer roleId, @RequestParam Integer clubId) {
        Student student = studentRepository.findById(rollNumber).orElseThrow();
        PorRole role = roleRepository.findById(roleId).orElseThrow();
        Club club = clubRepository.findById(clubId).orElseThrow();

        // INTEGRITY CHECK: Must already be a member of the club
        Optional<ClubMembership> existing = membershipRepository.findAll().stream()
            .filter(m -> m.getClub() != null && m.getClub().getClubId().equals(clubId) && m.getStudent().getRollNumber().equals(rollNumber))
            .findFirst();
            
        if(existing.isEmpty()) {
            return "redirect:/gensec?error=StudentNotMemberOfClub";
        }

        ClubMembership cm = existing.get();
        cm.setRole(role);
        membershipRepository.save(cm);
        return "redirect:/gensec?success=PorAssigned";
    }

    @PostMapping("/gensec/remove-por")
    public String removePor(@RequestParam Integer membershipId) {
        ClubMembership cm = membershipRepository.findById(membershipId).orElseThrow();
        // DEMOTION LOGIC: Strip role, keep membership
        cm.setRole(null);
        membershipRepository.save(cm);
        return "redirect:/gensec?success=PorRemovedDemoted";
    }

    @PostMapping("/gensec/allocate-room")
    public String allocateRoom(@RequestParam Integer clubId, @RequestParam Integer roomId) {
        Club club = clubRepository.findById(clubId).orElseThrow();
        Room room = roomRepository.findById(roomId).orElseThrow();
        
        ClubRoomAllocation alloc = new ClubRoomAllocation();
        alloc.setClub(club);
        alloc.setRoom(room);
        alloc.setAcademicYear("2026-2027");
        roomAllocationRepository.save(alloc);
        return "redirect:/gensec?success=RoomAllocated";
    }
}
"""
with open(os.path.join(controller_dir, "CouncilController.java"), 'w') as f: f.write(council_code)


# 4. Global Exception Handler for Graceful Errors
exception_code = """package com.college.clubmanagement.controller;

import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import java.util.NoSuchElementException;

@ControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(NoSuchElementException.class)
    public String handleNotFound(NoSuchElementException ex, Model model) {
        model.addAttribute("errorMessage", "The requested resource could not be found. It may have been deleted or the ID is invalid.");
        return "error";
    }
    
    @ExceptionHandler(Exception.class)
    public String handleGeneralException(Exception ex, Model model) {
        model.addAttribute("errorMessage", "An unexpected error occurred: " + ex.getMessage());
        return "error";
    }
}"""
with open(os.path.join(controller_dir, "GlobalExceptionHandler.java"), 'w') as f: f.write(exception_code)

error_html = """<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head><title>Error</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"></head>
<body class="bg-light d-flex align-items-center justify-content-center" style="height: 100vh;">
<div class="card shadow-sm p-5 text-center" style="max-width: 500px;">
    <h1 class="text-danger mb-3">Oops!</h1>
    <h5 class="text-secondary mb-4">Something went wrong.</h5>
    <div class="alert alert-danger" th:text="${errorMessage}">Error details.</div>
    <a href="/" class="btn btn-primary mt-3">Return to Dashboard</a>
</div>
</body></html>"""
with open(os.path.join(template_dir, "error.html"), 'w') as f: f.write(error_html)

# 5. AdminController (Only 1 GenSec per council logic)
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

    public AdminController(CouncilRepository councilRepository, StudentRepository studentRepository, 
                           ClubMembershipRepository membershipRepository, PorRoleRepository roleRepository) {
        this.councilRepository = councilRepository;
        this.studentRepository = studentRepository;
        this.membershipRepository = membershipRepository;
        this.roleRepository = roleRepository;
    }

    @GetMapping("/superadmin")
    public String viewAdminDashboard(HttpSession session, Model model) {
        Boolean isSuperAdmin = (Boolean) session.getAttribute("IS_SUPER_ADMIN");
        if (isSuperAdmin == null || !isSuperAdmin) {
            return "redirect:/?error=Unauthorized";
        }
        
        model.addAttribute("councils", councilRepository.findAll());
        
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
        if(councilHasGensec) {
            return "redirect:/superadmin?error=CouncilAlreadyHasGenSec";
        }
        
        Student student = studentRepository.findById(rollNumber).orElseThrow();
        Council council = councilRepository.findById(councilId).orElseThrow();
        
        // Find existing GenSec role for this club or create one
        PorRole role = roleRepository.findAll().stream()
                .filter(r -> "GenSec".equals(r.getTitle()) && r.getClub().getClubId().equals(clubId))
                .findFirst().orElseGet(() -> {
                    PorRole newRole = new PorRole();
                    newRole.setTitle("GenSec");
                    newRole.setCouncil(council);
                    newRole.setClub(council.getClubs().stream().filter(c -> c.getClubId().equals(clubId)).findFirst().orElseThrow());
                    newRole.setPermissionsJson("[\\"MANAGE_MEMBERS\\",\\"MANAGE_PORS\\",\\"CREATE_FORMS\\",\\"VIEW_EMAIL\\",\\"VIEW_PHONE\\"]");
                    return roleRepository.save(newRole);
                });

        ClubMembership cm = new ClubMembership();
        cm.setStudent(student);
        cm.setClub(role.getClub());
        cm.setRole(role);
        cm.setAcademicYear("2026-2027");
        membershipRepository.save(cm);

        return "redirect:/superadmin?success=GenSecAssigned";
    }
}"""
with open(os.path.join(controller_dir, "AdminController.java"), 'w') as f: f.write(admin_code)


# 6. Update HTML Files for Password fields
login_path = os.path.join(template_dir, "login.html")
with open(login_path, 'r') as f: content = f.read()
if 'name="password"' not in content:
    content = content.replace('name="rollNumber" placeholder="Roll Number" required>',
                              'name="rollNumber" placeholder="Roll Number" required>\n<input type="password" class="form-control mb-3" name="password" placeholder="Password" required>')
    with open(login_path, 'w') as f: f.write(content)

register_path = os.path.join(template_dir, "register.html")
with open(register_path, 'r') as f: content = f.read()
if 'name="password"' not in content:
    content = content.replace('name="rollNumber" placeholder="Roll Number" required>',
                              'name="rollNumber" placeholder="Roll Number" required>\n<input type="password" class="form-control mb-2" name="password" placeholder="Password (Optional, defaults to Roll No)">')
    # Update branch to use dropdown
    content = content.replace('<input type="text" class="form-control mb-2" name="branch" placeholder="Branch (e.g. CSE)">',
                              '<select class="form-select mb-2" name="branch" required><option th:each="b : ${branches}" th:value="${b}" th:text="${b}"></option></select>')
    with open(register_path, 'w') as f: f.write(content)

print("Java logic updated for GenSecs, PORs, Passwords, and Graceful Error Handling!")
