package com.college.clubmanagement.controller;

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
