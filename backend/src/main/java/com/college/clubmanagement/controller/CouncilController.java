package com.college.clubmanagement.controller;

import com.college.clubmanagement.entity.*;
import com.college.clubmanagement.repository.*;
import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import java.util.Optional;

@Controller
public class CouncilController {

    private final ClubRepository clubRepository;
    private final PorRoleRepository roleRepository;
    private final ClubMembershipRepository membershipRepository;
    private final StudentRepository studentRepository;
    private final RoomRepository roomRepository;
    private final ClubRoomAllocationRepository roomAllocationRepository;
    private final CouncilRepository councilRepository;

    public CouncilController(ClubRepository clubRepository, PorRoleRepository roleRepository,
                           ClubMembershipRepository membershipRepository, StudentRepository studentRepository,
                           RoomRepository roomRepository, ClubRoomAllocationRepository roomAllocationRepository,
                           CouncilRepository councilRepository) {
        this.clubRepository = clubRepository;
        this.roleRepository = roleRepository;
        this.membershipRepository = membershipRepository;
        this.studentRepository = studentRepository;
        this.roomRepository = roomRepository;
        this.roomAllocationRepository = roomAllocationRepository;
        this.councilRepository = councilRepository;
    }

    @GetMapping("/gensec")
    public String viewGenSecDashboard(HttpSession session, Model model) {
        String rollNumber = (String) session.getAttribute("USER_ROLL");
        if (rollNumber == null) return "redirect:/login";

        Integer councilId = null;
        for (ClubMembership m : membershipRepository.findAll()) {
            if (m.getStudent().getRollNumber().equals(rollNumber) && m.getRole() != null && "GenSec".equalsIgnoreCase(m.getRole().getTitle())) {
                councilId = m.getRole().getCouncil().getCouncilId();
                break;
            }
        }
        
        if (councilId == null) return "redirect:/?error=NotGenSec";
        
        final Integer cid = councilId;

        List<Club> myClubs = clubRepository.findAll().stream()
                .filter(c -> c.getCouncil().getCouncilId().equals(cid)).collect(Collectors.toList());
        model.addAttribute("clubs", myClubs);

        model.addAttribute("roles", roleRepository.findAll().stream()
                .filter(r -> r.getCouncil().getCouncilId().equals(cid) && r.getClub() != null).collect(Collectors.toList()));
        
        model.addAttribute("memberships", membershipRepository.findAll().stream()
                .filter(m -> m.getClub() != null && m.getClub().getCouncil().getCouncilId().equals(cid) && m.getRole() != null)
                .collect(Collectors.toList()));

        model.addAttribute("rooms", roomRepository.findAll());
        model.addAttribute("allocations", roomAllocationRepository.findAll().stream()
                .filter(a -> a.getClub().getCouncil().getCouncilId().equals(cid)).collect(Collectors.toList()));

        return "gensec";
    }

    @PostMapping("/gensec/create-role")
    public String createRole(@RequestParam Integer clubId, @RequestParam String title, 
                             @RequestParam(required=false) boolean canEditMembers, 
                             @RequestParam(required=false) boolean canEditPors, 
                             @RequestParam(required=false) boolean canFloatForms,
                             @RequestParam(required=false) boolean canViewEmail,
                             @RequestParam(required=false) boolean canViewPhone) {
        
        List<String> perms = new ArrayList<>();
        if(canEditMembers) perms.add("\"MANAGE_MEMBERS\"");
        if(canEditPors) perms.add("\"MANAGE_PORS\"");
        if(canFloatForms) perms.add("\"CREATE_FORMS\"");
        if(canViewEmail) perms.add("\"VIEW_EMAIL\"");
        if(canViewPhone) perms.add("\"VIEW_PHONE\"");
        
        String json = "[" + String.join(",", perms) + "]";

        Club club = clubRepository.findById(clubId).orElseThrow();
        PorRole role = new PorRole();
        role.setClub(club);
        role.setCouncil(club.getCouncil());
        role.setTitle(title);
        role.setPermissionsJson(json);
        roleRepository.save(role);
        return "redirect:/gensec?success=RoleCreated";
    }
    
    @PostMapping("/gensec/assign-por")
    public String assignPor(@RequestParam String rollNumber, @RequestParam Integer roleId, @RequestParam Integer clubId) {
        Student student = studentRepository.findById(rollNumber).orElseThrow();
        PorRole role = roleRepository.findById(roleId).orElseThrow();
        Club club = clubRepository.findById(clubId).orElseThrow();

        // INTEGRITY CHECK: Must already be a member of the club
        Optional<ClubMembership> existing = membershipRepository.findAll().stream()
            .filter(m -> m.getClub() != null && m.getClub().getClubId().equals(clubId) && m.getStudent().getRollNumber().equals(rollNumber))
            .findFirst();
            
        if(existing.isEmpty()) {
            return "redirect:/gensec?error=StudentNotMemberOfClub";
        }

        ClubMembership cm = existing.get();
        cm.setRole(role);
        membershipRepository.save(cm);
        return "redirect:/gensec?success=PorAssigned";
    }

    @PostMapping("/gensec/remove-por")
    public String removePor(@RequestParam Integer membershipId) {
        ClubMembership cm = membershipRepository.findById(membershipId).orElseThrow();
        // DEMOTION LOGIC: Strip role, keep membership
        cm.setRole(null);
        membershipRepository.save(cm);
        return "redirect:/gensec?success=PorRemovedDemoted";
    }

    @PostMapping("/gensec/allocate-room")
    public String allocateRoom(@RequestParam Integer clubId, @RequestParam Integer roomId) {
        Club club = clubRepository.findById(clubId).orElseThrow();
        Room room = roomRepository.findById(roomId).orElseThrow();
        
        ClubRoomAllocation alloc = new ClubRoomAllocation();
        alloc.setClub(club);
        alloc.setRoom(room);
        alloc.setAcademicYear("2026-2027");
        roomAllocationRepository.save(alloc);
        return "redirect:/gensec?success=RoomAllocated";
    }
}
