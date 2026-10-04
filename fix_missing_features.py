import os

base_dir = r"backend\src\main\java\com\college\clubmanagement\controller"
club_path = os.path.join(base_dir, "ClubController.java")
forms_path = os.path.join(base_dir, "FormsController.java")
club_html_path = r"backend\src\main\resources\templates\club.html"

# 1. Update ClubController.java
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
import java.util.Optional;

@Controller
public class ClubController {

    private final ClubRepository clubRepository;
    private final VerticalRepository verticalRepository;
    private final ClubMembershipRepository membershipRepository;
    private final DynamicFormRepository formRepository;
    private final StudentRepository studentRepository;
    private final PorRoleRepository roleRepository;

    public ClubController(ClubRepository clubRepository, VerticalRepository verticalRepository,
                          ClubMembershipRepository membershipRepository, DynamicFormRepository formRepository,
                          StudentRepository studentRepository, PorRoleRepository roleRepository) {
        this.clubRepository = clubRepository;
        this.verticalRepository = verticalRepository;
        this.membershipRepository = membershipRepository;
        this.formRepository = formRepository;
        this.studentRepository = studentRepository;
        this.roleRepository = roleRepository;
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
        
        model.addAttribute("clubRoles", roleRepository.findAll().stream()
                .filter(r -> r.getClub().getClubId().equals(id)).collect(Collectors.toList()));

        List<ClubMembership> allMembers = membershipRepository.findAll().stream()
                .filter(m -> m.getClub() != null && m.getClub().getClubId().equals(id)).collect(Collectors.toList());
        
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
                canCreateForms = true;
                canEditMembers = true;
                canEditPors = true;
            } else if (myMembership != null && myMembership.getRole() != null) {
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
    
    @PostMapping("/club/{id}/assign-por")
    public String assignPor(@PathVariable Integer id, @RequestParam String rollNumber, @RequestParam Integer roleId) {
        PorRole role = roleRepository.findById(roleId).orElseThrow();
        Optional<ClubMembership> existing = membershipRepository.findAll().stream()
            .filter(m -> m.getClub() != null && m.getClub().getClubId().equals(id) && m.getStudent().getRollNumber().equals(rollNumber))
            .findFirst();
            
        if(existing.isEmpty()) {
            return "redirect:/club/" + id + "?error=StudentNotMemberOfClub";
        }
        ClubMembership cm = existing.get();
        cm.setRole(role);
        membershipRepository.save(cm);
        return "redirect:/club/" + id + "?success=PorAssigned";
    }
    
    @PostMapping("/club/{id}/remove-por")
    public String removePor(@PathVariable Integer id, @RequestParam String rollNumber) {
        Optional<ClubMembership> existing = membershipRepository.findAll().stream()
            .filter(m -> m.getClub() != null && m.getClub().getClubId().equals(id) && m.getStudent().getRollNumber().equals(rollNumber))
            .findFirst();
        if(existing.isPresent()) {
            ClubMembership cm = existing.get();
            cm.setRole(null);
            membershipRepository.save(cm);
        }
        return "redirect:/club/" + id + "?success=PorDemoted";
    }
}
"""
with open(club_path, 'w') as f: f.write(club_code)

# 2. Update FormsController.java
forms_code = """package com.college.clubmanagement.controller;

import com.college.clubmanagement.entity.*;
import com.college.clubmanagement.repository.*;
import com.college.clubmanagement.service.ClubManagementService;
import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.stream.Collectors;

@Controller
public class FormsController {

    private final DynamicFormRepository dynamicFormRepository;
    private final FormSubmissionRepository formSubmissionRepository;
    private final StudentRepository studentRepository;
    private final ClubRepository clubRepository;
    private final ClubManagementService clubManagementService;
    private final ClubMembershipRepository clubMembershipRepository;

    public FormsController(DynamicFormRepository dynamicFormRepository,
                           FormSubmissionRepository formSubmissionRepository,
                           StudentRepository studentRepository,
                           ClubRepository clubRepository,
                           ClubManagementService clubManagementService,
                           ClubMembershipRepository clubMembershipRepository) {
        this.dynamicFormRepository = dynamicFormRepository;
        this.formSubmissionRepository = formSubmissionRepository;
        this.studentRepository = studentRepository;
        this.clubRepository = clubRepository;
        this.clubManagementService = clubManagementService;
        this.clubMembershipRepository = clubMembershipRepository;
    }

    @GetMapping("/form/{id}")
    public String viewForm(@PathVariable Integer id, Model model, HttpSession session) {
        String rollNumber = (String) session.getAttribute("USER_ROLL");
        if (rollNumber == null) return "redirect:/login";

        DynamicForm form = dynamicFormRepository.findById(id).orElseThrow();
        model.addAttribute("form", form);
        
        boolean alreadySubmitted = formSubmissionRepository.findAll().stream()
                .anyMatch(s -> s.getDynamicForm().getFormId().equals(id) && s.getStudent().getRollNumber().equals(rollNumber));
        model.addAttribute("alreadySubmitted", alreadySubmitted);

        return "dynamic-form";
    }

    @PostMapping("/form/{id}/submit")
    public String submitForm(@PathVariable Integer id, @RequestParam String answersJson, HttpSession session) {
        String rollNumber = (String) session.getAttribute("USER_ROLL");
        Student student = studentRepository.findById(rollNumber).orElseThrow();
        DynamicForm form = dynamicFormRepository.findById(id).orElseThrow();

        FormSubmission submission = new FormSubmission();
        submission.setDynamicForm(form);
        submission.setStudent(student);
        submission.setAnswersJson(answersJson);
        submission.setStatus("Pending");
        formSubmissionRepository.save(submission);

        return "redirect:/club/" + form.getClub().getClubId() + "?success=FormSubmitted";
    }

    @PostMapping("/club/{clubId}/create-form")
    public String createForm(@PathVariable Integer clubId, @RequestParam String title, @RequestParam String formType, @RequestParam String targetAudience, @RequestParam String questionsJson, HttpSession session) {
        String rollNumber = (String) session.getAttribute("USER_ROLL");
        Student student = studentRepository.findById(rollNumber).orElseThrow();
        Club club = clubRepository.findById(clubId).orElseThrow();
        
        DynamicForm form = new DynamicForm();
        form.setClub(club);
        form.setTitle(title);
        form.setFormType(formType);
        form.setTargetAudience(targetAudience);
        form.setQuestionsJson(questionsJson);
        form.setCreatedBy(student); // Link to creator!
        
        dynamicFormRepository.save(form);
        return "redirect:/club/" + clubId + "?success=FormCreated";
    }

    @GetMapping("/form/{formId}/submissions")
    public String viewSubmissions(@PathVariable Integer formId, Model model, HttpSession session) {
        String rollNumber = (String) session.getAttribute("USER_ROLL");
        if (rollNumber == null) return "redirect:/login";

        DynamicForm form = dynamicFormRepository.findById(formId).orElseThrow();
        
        Boolean isSuper = (Boolean) session.getAttribute("IS_SUPER_ADMIN");
        boolean isCreator = form.getCreatedBy() != null && form.getCreatedBy().getRollNumber().equals(rollNumber);
        
        boolean isGenSecOfCouncil = clubMembershipRepository.findAll().stream()
                .anyMatch(m -> m.getStudent().getRollNumber().equals(rollNumber) 
                            && m.getRole() != null 
                            && "GenSec".equals(m.getRole().getTitle())
                            && m.getRole().getCouncil().getCouncilId().equals(form.getClub().getCouncil().getCouncilId()));

        if (!isCreator && !isGenSecOfCouncil && (isSuper == null || !isSuper)) {
            return "redirect:/club/" + form.getClub().getClubId() + "?error=Unauthorized";
        }

        model.addAttribute("form", form);

        List<FormSubmission> pendingSubmissions = formSubmissionRepository.findAll().stream()
                .filter(s -> s.getDynamicForm().getFormId().equals(formId) && "Pending".equals(s.getStatus()))
                .collect(Collectors.toList());
        model.addAttribute("pendingForms", pendingSubmissions);

        return "submissions";
    }

    @PostMapping("/form/approve/{subId}")
    public String approve(@PathVariable Integer subId) {
        FormSubmission sub = formSubmissionRepository.findById(subId).orElseThrow();
        clubManagementService.approveSubmission(subId);
        return "redirect:/form/" + sub.getDynamicForm().getFormId() + "/submissions?success=Approved";
    }
    
    @PostMapping("/form/reject/{subId}")
    public String reject(@PathVariable Integer subId) {
        FormSubmission sub = formSubmissionRepository.findById(subId).orElseThrow();
        clubManagementService.rejectSubmission(subId);
        return "redirect:/form/" + sub.getDynamicForm().getFormId() + "/submissions?success=Rejected";
    }
}
"""
with open(forms_path, 'w') as f: f.write(forms_code)

# 3. Update club.html (Replace POR placeholder)
with open(club_html_path, 'r') as f:
    html_content = f.read()

replacement = """
                            <form th:action="@{/club/{id}/assign-por(id=${club.clubId})}" method="POST" class="d-flex flex-column gap-2 mb-2">
                                <input type="text" class="form-control form-control-sm" name="rollNumber" placeholder="Roll No" required>
                                <select class="form-select form-select-sm" name="roleId" required>
                                    <option th:each="r : ${clubRoles}" th:value="${r.roleId}" th:text="${r.title}"></option>
                                    <option th:if="${clubRoles.isEmpty()}" value="" disabled>No PORs created yet</option>
                                </select>
                                <button class="btn btn-sm btn-primary">Assign POR</button>
                            </form>
                            <form th:action="@{/club/{id}/remove-por(id=${club.clubId})}" method="POST" class="d-flex gap-2">
                                <input type="text" class="form-control form-control-sm" name="rollNumber" placeholder="Roll No to Demote" required>
                                <button class="btn btn-sm btn-danger">Demote</button>
                            </form>
"""

html_content = html_content.replace('<!-- Assign logic here -->', replacement)
with open(club_html_path, 'w') as f: f.write(html_content)

print("Finished fixing missing features: Club POR assignment, Demotion, Forms Security GenSec Access!")
