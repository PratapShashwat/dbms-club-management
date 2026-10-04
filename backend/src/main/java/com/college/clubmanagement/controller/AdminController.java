package com.college.clubmanagement.controller;
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
                    newRole.setPermissionsJson("[\"MANAGE_MEMBERS\",\"MANAGE_PORS\",\"CREATE_FORMS\",\"VIEW_EMAIL\",\"VIEW_PHONE\"]");
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
}