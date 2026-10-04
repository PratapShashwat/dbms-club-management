import os

base_dir = r"backend\src\main\java\com\college\clubmanagement\controller"
club_path = os.path.join(base_dir, "ClubController.java")

club_code = """package com.college.clubmanagement.controller;

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
    private final StudentRepository studentRepository;

    public ClubController(ClubRepository clubRepository, VerticalRepository verticalRepository,
                          ClubMembershipRepository membershipRepository, DynamicFormRepository formRepository,
                          StudentRepository studentRepository) {
        this.clubRepository = clubRepository;
        this.verticalRepository = verticalRepository;
        this.membershipRepository = membershipRepository;
        this.formRepository = formRepository;
        this.studentRepository = studentRepository;
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

        List<ClubMembership> allMembers = membershipRepository.findAll().stream()
                .filter(m -> m.getClub() != null && m.getClub().getClubId().equals(id)).collect(Collectors.toList());
        
        // Check if user is a GenSec of this Club's Council!
        boolean isCouncilGenSec = membershipRepository.findAll().stream()
                .anyMatch(m -> m.getStudent().getRollNumber().equals(rollNumber) 
                            && m.getRole() != null 
                            && "GenSec".equals(m.getRole().getTitle())
                            && m.getRole().getCouncil().getCouncilId().equals(club.getCouncil().getCouncilId()));

        ClubMembership myMembership = allMembers.stream().filter(m -> m.getStudent().getRollNumber().equals(rollNumber)).findFirst().orElse(null);
        
        boolean isMember = myMembership != null || isCouncilGenSec;
        model.addAttribute("isMember", isMember);

        if (isMember) {
            model.addAttribute("allMembers", allMembers);
            
            boolean canCreateForms = false;
            boolean canEditMembers = false;
            boolean canEditPors = false;

            if (isCouncilGenSec) {
                // GenSec has absolute power over the entire council
                canCreateForms = true;
                canEditMembers = true;
                canEditPors = true;
            } else if (myMembership != null && myMembership.getRole() != null) {
                // Parse standard POR permissions
                String perms = myMembership.getRole().getPermissionsJson();
                if (perms != null) {
                    canCreateForms = perms.contains("CREATE_FORMS");
                    canEditMembers = perms.contains("MANAGE_MEMBERS");
                    canEditPors = perms.contains("MANAGE_PORS");
                }
            }
            
            model.addAttribute("canCreateForms", canCreateForms);
            model.addAttribute("canEditMembers", canEditMembers);
            model.addAttribute("canEditPors", canEditPors);
            
            model.addAttribute("myCreatedForms", forms.stream().filter(f -> f.getCreatedBy() != null && f.getCreatedBy().getRollNumber().equals(rollNumber)).collect(Collectors.toList()));
        }

        return "club";
    }

    @PostMapping("/club/{id}/add-member")
    public String addMember(@PathVariable Integer id, @RequestParam String rollNumber) {
        Student student = studentRepository.findById(rollNumber).orElseThrow();
        Club club = clubRepository.findById(id).orElseThrow();
        
        // Prevent duplicate membership
        boolean exists = membershipRepository.findAll().stream()
                .anyMatch(m -> m.getClub() != null && m.getClub().getClubId().equals(id) && m.getStudent().getRollNumber().equals(rollNumber));
        if (exists) return "redirect:/club/" + id + "?error=AlreadyMember";
        
        ClubMembership cm = new ClubMembership();
        cm.setStudent(student);
        cm.setClub(club);
        cm.setAcademicYear("2026-2027");
        membershipRepository.save(cm);
        return "redirect:/club/" + id + "?success=Added";
    }

    @PostMapping("/club/{id}/remove-member")
    public String removeMember(@PathVariable Integer id, @RequestParam String rollNumber) {
        membershipRepository.findAll().stream()
            .filter(m -> m.getClub() != null && m.getClub().getClubId().equals(id) && m.getStudent().getRollNumber().equals(rollNumber))
            .forEach(m -> membershipRepository.delete(m));
        return "redirect:/club/" + id + "?success=Removed";
    }
}
"""

with open(club_path, 'w') as f:
    f.write(club_code)
print("ClubController patched successfully for GenSec cascading powers and StudentRepo injection.")
