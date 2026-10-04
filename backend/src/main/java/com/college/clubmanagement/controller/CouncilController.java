package com.college.clubmanagement.controller;

import com.college.clubmanagement.entity.*;
import com.college.clubmanagement.repository.*;
import com.college.clubmanagement.service.LoggingService;
import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

@org.springframework.transaction.annotation.Transactional
@Controller
public class CouncilController {
    private final ClubRepository clubRepository;
    private final PorRoleRepository roleRepository;
    private final ClubMembershipRepository membershipRepository;
    private final StudentRepository studentRepository;
    private final RoomRepository roomRepository;
    private final ClubRoomAllocationRepository roomAllocationRepository;
    private final CouncilRepository councilRepository;
    private final LoggingService loggingService;

    public CouncilController(ClubRepository clubRepository, PorRoleRepository roleRepository,
                           ClubMembershipRepository membershipRepository, StudentRepository studentRepository,
                           RoomRepository roomRepository, ClubRoomAllocationRepository roomAllocationRepository,
                           CouncilRepository councilRepository, LoggingService loggingService) {
        this.clubRepository = clubRepository;
        this.roleRepository = roleRepository;
        this.membershipRepository = membershipRepository;
        this.studentRepository = studentRepository;
        this.roomRepository = roomRepository;
        this.roomAllocationRepository = roomAllocationRepository;
        this.councilRepository = councilRepository;
        this.loggingService = loggingService;
    }

    @GetMapping("/gensec")
    public String viewGenSecDashboard(HttpSession session, Model model) {
        String rollNumber = (String) session.getAttribute("USER_ROLL");
        if (rollNumber == null) return "redirect:/login";

        Boolean isSuperAdmin = (Boolean) session.getAttribute("IS_SUPER_ADMIN");
        boolean isSuper = (isSuperAdmin != null && isSuperAdmin);

        Integer councilId = null;
        for (ClubMembership m : membershipRepository.findAll()) {
            if (m.getStudent().getRollNumber().equals(rollNumber) && m.getRole() != null && "GenSec".equalsIgnoreCase(m.getRole().getTitle())) {
                councilId = m.getRole().getCouncil().getCouncilId();
                break;
            }
        }
        if (councilId == null && !isSuper) return "redirect:/?error=NotGenSec";
        
        if (isSuper) {
            model.addAttribute("roles", roleRepository.findByClubIsNotNull());
            model.addAttribute("memberships", membershipRepository.findByClubIsNotNullAndRoleIsNotNull());
            model.addAttribute("clubs", clubRepository.findAll());
            model.addAttribute("rooms", roomRepository.findAll());
            model.addAttribute("allocations", roomAllocationRepository.findAll());
            model.addAttribute("isSuperAdmin", true);
        } else {
            final Integer cid = councilId;
            model.addAttribute("roles", roleRepository.findByCouncil_CouncilIdAndClubIsNotNull(cid));
            model.addAttribute("memberships", membershipRepository.findByClub_Council_CouncilIdAndRoleIsNotNull(cid));
            model.addAttribute("clubs", clubRepository.findByCouncil_CouncilId(cid));
            model.addAttribute("rooms", roomRepository.findAll());
            model.addAttribute("allocations", roomAllocationRepository.findByClub_Council_CouncilId(cid));
        }

        return "gensec";
    }

    @PostMapping("/gensec/create-role")
    public String createRole(@RequestParam Integer clubId, @RequestParam String title, 
                             @RequestParam(required=false) boolean canEditMembers, @RequestParam(required=false) boolean canEditPors, 
                             @RequestParam(required=false) boolean canFloatForms, @RequestParam(required=false) boolean canViewEmail,
                             @RequestParam(required=false) boolean canViewPhone, HttpSession session) {
        if("GenSec".equalsIgnoreCase(title)) return "redirect:/gensec?error=You+cannot+create+a+GenSec+role!";
        List<String> perms = new ArrayList<>();
        if(canEditMembers) perms.add("\"MANAGE_MEMBERS\"");
        if(canEditPors) perms.add("\"MANAGE_PORS\"");
        if(canFloatForms) perms.add("\"CREATE_FORMS\"");
        if(canViewEmail) perms.add("\"VIEW_EMAIL\"");
        if(canViewPhone) perms.add("\"VIEW_PHONE\"");
        
        Club club = clubRepository.findById(clubId).orElseThrow();
        PorRole role = new PorRole();
        role.setClub(club);
        role.setCouncil(club.getCouncil());
        role.setTitle(title);
        role.setPermissionsJson("[" + String.join(",", perms) + "]");
        roleRepository.save(role);
        
        loggingService.log(session.getAttribute("USER_ROLL").toString(), "Create POR Template", "Created " + title + " in " + club.getName());
        return "redirect:/gensec?success=RoleCreated";
    }

    @PostMapping("/gensec/delete-role")
    public String deleteRole(@RequestParam Integer roleId, HttpSession session) {
        PorRole role = roleRepository.findById(roleId).orElseThrow();
        if("GenSec".equalsIgnoreCase(role.getTitle())) return "redirect:/gensec?error=GenSec+cannot+delete+GenSec+roles!";
        
        // Demote all users
        membershipRepository.findByRole_RoleId(roleId).forEach(m -> {
            m.setRole(null);
            membershipRepository.save(m);
        });
        roleRepository.delete(role);
        loggingService.log(session.getAttribute("USER_ROLL").toString(), "Delete POR Template", "Deleted " + role.getTitle() + " and demoted all holders");
        return "redirect:/gensec?success=RoleDeletedAndHoldersDemoted";
    }

    @PostMapping("/gensec/allocate-room")
    public String allocateRoom(@RequestParam Integer clubId, @RequestParam Integer roomId, HttpSession session) {
        Club club = clubRepository.findById(clubId).orElseThrow();
        Room room = roomRepository.findById(roomId).orElseThrow();
        ClubRoomAllocation alloc = new ClubRoomAllocation();
        alloc.setClub(club); alloc.setRoom(room); alloc.setAcademicYear("2026-2027");
        roomAllocationRepository.save(alloc);
        loggingService.log(session.getAttribute("USER_ROLL").toString(), "Allocate Room", "Room " + room.getRoomId() + " to " + club.getName());
        return "redirect:/gensec?success=RoomAllocated";
    }
}