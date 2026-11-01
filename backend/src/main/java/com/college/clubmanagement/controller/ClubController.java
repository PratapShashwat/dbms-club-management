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

    // ── Auth helpers ─────────────────────────────────────────────────────────────

    private boolean isLoggedIn(HttpSession session) {
        return session.getAttribute("USER_ROLL") != null;
    }

    /**
     * Returns true if the session user has the given permission for this club.
     * SuperAdmin and Council GenSec always pass.
     */
    private boolean hasClubPermission(HttpSession session, Integer clubId, String permission) {
        String roll = (String) session.getAttribute("USER_ROLL");
        if (roll == null) return false;
        Boolean isSuperAdmin = (Boolean) session.getAttribute("IS_SUPER_ADMIN");
        if (Boolean.TRUE.equals(isSuperAdmin)) return true;

        Club club = clubRepository.findById(clubId).orElse(null);
        if (club != null && club.getCouncil() != null) {
            Integer councilId = club.getCouncil().getCouncilId();
            boolean isGenSec = membershipRepository.findByStudentRollNumberEager(roll).stream()
                    .anyMatch(m -> m.getRole() != null && "GenSec".equals(m.getRole().getTitle())
                            && m.getRole().getCouncil() != null
                            && m.getRole().getCouncil().getCouncilId().equals(councilId));
            if (isGenSec) return true;
        }

        return membershipRepository.findByStudentRollNumberEager(roll).stream()
                .anyMatch(m -> m.getClub() != null && m.getClub().getClubId().equals(clubId)
                        && m.getRole() != null && m.getRole().getPermissionsJson() != null
                        && m.getRole().getPermissionsJson().contains(permission));
    }

    // ── GET club view ─────────────────────────────────────────────────────────────

    @GetMapping("/club/{id}")
    public String viewClub(@PathVariable Integer id, Model model, HttpSession session) {
        String rollNumber = (String) session.getAttribute("USER_ROLL");
        if (rollNumber == null) return "redirect:/login";

        Club club = clubRepository.findById(id).orElseThrow();
        model.addAttribute("club", club);

        Optional<ClubRoomAllocation> alloc = roomAllocationRepository.findByClub_ClubId(id);
        model.addAttribute("allocatedRoom", alloc.orElse(null));

        List<Vertical> verticals = verticalRepository.findByClub_ClubId(id);
        model.addAttribute("verticals", verticals);

        List<DynamicForm> allForms = formRepository.findByClub_ClubId(id);
        model.addAttribute("clubRoles", roleRepository.findByClub_ClubId(id).stream()
                .filter(r -> !"GenSec".equalsIgnoreCase(r.getTitle())).collect(Collectors.toList()));

        List<ClubMembership> allMembers = membershipRepository.findByClub_ClubId(id);

        boolean isCouncilGenSec = membershipRepository.findByStudentRollNumberEager(rollNumber).stream()
                .anyMatch(m -> m.getRole() != null && "GenSec".equals(m.getRole().getTitle())
                        && m.getRole().getCouncil() != null
                        && m.getRole().getCouncil().getCouncilId().equals(club.getCouncil().getCouncilId()));
        Boolean isSuperAdmin = (Boolean) session.getAttribute("IS_SUPER_ADMIN");
        boolean isSuper = (isSuperAdmin != null && isSuperAdmin);

        ClubMembership myMembership = allMembers.stream()
                .filter(m -> m.getStudent().getRollNumber().equals(rollNumber)).findFirst().orElse(null);

        boolean isMember = myMembership != null || isCouncilGenSec || isSuper;
        model.addAttribute("isMember", isMember);

        if (isMember) {
            model.addAttribute("allMembers", allMembers);
            boolean canCreateForms = false, canEditMembers = false, canEditPors = false;
            if (isCouncilGenSec || isSuper) {
                canCreateForms = true; canEditMembers = true; canEditPors = true;
            } else if (myMembership != null && myMembership.getRole() != null
                    && myMembership.getRole().getPermissionsJson() != null) {
                String p = myMembership.getRole().getPermissionsJson();
                canCreateForms = p.contains("CREATE_FORMS");
                canEditMembers = p.contains("MANAGE_MEMBERS");
                canEditPors    = p.contains("MANAGE_PORS");
            }
            model.addAttribute("canCreateForms", canCreateForms);
            model.addAttribute("canEditMembers", canEditMembers);
            model.addAttribute("canEditPors", canEditPors);
            model.addAttribute("myCreatedForms",
                    formRepository.findByClub_ClubIdAndCreatedBy_RollNumber(id, rollNumber));
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

    // ── Member management ─────────────────────────────────────────────────────────

    @PostMapping("/club/{id}/add-member")
    public String addMember(@PathVariable Integer id,
                            @RequestParam String rollNumber,
                            @RequestParam(required = false) Integer verticalId,
                            HttpSession session) {
        if (!isLoggedIn(session)) return "redirect:/login";
        if (!hasClubPermission(session, id, "MANAGE_MEMBERS"))
            return "redirect:/club/" + id + "?error=Unauthorized";

        boolean existsMember = membershipRepository.findAll().stream()
                .anyMatch(m -> m.getClub() != null && m.getClub().getClubId().equals(id)
                        && m.getStudent().getRollNumber().equals(rollNumber) && m.getRole() == null);
        if (existsMember) return "redirect:/club/" + id + "?error=Already+a+member!";

        ClubMembership cm = new ClubMembership();
        cm.setStudent(studentRepository.findById(rollNumber).orElseThrow());
        cm.setClub(clubRepository.findById(id).orElseThrow());
        cm.setAcademicYear("2026-2027");
        if (verticalId != null) {
            verticalRepository.findById(verticalId).ifPresent(cm::setVertical);
        }
        membershipRepository.save(cm);
        loggingService.log(session.getAttribute("USER_ROLL").toString(), "Add Member",
                rollNumber + " added to Club " + id);
        return "redirect:/club/" + id + "?success=Added";
    }

    @PostMapping("/club/{id}/assign-por")
    public String assignPor(@PathVariable Integer id,
                            @RequestParam String rollNumber,
                            @RequestParam Integer roleId,
                            HttpSession session) {
        if (!isLoggedIn(session)) return "redirect:/login";
        if (!hasClubPermission(session, id, "MANAGE_PORS"))
            return "redirect:/club/" + id + "?error=Unauthorized";

        PorRole role = roleRepository.findById(roleId).orElseThrow();
        if ("GenSec".equalsIgnoreCase(role.getTitle()))
            return "redirect:/club/" + id + "?error=Cannot+modify+GenSecs+from+Club+View!";

        boolean hasAnyMembership = membershipRepository.findAll().stream()
                .anyMatch(m -> m.getClub() != null && m.getClub().getClubId().equals(id)
                        && m.getStudent().getRollNumber().equals(rollNumber));
        if (!hasAnyMembership)
            return "redirect:/club/" + id + "?error=Student+must+be+a+member+first!";

        ClubMembership emptyMem = membershipRepository.findByClub_ClubId(id).stream()
                .filter(m -> m.getStudent().getRollNumber().equals(rollNumber) && m.getRole() == null)
                .findFirst().orElse(null);
        if (emptyMem != null) {
            emptyMem.setRole(role); membershipRepository.save(emptyMem);
        } else {
            ClubMembership newCm = new ClubMembership();
            newCm.setStudent(studentRepository.findById(rollNumber).orElseThrow());
            newCm.setClub(clubRepository.findById(id).orElseThrow());
            newCm.setRole(role); newCm.setAcademicYear("2026-2027");
            membershipRepository.save(newCm);
        }
        loggingService.log(session.getAttribute("USER_ROLL").toString(), "Assign POR",
                rollNumber + " given " + role.getTitle());
        return "redirect:/club/" + id + "?success=PorAssigned";
    }

    @PostMapping("/club/{id}/remove-por")
    public String removePor(@PathVariable Integer id,
                            @RequestParam String rollNumber,
                            @RequestParam Integer membershipId,
                            HttpSession session) {
        if (!isLoggedIn(session)) return "redirect:/login";
        if (!hasClubPermission(session, id, "MANAGE_PORS"))
            return "redirect:/club/" + id + "?error=Unauthorized";

        ClubMembership cm = membershipRepository.findById(membershipId).orElseThrow();
        if (cm.getRole() != null && "GenSec".equalsIgnoreCase(cm.getRole().getTitle()))
            return "redirect:/club/" + id + "?error=Cannot+demote+GenSecs!";
        cm.setRole(null);
        membershipRepository.save(cm);
        loggingService.log(session.getAttribute("USER_ROLL").toString(), "Demote POR",
                rollNumber + " demoted in club " + id);
        return "redirect:/club/" + id + "?success=PorDemoted";
    }

    @PostMapping("/club/{id}/remove-member")
    public String removeMember(@PathVariable Integer id,
                               @RequestParam String rollNumber,
                               @RequestParam Integer membershipId,
                               HttpSession session) {
        if (!isLoggedIn(session)) return "redirect:/login";
        if (!hasClubPermission(session, id, "MANAGE_MEMBERS"))
            return "redirect:/club/" + id + "?error=Unauthorized";

        ClubMembership cm = membershipRepository.findById(membershipId).orElseThrow();
        if (cm.getRole() != null && "GenSec".equalsIgnoreCase(cm.getRole().getTitle()))
            return "redirect:/club/" + id + "?error=Cannot+kick+GenSecs!";
        membershipRepository.delete(cm);
        loggingService.log(session.getAttribute("USER_ROLL").toString(), "Kick Member",
                rollNumber + " removed from club " + id);
        return "redirect:/club/" + id + "?success=MemberKicked";
    }

    /** Assign or clear a member's vertical. Requires MANAGE_MEMBERS. */
    @PostMapping("/club/{id}/assign-vertical")
    public String assignVertical(@PathVariable Integer id,
                                 @RequestParam Integer membershipId,
                                 @RequestParam(required = false) Integer verticalId,
                                 HttpSession session) {
        if (!isLoggedIn(session)) return "redirect:/login";
        if (!hasClubPermission(session, id, "MANAGE_MEMBERS"))
            return "redirect:/club/" + id + "?error=Unauthorized";

        ClubMembership cm = membershipRepository.findById(membershipId).orElseThrow();
        if (!cm.getClub().getClubId().equals(id))
            return "redirect:/club/" + id + "?error=Invalid+membership";

        cm.setVertical(verticalId != null ? verticalRepository.findById(verticalId).orElse(null) : null);
        membershipRepository.save(cm);
        loggingService.log(session.getAttribute("USER_ROLL").toString(), "Assign Vertical",
                cm.getStudent().getRollNumber() + " vertical updated in club " + id);
        return "redirect:/club/" + id + "?success=VerticalUpdated";
    }

    // ── Vertical CRUD (requires MANAGE_MEMBERS) ───────────────────────────────────

    /** Add a new vertical to this club. Requires MANAGE_MEMBERS. */
    @PostMapping("/club/{id}/create-vertical")
    public String createVertical(@PathVariable Integer id,
                                 @RequestParam String name,
                                 HttpSession session) {
        if (!isLoggedIn(session)) return "redirect:/login";
        if (!hasClubPermission(session, id, "MANAGE_MEMBERS"))
            return "redirect:/club/" + id + "?error=Unauthorized";

        String trimmed = name == null ? "" : name.trim();
        if (trimmed.isEmpty()) return "redirect:/club/" + id + "?error=Vertical+name+cannot+be+empty";

        Vertical v = new Vertical();
        v.setName(trimmed);
        v.setClub(clubRepository.findById(id).orElseThrow());
        verticalRepository.save(v);
        loggingService.log(session.getAttribute("USER_ROLL").toString(), "Create Vertical",
                "Created vertical '" + trimmed + "' in club " + id);
        return "redirect:/club/" + id + "?success=VerticalCreated";
    }

    /** Rename an existing vertical. Requires MANAGE_MEMBERS and vertical must belong to this club. */
    @PostMapping("/club/{id}/rename-vertical")
    public String renameVertical(@PathVariable Integer id,
                                 @RequestParam Integer verticalId,
                                 @RequestParam String name,
                                 HttpSession session) {
        if (!isLoggedIn(session)) return "redirect:/login";
        if (!hasClubPermission(session, id, "MANAGE_MEMBERS"))
            return "redirect:/club/" + id + "?error=Unauthorized";

        String trimmed = name == null ? "" : name.trim();
        if (trimmed.isEmpty()) return "redirect:/club/" + id + "?error=Vertical+name+cannot+be+empty";

        Vertical v = verticalRepository.findById(verticalId).orElseThrow();
        if (!v.getClub().getClubId().equals(id))
            return "redirect:/club/" + id + "?error=Invalid+vertical";
        v.setName(trimmed);
        verticalRepository.save(v);
        loggingService.log(session.getAttribute("USER_ROLL").toString(), "Rename Vertical",
                "Vertical " + verticalId + " renamed to '" + trimmed + "' in club " + id);
        return "redirect:/club/" + id + "?success=VerticalRenamed";
    }

    /**
     * Delete a vertical from this club. Requires MANAGE_MEMBERS.
     * All memberships using this vertical have their vertical cleared first.
     */
    @PostMapping("/club/{id}/delete-vertical")
    public String deleteVertical(@PathVariable Integer id,
                                 @RequestParam Integer verticalId,
                                 HttpSession session) {
        if (!isLoggedIn(session)) return "redirect:/login";
        if (!hasClubPermission(session, id, "MANAGE_MEMBERS"))
            return "redirect:/club/" + id + "?error=Unauthorized";

        Vertical v = verticalRepository.findById(verticalId).orElseThrow();
        if (!v.getClub().getClubId().equals(id))
            return "redirect:/club/" + id + "?error=Invalid+vertical";

        // Detach any memberships using this vertical before deleting
        membershipRepository.findByClub_ClubId(id).stream()
                .filter(m -> m.getVertical() != null && m.getVertical().getVerticalId().equals(verticalId))
                .forEach(m -> { m.setVertical(null); membershipRepository.save(m); });

        verticalRepository.delete(v);
        loggingService.log(session.getAttribute("USER_ROLL").toString(), "Delete Vertical",
                "Deleted vertical " + verticalId + " from club " + id);
        return "redirect:/club/" + id + "?success=VerticalDeleted";
    }
}
