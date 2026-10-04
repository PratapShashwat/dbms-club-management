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
import java.util.Optional;

@org.springframework.transaction.annotation.Transactional
@Controller
public class ClubController {
    private final ClubRepository clubRepository;
    private final VerticalRepository verticalRepository;
    private final ClubMembershipRepository membershipRepository;
    private final DynamicFormRepository formRepository;
    private final StudentRepository studentRepository;
    private final PorRoleRepository roleRepository;
    private final ClubRoomAllocationRepository roomAllocationRepository;
    private final LoggingService loggingService;

    public ClubController(ClubRepository clubRepository, VerticalRepository verticalRepository,
                          ClubMembershipRepository membershipRepository, DynamicFormRepository formRepository,
                          StudentRepository studentRepository, PorRoleRepository roleRepository,
                          ClubRoomAllocationRepository roomAllocationRepository, LoggingService loggingService) {
        this.clubRepository = clubRepository;
        this.verticalRepository = verticalRepository;
        this.membershipRepository = membershipRepository;
        this.formRepository = formRepository;
        this.studentRepository = studentRepository;
        this.roleRepository = roleRepository;
        this.roomAllocationRepository = roomAllocationRepository;
        this.loggingService = loggingService;
    }

    @GetMapping("/club/{id}")
    public String viewClub(@PathVariable Integer id, Model model, HttpSession session) {
        String rollNumber = (String) session.getAttribute("USER_ROLL");
        if (rollNumber == null) return "redirect:/login";

        Club club = clubRepository.findById(id).orElseThrow();
        model.addAttribute("club", club);
        
        Optional<ClubRoomAllocation> alloc = roomAllocationRepository.findByClub_ClubId(id);
        model.addAttribute("allocatedRoom", alloc.orElse(null));

        model.addAttribute("verticals", verticalRepository.findByClub_ClubId(id));
        List<DynamicForm> allForms = formRepository.findByClub_ClubId(id);
        model.addAttribute("clubRoles", roleRepository.findByClub_ClubId(id).stream().filter(r -> !"GenSec".equalsIgnoreCase(r.getTitle())).collect(Collectors.toList()));

        List<ClubMembership> allMembers = membershipRepository.findByClub_ClubId(id);
        
        boolean isCouncilGenSec = membershipRepository.findByStudentRollNumberEager(rollNumber).stream().anyMatch(m -> m.getRole() != null && "GenSec".equals(m.getRole().getTitle()) && m.getRole().getCouncil() != null && m.getRole().getCouncil().getCouncilId().equals(club.getCouncil().getCouncilId()));
        Boolean isSuperAdmin = (Boolean) session.getAttribute("IS_SUPER_ADMIN");
        boolean isSuper = (isSuperAdmin != null && isSuperAdmin);

        ClubMembership myMembership = allMembers.stream().filter(m -> m.getStudent().getRollNumber().equals(rollNumber)).findFirst().orElse(null);
        
        boolean isMember = myMembership != null || isCouncilGenSec || isSuper;
        model.addAttribute("isMember", isMember);

        if (isMember) {
            model.addAttribute("allMembers", allMembers);
            boolean canCreateForms = false, canEditMembers = false, canEditPors = false;
            if (isCouncilGenSec || isSuper) {
                canCreateForms = true; canEditMembers = true; canEditPors = true;
            } else if (myMembership != null && myMembership.getRole() != null && myMembership.getRole().getPermissionsJson() != null) {
                String p = myMembership.getRole().getPermissionsJson();
                canCreateForms = p.contains("CREATE_FORMS"); canEditMembers = p.contains("MANAGE_MEMBERS"); canEditPors = p.contains("MANAGE_PORS");
            }
            model.addAttribute("canCreateForms", canCreateForms); model.addAttribute("canEditMembers", canEditMembers); model.addAttribute("canEditPors", canEditPors);
            model.addAttribute("myCreatedForms", formRepository.findByClub_ClubIdAndCreatedBy_RollNumber(id, rollNumber));
        }
        
        List<DynamicForm> visibleForms = allForms.stream().filter(f -> {
            if ("ALL".equals(f.getTargetAudience())) return true;
            if ("THIS_CLUB".equals(f.getTargetAudience())) return isMember;
            if ("PORS_ONLY".equals(f.getTargetAudience())) {
                return isSuper || isCouncilGenSec || (myMembership != null && myMembership.getRole() != null);
            }
            return false;
        }).collect(Collectors.toList());
        model.addAttribute("forms", visibleForms);

        return "club";
    }

    @PostMapping("/club/{id}/add-member")
    public String addMember(@PathVariable Integer id, @RequestParam String rollNumber, HttpSession session) {
        boolean existsMember = membershipRepository.findAll().stream().anyMatch(m -> m.getClub() != null && m.getClub().getClubId().equals(id) && m.getStudent().getRollNumber().equals(rollNumber) && m.getRole() == null);
        if (existsMember) return "redirect:/club/" + id + "?error=Already+a+member!";
        
        ClubMembership cm = new ClubMembership();
        cm.setStudent(studentRepository.findById(rollNumber).orElseThrow());
        cm.setClub(clubRepository.findById(id).orElseThrow());
        cm.setAcademicYear("2026-2027");
        membershipRepository.save(cm);
        loggingService.log(session.getAttribute("USER_ROLL").toString(), "Add Member", rollNumber + " added to Club " + id);
        return "redirect:/club/" + id + "?success=Added";
    }

    @PostMapping("/club/{id}/assign-por")
    public String assignPor(@PathVariable Integer id, @RequestParam String rollNumber, @RequestParam Integer roleId, HttpSession session) {
        PorRole role = roleRepository.findById(roleId).orElseThrow();
        if("GenSec".equalsIgnoreCase(role.getTitle())) return "redirect:/club/" + id + "?error=Cannot+modify+GenSecs+from+Club+View!";
        
        boolean hasAnyMembership = membershipRepository.findAll().stream().anyMatch(m -> m.getClub() != null && m.getClub().getClubId().equals(id) && m.getStudent().getRollNumber().equals(rollNumber));
        if(!hasAnyMembership) return "redirect:/club/" + id + "?error=Student+must+be+a+member+first!";
        
        ClubMembership emptyMem = membershipRepository.findByClub_ClubId(id).stream().filter(m -> m.getStudent().getRollNumber().equals(rollNumber) && m.getRole() == null).findFirst().orElse(null);
        if(emptyMem != null) {
            emptyMem.setRole(role); membershipRepository.save(emptyMem);
        } else {
            ClubMembership newCm = new ClubMembership();
            newCm.setStudent(studentRepository.findById(rollNumber).orElseThrow());
            newCm.setClub(clubRepository.findById(id).orElseThrow());
            newCm.setRole(role); newCm.setAcademicYear("2026-2027");
            membershipRepository.save(newCm);
        }
        loggingService.log(session.getAttribute("USER_ROLL").toString(), "Assign POR", rollNumber + " given " + role.getTitle());
        return "redirect:/club/" + id + "?success=PorAssigned";
    }
    
    @PostMapping("/club/{id}/remove-por")
    public String removePor(@PathVariable Integer id, @RequestParam String rollNumber, @RequestParam Integer membershipId, HttpSession session) {
        ClubMembership cm = membershipRepository.findById(membershipId).orElseThrow();
        if(cm.getRole() != null && "GenSec".equalsIgnoreCase(cm.getRole().getTitle())) return "redirect:/club/" + id + "?error=Cannot+demote+GenSecs!";
        cm.setRole(null);
        membershipRepository.save(cm);
        loggingService.log(session.getAttribute("USER_ROLL").toString(), "Demote POR", rollNumber + " demoted in club " + id);
        return "redirect:/club/" + id + "?success=PorDemoted";
    }

    @PostMapping("/club/{id}/remove-member")
    public String removeMember(@PathVariable Integer id, @RequestParam String rollNumber, @RequestParam Integer membershipId, HttpSession session) {
        ClubMembership cm = membershipRepository.findById(membershipId).orElseThrow();
        if(cm.getRole() != null && "GenSec".equalsIgnoreCase(cm.getRole().getTitle())) return "redirect:/club/" + id + "?error=Cannot+kick+GenSecs!";
        membershipRepository.delete(cm);
        loggingService.log(session.getAttribute("USER_ROLL").toString(), "Kick Member", rollNumber + " removed from club " + id);
        return "redirect:/club/" + id + "?success=MemberKicked";
    }
}
