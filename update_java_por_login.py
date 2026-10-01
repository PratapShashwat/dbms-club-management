import os

base_dir = r"backend\src\main\java\com\college\clubmanagement"
entity_dir = os.path.join(base_dir, "entity")
repo_dir = os.path.join(base_dir, "repository")
controller_dir = os.path.join(base_dir, "controller")
template_dir = r"backend\src\main\resources\templates"

# 1. Update ClubMembership.java
club_membership_java = """package com.college.clubmanagement.entity;
import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
@Table(name = "Club_Membership")
public class ClubMembership {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "Membership_ID")
    private Integer membershipId;

    @ManyToOne
    @JoinColumn(name = "Roll_Number")
    private Student student;

    @ManyToOne
    @JoinColumn(name = "Club_ID")
    private Club club;

    @ManyToOne
    @JoinColumn(name = "Vertical_ID")
    private Vertical vertical;

    @ManyToOne
    @JoinColumn(name = "Role_ID")
    private PorRole role;

    @Column(name = "Academic_Year", length = 10)
    private String academicYear;
}"""
with open(os.path.join(entity_dir, "ClubMembership.java"), 'w') as f: f.write(club_membership_java)

# 2. Create PorRole.java
por_role_java = """package com.college.clubmanagement.entity;
import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
@Table(name = "POR_Role")
public class PorRole {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "Role_ID")
    private Integer roleId;

    @ManyToOne
    @JoinColumn(name = "Council_ID")
    private Council council;

    @ManyToOne
    @JoinColumn(name = "Club_ID")
    private Club club;

    @Column(name = "Title", length = 100)
    private String title;

    @Column(name = "Permissions_JSON", columnDefinition = "JSON")
    private String permissionsJson;
}"""
with open(os.path.join(entity_dir, "PorRole.java"), 'w') as f: f.write(por_role_java)

# 3. Create PorRoleRepository.java
repo_java = """package com.college.clubmanagement.repository;
import com.college.clubmanagement.entity.PorRole;
import org.springframework.data.jpa.repository.JpaRepository;
public interface PorRoleRepository extends JpaRepository<PorRole, Integer> {}"""
with open(os.path.join(repo_dir, "PorRoleRepository.java"), 'w') as f: f.write(repo_java)

# 4. Create AuthController.java
auth_controller = """package com.college.clubmanagement.controller;

import com.college.clubmanagement.entity.Student;
import com.college.clubmanagement.repository.StudentRepository;
import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

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
    
    @PostMapping("/login")
    public String doLogin(@RequestParam String rollNumber, HttpSession session, Model model) {
        // Special Super Admin check
        if ("0".equals(rollNumber)) {
            session.setAttribute("USER_ROLL", "0");
            session.setAttribute("USER_NAME", "Super Admin");
            session.setAttribute("IS_SUPER_ADMIN", true);
            return "redirect:/";
        }
        
        // Normal Student Check
        Student student = studentRepository.findById(rollNumber).orElse(null);
        if (student != null) {
            session.setAttribute("USER_ROLL", student.getRollNumber());
            session.setAttribute("USER_NAME", student.getName());
            session.setAttribute("IS_SUPER_ADMIN", false);
            return "redirect:/";
        } else {
            model.addAttribute("error", "Roll Number not found! Ask Admin to register you.");
            return "login";
        }
    }
    
    @GetMapping("/logout")
    public String logout(HttpSession session) {
        session.invalidate();
        return "redirect:/login";
    }
}"""
with open(os.path.join(controller_dir, "AuthController.java"), 'w') as f: f.write(auth_controller)

# 5. Create login.html
login_html = """<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <title>Login - Club Management</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light d-flex align-items-center justify-content-center" style="height: 100vh;">

<div class="card shadow-sm p-4" style="width: 100%; max-width: 400px;">
    <h3 class="text-center mb-4 text-primary">Login</h3>
    
    <div th:if="${error}" class="alert alert-danger" th:text="${error}"></div>
    
    <form th:action="@{/login}" method="POST">
        <div class="mb-3">
            <label for="rollNumber" class="form-label">Roll Number</label>
            <input type="text" class="form-control" id="rollNumber" name="rollNumber" required placeholder="e.g. 24075074 or 0 for Admin">
        </div>
        <button type="submit" class="btn btn-primary w-100">Sign In</button>
    </form>
</div>

</body>
</html>"""
with open(os.path.join(template_dir, "login.html"), 'w') as f: f.write(login_html)

print("Java files updated to support Auth and POR Role Matrix!")
