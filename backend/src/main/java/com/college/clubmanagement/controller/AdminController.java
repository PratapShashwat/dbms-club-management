package com.college.clubmanagement.controller;

import com.college.clubmanagement.entity.*;
import com.college.clubmanagement.repository.*;
import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

@Controller
public class AdminController {

    private final CouncilRepository councilRepository;
    private final PorRoleRepository roleRepository;
    private final ClubMembershipRepository membershipRepository;
    private final StudentRepository studentRepository;

    public AdminController(CouncilRepository councilRepository, PorRoleRepository roleRepository,
                           ClubMembershipRepository membershipRepository, StudentRepository studentRepository) {
        this.councilRepository = councilRepository;
        this.roleRepository = roleRepository;
        this.membershipRepository = membershipRepository;
        this.studentRepository = studentRepository;
    }

    @GetMapping("/superadmin")
    public String viewSuperAdmin(HttpSession session, Model model) {
        Boolean isSuper = (Boolean) session.getAttribute("IS_SUPER_ADMIN");
        if (isSuper == null || !isSuper) {
            return "redirect:/"; // Block non-admins
        }

        model.addAttribute("councils", councilRepository.findAll());
        // Only fetch Council-level roles (GenSecs)
        model.addAttribute("gensecRoles", roleRepository.findAll().stream()
                .filter(r -> r.getClub() == null).toList());
        
        return "superadmin";
    }

    @PostMapping("/superadmin/assign-gensec")
    public String assignGenSec(@RequestParam String rollNumber, @RequestParam Integer roleId) {
        Student student = studentRepository.findById(rollNumber).orElseThrow();
        PorRole role = roleRepository.findById(roleId).orElseThrow();

        ClubMembership cm = new ClubMembership();
        cm.setStudent(student);
        cm.setRole(role);
        // Club_ID is left null for GenSecs
        cm.setAcademicYear("2026-2027");
        membershipRepository.save(cm);

        return "redirect:/superadmin?success=GenSecAssigned";
    }
}
