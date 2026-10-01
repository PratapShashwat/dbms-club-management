import os

repos_dir = r"backend\src\main\java\com\college\clubmanagement\repository"
service_dir = r"backend\src\main\java\com\college\clubmanagement\service"
os.makedirs(repos_dir, exist_ok=True)
os.makedirs(service_dir, exist_ok=True)

repos = {
    "StudentRepository.java": "String",
    "CouncilRepository.java": "Integer",
    "ClubRepository.java": "Integer",
    "VerticalRepository.java": "Integer",
    "EventRepository.java": "Integer",
    "RoomRepository.java": "Integer",
    "ClubMembershipRepository.java": "Integer",
    "ClubRoomAllocationRepository.java": "Integer",
    "EventInvolvementRepository.java": "Integer",
    "FormMembershipRepository.java": "Integer",
    "FormEventRegRepository.java": "Integer",
    "FormRoomAccessRepository.java": "Integer"
}

for repo_file, id_type in repos.items():
    entity_name = repo_file.replace("Repository.java", "")
    content = f"""package com.college.clubmanagement.repository;

import com.college.clubmanagement.entity.{entity_name};
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface {entity_name}Repository extends JpaRepository<{entity_name}, {id_type}> {{
}}
"""
    with open(os.path.join(repos_dir, repo_file), 'w') as f:
        f.write(content)

service_content = """package com.college.clubmanagement.service;

import com.college.clubmanagement.entity.*;
import com.college.clubmanagement.repository.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class ClubManagementService {

    private final FormMembershipRepository formMembershipRepository;
    private final ClubMembershipRepository clubMembershipRepository;
    
    private final FormRoomAccessRepository formRoomAccessRepository;
    private final ClubRoomAllocationRepository clubRoomAllocationRepository;

    public ClubManagementService(
            FormMembershipRepository formMembershipRepository,
            ClubMembershipRepository clubMembershipRepository,
            FormRoomAccessRepository formRoomAccessRepository,
            ClubRoomAllocationRepository clubRoomAllocationRepository) {
        this.formMembershipRepository = formMembershipRepository;
        this.clubMembershipRepository = clubMembershipRepository;
        this.formRoomAccessRepository = formRoomAccessRepository;
        this.clubRoomAllocationRepository = clubRoomAllocationRepository;
    }

    /**
     * Approves a membership form and automatically inserts a record into Club_Membership
     */
    @Transactional
    public void approveMembershipForm(Integer formId) {
        FormMembership form = formMembershipRepository.findById(formId)
                .orElseThrow(() -> new RuntimeException("Form not found"));

        if (!"Pending".equals(form.getStatus())) {
            throw new RuntimeException("Form is already processed.");
        }

        form.setStatus("Approved");
        formMembershipRepository.save(form);

        ClubMembership membership = new ClubMembership();
        membership.setStudent(form.getApplicant());
        membership.setClub(form.getClub());
        membership.setVertical(form.getVertical());
        membership.setAcademicYear(form.getAcademicYear());
        // POR_Title defaults to "Member" based on Entity definition
        
        clubMembershipRepository.save(membership);
    }

    /**
     * Approves a room access request and automatically allocates the room to the club
     */
    @Transactional
    public void approveRoomAccessForm(Integer formId, String academicYear) {
        FormRoomAccess form = formRoomAccessRepository.findById(formId)
                .orElseThrow(() -> new RuntimeException("Room Form not found"));

        if (!"Pending".equals(form.getStatus())) {
            throw new RuntimeException("Form is already processed.");
        }

        form.setStatus("Approved");
        formRoomAccessRepository.save(form);

        ClubRoomAllocation allocation = new ClubRoomAllocation();
        allocation.setClub(form.getClub());
        allocation.setRoom(form.getRoom());
        allocation.setAcademicYear(academicYear);
        
        clubRoomAllocationRepository.save(allocation);
    }

    /**
     * Rejects a membership form
     */
    @Transactional
    public void rejectMembershipForm(Integer formId) {
        FormMembership form = formMembershipRepository.findById(formId)
                .orElseThrow(() -> new RuntimeException("Form not found"));
        form.setStatus("Rejected");
        formMembershipRepository.save(form);
    }
}
"""

with open(os.path.join(service_dir, "ClubManagementService.java"), 'w') as f:
    f.write(service_content)

print("Generated 12 Repositories and 1 Service class.")
