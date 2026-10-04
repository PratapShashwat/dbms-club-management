import os

base_dir = r"backend\src\main\java\com\college\clubmanagement"
controller_dir = os.path.join(base_dir, "controller")
template_dir = r"backend\src\main\resources\templates"

council_code = """package com.college.clubmanagement.controller;

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

        Integer councilId = null;
        for (ClubMembership m : membershipRepository.findAll()) {
            if (m.getStudent().getRollNumber().equals(rollNumber) && m.getRole() != null && "GenSec".equalsIgnoreCase(m.getRole().getTitle())) {
                councilId = m.getRole().getCouncil().getCouncilId();
                break;
            }
        }
        if (councilId == null) return "redirect:/?error=NotGenSec";
        final Integer cid = councilId;
        
        model.addAttribute("roles", roleRepository.findAll().stream().filter(r -> r.getCouncil().getCouncilId().equals(cid) && r.getClub() != null).collect(Collectors.toList()));
        model.addAttribute("memberships", membershipRepository.findAll().stream().filter(m -> m.getClub() != null && m.getClub().getCouncil().getCouncilId().equals(cid) && m.getRole() != null).collect(Collectors.toList()));
        model.addAttribute("clubs", clubRepository.findAll().stream().filter(c -> c.getCouncil().getCouncilId().equals(cid)).collect(Collectors.toList()));
        model.addAttribute("rooms", roomRepository.findAll());
        model.addAttribute("allocations", roomAllocationRepository.findAll().stream().filter(a -> a.getClub().getCouncil().getCouncilId().equals(cid)).collect(Collectors.toList()));

        return "gensec";
    }

    @PostMapping("/gensec/create-role")
    public String createRole(@RequestParam Integer clubId, @RequestParam String title, 
                             @RequestParam(required=false) boolean canEditMembers, @RequestParam(required=false) boolean canEditPors, 
                             @RequestParam(required=false) boolean canFloatForms, @RequestParam(required=false) boolean canViewEmail,
                             @RequestParam(required=false) boolean canViewPhone, HttpSession session) {
        if("GenSec".equalsIgnoreCase(title)) return "redirect:/gensec?error=You+cannot+create+a+GenSec+role!";
        List<String> perms = new ArrayList<>();
        if(canEditMembers) perms.add("\\"MANAGE_MEMBERS\\"");
        if(canEditPors) perms.add("\\"MANAGE_PORS\\"");
        if(canFloatForms) perms.add("\\"CREATE_FORMS\\"");
        if(canViewEmail) perms.add("\\"VIEW_EMAIL\\"");
        if(canViewPhone) perms.add("\\"VIEW_PHONE\\"");
        
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
        membershipRepository.findAll().stream().filter(m -> m.getRole() != null && m.getRole().getRoleId().equals(roleId)).forEach(m -> {
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
        loggingService.log(session.getAttribute("USER_ROLL").toString(), "Allocate Room", room.getBuildingName() + " to " + club.getName());
        return "redirect:/gensec?success=RoomAllocated";
    }
}"""
with open(os.path.join(controller_dir, "CouncilController.java"), 'w') as f: f.write(council_code)

gensec_html = """<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head><title>GenSec Console</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"></head>
<body class="bg-light">
<nav class="navbar navbar-expand-lg navbar-dark bg-success"><div class="container"><a class="navbar-brand" href="#">GenSec Workspace</a><a class="nav-link text-white" href="/">Dashboard</a></div></nav>
<div class="container mt-4">
    <div th:if="${param.error}" class="alert alert-danger fw-bold shadow-sm" th:text="${param.error}"></div>
    <div th:if="${param.success}" class="alert alert-success fw-bold shadow-sm" th:text="${param.success}"></div>

    <div class="row">
        <!-- Room Allocations -->
        <div class="col-md-6 mb-4">
            <div class="card shadow-sm h-100">
                <div class="card-header bg-secondary text-white"><h5 class="mb-0">Council Room Allocations</h5></div>
                <div class="card-body">
                    <ul class="list-group mb-3">
                        <li class="list-group-item d-flex justify-content-between" th:each="a : ${allocations}"><span th:text="${a.club.name}"></span><strong th:text="${a.room.buildingName + ' ' + a.room.roomNumber}"></strong></li>
                    </ul>
                    <form th:action="@{/gensec/allocate-room}" method="POST">
                        <div class="d-flex gap-2">
                            <select class="form-select" name="clubId" required><option th:each="c : ${clubs}" th:value="${c.clubId}" th:text="${c.name}"></option></select>
                            <select class="form-select" name="roomId" required><option th:each="r : ${rooms}" th:value="${r.roomId}" th:text="${r.buildingName + ' ' + r.roomNumber}"></option></select>
                            <button type="submit" class="btn btn-secondary">Allocate</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <!-- POR Templates -->
        <div class="col-md-6 mb-4">
            <div class="card shadow-sm h-100 border-success">
                <div class="card-header bg-success text-white"><h5 class="mb-0">Manage POR Templates</h5></div>
                <div class="card-body">
                    <ul class="list-group mb-3">
                        <li class="list-group-item d-flex justify-content-between align-items-center" th:each="r : ${roles}">
                            <div><strong th:text="${r.title}"></strong> <small th:text="'(' + ${r.club.name} + ')'"></small></div>
                            <form th:action="@{/gensec/delete-role}" method="POST" th:if="${r.title != 'GenSec'}">
                                <input type="hidden" name="roleId" th:value="${r.roleId}">
                                <button type="submit" class="btn btn-sm btn-danger">Delete & Demote All</button>
                            </form>
                        </li>
                    </ul>
                    <form th:action="@{/gensec/create-role}" method="POST">
                        <input type="text" class="form-control mb-2" name="title" placeholder="POR Title (e.g. Event Manager)" required>
                        <select class="form-select mb-2" name="clubId" required><option th:each="c : ${clubs}" th:value="${c.clubId}" th:text="${c.name}"></option></select>
                        <div class="form-check"><input class="form-check-input" type="checkbox" name="canEditMembers"><label class="form-check-label">Can Edit Members</label></div>
                        <div class="form-check"><input class="form-check-input" type="checkbox" name="canEditPors"><label class="form-check-label">Can Assign PORs</label></div>
                        <div class="form-check"><input class="form-check-input" type="checkbox" name="canFloatForms"><label class="form-check-label">Can Create Forms</label></div>
                        <button type="submit" class="btn btn-success mt-2 w-100">Create Template</button>
                    </form>
                </div>
            </div>
        </div>

        <!-- All Council POR Holders Display Only -->
        <div class="col-md-12 mb-4">
            <div class="card shadow-sm">
                <div class="card-header"><h5>All Current POR Holders in Council</h5></div>
                <div class="card-body">
                    <table class="table">
                        <thead><tr><th>Name</th><th>Roll No</th><th>Club</th><th>POR Title</th></tr></thead>
                        <tbody><tr th:each="m : ${memberships}"><td th:text="${m.student.name}"></td><td th:text="${m.student.rollNumber}"></td><td th:text="${m.club.name}"></td><td><span class="badge bg-primary" th:text="${m.role.title}"></span></td></tr></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div></body></html>"""
with open(os.path.join(template_dir, "gensec.html"), 'w') as f: f.write(gensec_html)

print("Phase 2/3 written.")
