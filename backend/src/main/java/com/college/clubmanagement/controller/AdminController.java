package com.college.clubmanagement.controller;

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
    private final ClubRepository clubRepository;

    public AdminController(CouncilRepository councilRepository, StudentRepository studentRepository, 
                           ClubMembershipRepository membershipRepository, PorRoleRepository roleRepository,
                           ClubRepository clubRepository) {
        this.councilRepository = councilRepository;
        this.studentRepository = studentRepository;
        this.membershipRepository = membershipRepository;
        this.roleRepository = roleRepository;
        this.clubRepository = clubRepository;
    }

    @GetMapping("/superadmin")
    public String viewAdminDashboard(HttpSession session, Model model) {
        Boolean isSuperAdmin = (Boolean) session.getAttribute("IS_SUPER_ADMIN");
        if (isSuperAdmin == null || !isSuperAdmin) return "redirect:/?error=Unauthorized";
        
        model.addAttribute("councils", councilRepository.findAll());
        model.addAttribute("clubs", clubRepository.findAll());
        
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
        if(councilHasGensec) return "redirect:/superadmin?error=CouncilAlreadyHasGenSec";
        
        Student student = studentRepository.findById(rollNumber).orElseThrow();
        Council council = councilRepository.findById(councilId).orElseThrow();
        Club club = clubRepository.findById(clubId).orElseThrow();
        
        PorRole role = roleRepository.findAll().stream()
                .filter(r -> "GenSec".equals(r.getTitle()) && r.getClub().getClubId().equals(clubId))
                .findFirst().orElseGet(() -> {
                    PorRole newRole = new PorRole();
                    newRole.setTitle("GenSec");
                    newRole.setCouncil(council);
                    newRole.setClub(club);
                    newRole.setPermissionsJson("[\"MANAGE_MEMBERS\",\"MANAGE_PORS\",\"CREATE_FORMS\",\"VIEW_EMAIL\",\"VIEW_PHONE\"]");
                    return roleRepository.save(newRole);
                });

        // Ensure user is in the club
        ClubMembership cm = membershipRepository.findAll().stream()
                .filter(m -> m.getStudent().getRollNumber().equals(rollNumber) && m.getClub().getClubId().equals(clubId))
                .findFirst().orElseGet(() -> {
                    ClubMembership newCm = new ClubMembership();
                    newCm.setStudent(student);
                    newCm.setClub(club);
                    newCm.setAcademicYear("2026-2027");
                    return newCm;
                });
        cm.setRole(role);
        membershipRepository.save(cm);
        return "redirect:/superadmin?success=GenSecAssigned";
    }
    
    @PostMapping("/admin/remove-gensec")
    public String removeGenSec(@RequestParam Integer membershipId) {
        ClubMembership cm = membershipRepository.findById(membershipId).orElseThrow();
        cm.setRole(null);
        membershipRepository.save(cm);
        return "redirect:/superadmin?success=GenSecRemoved";
    }
}