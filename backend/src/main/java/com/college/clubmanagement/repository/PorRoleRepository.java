package com.college.clubmanagement.repository;
import com.college.clubmanagement.entity.PorRole;
import org.springframework.data.jpa.repository.JpaRepository;
public interface PorRoleRepository extends JpaRepository<PorRole, Integer> {    java.util.List<com.college.clubmanagement.entity.PorRole> findByClub_ClubId(Integer clubId);
    java.util.List<com.college.clubmanagement.entity.PorRole> findByClubIsNotNull();
    java.util.List<com.college.clubmanagement.entity.PorRole> findByCouncil_CouncilIdAndClubIsNotNull(Integer councilId);
}
