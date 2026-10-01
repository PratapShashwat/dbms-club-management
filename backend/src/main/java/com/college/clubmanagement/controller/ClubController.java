package com.college.clubmanagement.controller;

import com.college.clubmanagement.entity.*;
import com.college.clubmanagement.repository.*;
import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

import java.util.List;
import java.util.stream.Collectors;

@Controller
public class ClubController {

    private final ClubRepository clubRepository;
    private final VerticalRepository verticalRepository;
    private final ClubMembershipRepository membershipRepository;
    private final DynamicFormRepository formRepository;

    public ClubController(ClubRepository clubRepository, VerticalRepository verticalRepository,
                          ClubMembershipRepository membershipRepository, DynamicFormRepository formRepository) {
        this.clubRepository = clubRepository;
        this.verticalRepository = verticalRepository;
        this.membershipRepository = membershipRepository;
        this.formRepository = formRepository;
    }

    @GetMapping("/club/{id}")
    public String viewClub(@PathVariable Integer id, Model model, HttpSession session) {
        String rollNumber = (String) session.getAttribute("USER_ROLL");
        if (rollNumber == null) return "redirect:/login";

        Club club = clubRepository.findById(id).orElseThrow();
        model.addAttribute("club", club);

        model.addAttribute("verticals", verticalRepository.findAll().stream()
                .filter(v -> v.getClub().getClubId().equals(id)).collect(Collectors.toList()));

        List<DynamicForm> forms = formRepository.findAll().stream()
                .filter(f -> f.getClub().getClubId().equals(id)).collect(Collectors.toList());
        model.addAttribute("forms", forms);

        // Check Membership
        List<ClubMembership> allMembers = membershipRepository.findAll().stream()
                .filter(m -> m.getClub() != null && m.getClub().getClubId().equals(id)).collect(Collectors.toList());
        
        ClubMembership myMembership = allMembers.stream().filter(m -> m.getStudent().getRollNumber().equals(rollNumber)).findFirst().orElse(null);
        model.addAttribute("isMember", myMembership != null);

        if (myMembership != null) {
            model.addAttribute("allMembers", allMembers);
            
            String perms = myMembership.getRole() != null ? myMembership.getRole().getPermissionsJson() : "";
            if (perms == null) perms = "";
            
            model.addAttribute("canCreateForms", perms.contains("CREATE_FORMS"));
            model.addAttribute("canEditMembers", perms.contains("MANAGE_MEMBERS"));
            model.addAttribute("canEditPors", perms.contains("MANAGE_PORS"));
            
            model.addAttribute("myCreatedForms", forms.stream().filter(f -> f.getCreatedBy() != null && f.getCreatedBy().getRollNumber().equals(rollNumber)).collect(Collectors.toList()));
        }

        return "club";
    }

    @PostMapping("/club/{id}/add-member")
    public String addMember(@PathVariable Integer id, @RequestParam String rollNumber) {
        Student student = new Student(); // In real app, fetch from StudentRepo
        student.setRollNumber(rollNumber);
        
        Club club = clubRepository.findById(id).orElseThrow();
        
        ClubMembership cm = new ClubMembership();
        cm.setStudent(student);
        cm.setClub(club);
        cm.setAcademicYear("2026-2027");
        membershipRepository.save(cm);
        return "redirect:/club/" + id + "?success=Added";
    }

    @PostMapping("/club/{id}/remove-member")
    public String removeMember(@PathVariable Integer id, @RequestParam String rollNumber) {
        // Find and delete membership
        membershipRepository.findAll().stream()
            .filter(m -> m.getClub() != null && m.getClub().getClubId().equals(id) && m.getStudent().getRollNumber().equals(rollNumber))
            .forEach(m -> membershipRepository.delete(m));
        return "redirect:/club/" + id + "?success=Removed";
    }
}
