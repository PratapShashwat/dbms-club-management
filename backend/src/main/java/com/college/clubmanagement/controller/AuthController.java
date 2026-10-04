package com.college.clubmanagement.controller;

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
}