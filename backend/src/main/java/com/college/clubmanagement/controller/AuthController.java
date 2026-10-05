package com.college.clubmanagement.controller;
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

@org.springframework.transaction.annotation.Transactional
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
    @GetMapping("/register") 
    public String registerPage(Model model) { 
        model.addAttribute("branches", java.util.Arrays.asList("CSE", "ECE", "EEE", "MECH", "CIVIL", "CHEM", "META", "ARCH"));
        return "register"; 
    }

    @PostMapping("/register")
    public String registerSubmit(
            @RequestParam String rollNumber,
            @RequestParam(required = false) String password,
            @RequestParam String name,
            @RequestParam String email,
            @RequestParam(required = false) String phoneNumber,
            @RequestParam String branch,
            @RequestParam(required = false) String course,
            @RequestParam(required = false) Integer graduationYear,
            HttpSession session) {
            
        if (studentRepository.existsById(rollNumber)) {
            return "redirect:/register?error=RollNumberAlreadyExists";
        }
        
        com.college.clubmanagement.entity.Student student = new com.college.clubmanagement.entity.Student();
        student.setRollNumber(rollNumber);
        student.setPassword(password != null && !password.isEmpty() ? password : rollNumber);
        student.setName(name);
        student.setEmail(email);
        student.setPhoneNumber(phoneNumber);
        student.setBranch(branch);
        student.setCourse(course);
        student.setGraduationYear(graduationYear);
        
        studentRepository.save(student);
        
        session.setAttribute("USER_ROLL", student.getRollNumber());
        session.setAttribute("USER_NAME", student.getName());
        return "redirect:/";
    }

    @GetMapping("/logout") public String logout(HttpSession session) { session.invalidate(); return "redirect:/login"; }

    @PostMapping("/login")
    public String loginSubmit(@RequestParam String rollNumber, @RequestParam String password, HttpSession session) {
        if (("superadmin".equals(rollNumber) && "superadmin".equals(password)) || 
            ("0".equals(rollNumber) && "superadmin".equals(password))) {
            session.setAttribute("USER_ROLL", "0"); 
            session.setAttribute("USER_NAME", "Super Admin"); 
            session.setAttribute("IS_SUPER_ADMIN", true);
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
        model.addAttribute("memberships", membershipRepository.findByStudentRollNumberEager(rollNumber));
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
}