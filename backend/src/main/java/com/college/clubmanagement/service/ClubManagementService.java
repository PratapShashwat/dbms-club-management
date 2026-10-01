package com.college.clubmanagement.service;

import com.college.clubmanagement.entity.*;
import com.college.clubmanagement.repository.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ClubManagementService {

    private final FormSubmissionRepository formSubmissionRepository;
    private final ClubMembershipRepository clubMembershipRepository;

    public ClubManagementService(FormSubmissionRepository formSubmissionRepository,
                                 ClubMembershipRepository clubMembershipRepository) {
        this.formSubmissionRepository = formSubmissionRepository;
        this.clubMembershipRepository = clubMembershipRepository;
    }

    @Transactional
    public void approveSubmission(Integer submissionId) {
        FormSubmission sub = formSubmissionRepository.findById(submissionId)
                .orElseThrow(() -> new RuntimeException("Submission not found"));
        
        if (!"Pending".equals(sub.getStatus())) {
            throw new RuntimeException("Already processed.");
        }
        
        sub.setStatus("Approved");
        formSubmissionRepository.save(sub);

        // Dynamic execution based on Form Type!
        String type = sub.getDynamicForm().getFormType();
        
        if ("MEMBERSHIP".equals(type)) {
            ClubMembership cm = new ClubMembership();
            cm.setStudent(sub.getStudent());
            cm.setClub(sub.getDynamicForm().getClub());
            cm.setAcademicYear("2026-2027");
            // Role_ID would be assigned here logically
            clubMembershipRepository.save(cm);
        }
    }

    @Transactional
    public void rejectSubmission(Integer submissionId) {
        FormSubmission sub = formSubmissionRepository.findById(submissionId).orElseThrow();
        sub.setStatus("Rejected");
        formSubmissionRepository.save(sub);
    }
}
