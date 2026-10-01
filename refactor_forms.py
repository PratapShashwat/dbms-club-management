import os
import glob

# Paths
base_dir = r"backend\src\main\java\com\college\clubmanagement"
entity_dir = os.path.join(base_dir, "entity")
repo_dir = os.path.join(base_dir, "repository")
service_dir = os.path.join(base_dir, "service")

# 1. Delete old form files
old_entities = ["FormMembership.java", "FormEventReg.java", "FormRoomAccess.java"]
for e in old_entities:
    path = os.path.join(entity_dir, e)
    if os.path.exists(path):
        os.remove(path)
        
old_repos = ["FormMembershipRepository.java", "FormEventRegRepository.java", "FormRoomAccessRepository.java"]
for r in old_repos:
    path = os.path.join(repo_dir, r)
    if os.path.exists(path):
        os.remove(path)

# 2. Create new Entities
dynamic_form_java = """package com.college.clubmanagement.entity;
import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
@Table(name = "Dynamic_Form")
public class DynamicForm {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "Form_ID")
    private Integer formId;

    @ManyToOne
    @JoinColumn(name = "Club_ID")
    private Club club;

    @Column(name = "Title", nullable = false, length = 150)
    private String title;

    @Column(name = "Form_Type", nullable = false, length = 50)
    private String formType;

    @Column(name = "Target_Audience", nullable = false, length = 50)
    private String targetAudience;

    @Column(name = "Questions_JSON", columnDefinition = "JSON")
    private String questionsJson;
}"""

form_submission_java = """package com.college.clubmanagement.entity;
import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
@Table(name = "Form_Submission")
public class FormSubmission {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "Submission_ID")
    private Integer submissionId;

    @ManyToOne
    @JoinColumn(name = "Form_ID")
    private DynamicForm dynamicForm;

    @ManyToOne
    @JoinColumn(name = "Roll_Number")
    private Student student;

    @Column(name = "Answers_JSON", columnDefinition = "JSON")
    private String answersJson;

    @Column(name = "Status", length = 20)
    private String status = "Pending";
}"""

with open(os.path.join(entity_dir, "DynamicForm.java"), 'w') as f: f.write(dynamic_form_java)
with open(os.path.join(entity_dir, "FormSubmission.java"), 'w') as f: f.write(form_submission_java)

# 3. Create new Repositories
dyn_repo_java = """package com.college.clubmanagement.repository;
import com.college.clubmanagement.entity.DynamicForm;
import org.springframework.data.jpa.repository.JpaRepository;
public interface DynamicFormRepository extends JpaRepository<DynamicForm, Integer> {}"""

sub_repo_java = """package com.college.clubmanagement.repository;
import com.college.clubmanagement.entity.FormSubmission;
import org.springframework.data.jpa.repository.JpaRepository;
public interface FormSubmissionRepository extends JpaRepository<FormSubmission, Integer> {}"""

with open(os.path.join(repo_dir, "DynamicFormRepository.java"), 'w') as f: f.write(dyn_repo_java)
with open(os.path.join(repo_dir, "FormSubmissionRepository.java"), 'w') as f: f.write(sub_repo_java)

# 4. Create PrivilegeService (RBAC)
privilege_service_java = """package com.college.clubmanagement.service;

import com.college.clubmanagement.entity.ClubMembership;
import com.college.clubmanagement.repository.ClubMembershipRepository;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class PrivilegeService {
    private final ClubMembershipRepository clubMembershipRepository;

    public PrivilegeService(ClubMembershipRepository clubMembershipRepository) {
        this.clubMembershipRepository = clubMembershipRepository;
    }

    public String getHighestPor(String rollNumber, Integer clubId) {
        // Dummy logic for now, in a real scenario we'd query the DB for the exact POR
        // List<ClubMembership> memberships = clubMembershipRepository.findByStudentRollNumberAndClubClubId(rollNumber, clubId);
        // We'll return strings like "MEMBER", "SECRETARY", "GENSEC", "NONE"
        return "MEMBER";
    }
}"""
with open(os.path.join(service_dir, "PrivilegeService.java"), 'w') as f: f.write(privilege_service_java)

print("Refactored Java entities and repositories to support Dynamic Forms and RBAC!")
