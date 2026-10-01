package com.college.clubmanagement.controller;

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
}