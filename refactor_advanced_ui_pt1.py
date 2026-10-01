import os

base_dir = r"backend\src\main\java\com\college\clubmanagement"
entity_dir = os.path.join(base_dir, "entity")
controller_dir = os.path.join(base_dir, "controller")
template_dir = r"backend\src\main\resources\templates"

# 1. Update Student.java
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
}"""
with open(os.path.join(entity_dir, "Student.java"), 'w') as f: f.write(student_java)


# 2. Update AuthController.java (Register & Profile)
auth_code = """package com.college.clubmanagement.controller;

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

    @GetMapping("/register")
    public String viewRegister() {
        return "register";
    }
    
    @PostMapping("/register")
    public String doRegister(Student student) {
        studentRepository.save(student);
        return "redirect:/login?success=Registered";
    }

    @PostMapping("/login")
    public String doLogin(@RequestParam String rollNumber, HttpSession session, Model model) {
        if ("0".equals(rollNumber)) {
            session.setAttribute("USER_ROLL", "0");
            session.setAttribute("USER_NAME", "Super Admin");
            session.setAttribute("IS_SUPER_ADMIN", true);
            return "redirect:/";
        }
        
        Student student = studentRepository.findById(rollNumber).orElse(null);
        if (student != null) {
            session.setAttribute("USER_ROLL", student.getRollNumber());
            session.setAttribute("USER_NAME", student.getName());
            session.setAttribute("IS_SUPER_ADMIN", false);
            return "redirect:/";
        } else {
            model.addAttribute("error", "Roll Number not found! Please register first.");
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
        
        // In a real system, you'd pull the viewer's highest POR and check Privacy JSON
        // For simplicity in UI, we pass it down and thymeleaf will conditionally hide
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

# 3. Create register.html and profile.html
register_html = """<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head><title>Register</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"></head>
<body class="bg-light d-flex align-items-center justify-content-center" style="height: 100vh;">
<div class="card shadow-sm p-4" style="width: 100%; max-width: 400px;">
    <h3 class="text-center mb-4 text-primary">Student Registration</h3>
    <form th:action="@{/register}" method="POST">
        <input type="text" class="form-control mb-2" name="rollNumber" placeholder="Roll Number" required>
        <input type="text" class="form-control mb-2" name="name" placeholder="Full Name" required>
        <input type="email" class="form-control mb-2" name="email" placeholder="Email" required>
        <input type="text" class="form-control mb-2" name="phoneNumber" placeholder="Phone Number">
        <input type="text" class="form-control mb-2" name="branch" placeholder="Branch (e.g. CSE)">
        <input type="text" class="form-control mb-2" name="course" placeholder="Course (e.g. B.Tech)">
        <input type="number" class="form-control mb-3" name="graduationYear" placeholder="Graduation Year (e.g. 2026)">
        <button type="submit" class="btn btn-primary w-100 mb-2">Register</button>
        <a href="/login" class="btn btn-outline-secondary w-100">Back to Login</a>
    </form>
</div></body></html>"""
with open(os.path.join(template_dir, "register.html"), 'w') as f: f.write(register_html)

profile_html = """<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head><title>Profile</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"></head>
<body class="bg-light">
<nav class="navbar navbar-dark bg-dark mb-4"><div class="container"><a class="navbar-brand" href="/">Dashboard</a></div></nav>
<div class="container">
    <div class="card shadow-sm">
        <div class="card-header bg-primary text-white"><h3>User Profile</h3></div>
        <div class="card-body">
            <p><strong>Name:</strong> <span th:text="${student.name}"></span></p>
            <p><strong>Roll Number:</strong> <span th:text="${student.rollNumber}"></span></p>
            <p><strong>Branch / Course:</strong> <span th:text="${student.branch} + ' ' + ${student.course}"></span></p>
            
            <hr>
            <h5 class="text-secondary">Protected Information</h5>
            <!-- Note: Privacy masking logic simulated based on query params or 'isSelf' -->
            <p th:if="${isSelf or param.canViewPrivacy != null}"><strong>Email:</strong> <span th:text="${student.email}"></span></p>
            <p th:if="${isSelf or param.canViewPrivacy != null}"><strong>Phone:</strong> <span th:text="${student.phoneNumber}"></span></p>
            
            <div th:unless="${isSelf or param.canViewPrivacy != null}" class="alert alert-warning">
                Contact information is hidden. You lack POR privacy viewing rights.
            </div>
        </div>
    </div>
</div></body></html>"""
with open(os.path.join(template_dir, "profile.html"), 'w') as f: f.write(profile_html)

# 4. Modify login.html to add Register button
login_path = os.path.join(template_dir, "login.html")
with open(login_path, 'r') as f: login_content = f.read()
if "Register Here" not in login_content:
    login_content = login_content.replace('</form>', '</form>\n<a href="/register" class="btn btn-outline-secondary w-100 mt-2">Register Here</a>')
    with open(login_path, 'w') as f: f.write(login_content)

print("Auth, Registration, and Profile successfully implemented!")
