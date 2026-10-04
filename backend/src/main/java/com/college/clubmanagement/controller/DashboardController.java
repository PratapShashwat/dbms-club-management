package com.college.clubmanagement.controller;

import com.college.clubmanagement.entity.Club;
import com.college.clubmanagement.entity.Council;
import com.college.clubmanagement.repository.ClubMembershipRepository;
import com.college.clubmanagement.repository.ClubRepository;
import com.college.clubmanagement.repository.CouncilRepository;
import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

import java.util.List;
import java.util.stream.Collectors;

@Controller
public class DashboardController {

    private final ClubRepository clubRepository;
    private final CouncilRepository councilRepository;
    private final ClubMembershipRepository clubMembershipRepository;

    public DashboardController(ClubRepository clubRepository, 
                               CouncilRepository councilRepository,
                               ClubMembershipRepository clubMembershipRepository) {
        this.clubRepository = clubRepository;
        this.councilRepository = councilRepository;
        this.clubMembershipRepository = clubMembershipRepository;
    }

    @GetMapping("/")
    public String viewDashboard(HttpSession session, Model model) {
        String rollNumber = (String) session.getAttribute("USER_ROLL");
        
        if (rollNumber == null) {
            return "redirect:/login"; // Force Login
        }
        
        Boolean isSuperAdmin = (Boolean) session.getAttribute("IS_SUPER_ADMIN");
        model.addAttribute("isSuperAdmin", isSuperAdmin != null && isSuperAdmin);
        model.addAttribute("userName", session.getAttribute("USER_NAME"));

        var memberships = clubMembershipRepository.findByStudentRollNumberEager(rollNumber);
        boolean isGenSec = memberships.stream()
                .anyMatch(m -> m.getRole() != null && "GenSec".equals(m.getRole().getTitle()));
        model.addAttribute("isGenSec", isGenSec);

        // Fetch all Councils to display the 'Explore' hierarchy
        List<Council> allCouncils = councilRepository.findAll();
        model.addAttribute("councils", allCouncils);

        List<Club> allClubs = clubRepository.findAll();
        model.addAttribute("allClubs", allClubs);

        // Fetch clubs the user is a part of
        List<Club> myClubs = memberships.stream()
                .map(m -> m.getClub())
                .filter(c -> c != null)
                .collect(Collectors.toList());
        
        model.addAttribute("myClubs", myClubs);

        return "dashboard";
    }
}
