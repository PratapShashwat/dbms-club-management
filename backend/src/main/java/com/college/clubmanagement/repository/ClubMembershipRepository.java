package com.college.clubmanagement.repository;

import com.college.clubmanagement.entity.ClubMembership;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface ClubMembershipRepository extends JpaRepository<ClubMembership, Integer> {
    @org.springframework.data.jpa.repository.Query("SELECT m FROM ClubMembership m JOIN FETCH m.club LEFT JOIN FETCH m.role WHERE m.student.rollNumber = :rollNumber")
    java.util.List<ClubMembership> findByStudentRollNumberEager(@org.springframework.data.repository.query.Param("rollNumber") String rollNumber);

    java.util.List<com.college.clubmanagement.entity.ClubMembership> findByClub_ClubId(Integer clubId);
    java.util.List<com.college.clubmanagement.entity.ClubMembership> findByClubIsNotNullAndRoleIsNotNull();
    java.util.List<com.college.clubmanagement.entity.ClubMembership> findByClub_Council_CouncilIdAndRoleIsNotNull(Integer councilId);
    java.util.List<com.college.clubmanagement.entity.ClubMembership> findByRole_RoleId(Integer roleId);
}
