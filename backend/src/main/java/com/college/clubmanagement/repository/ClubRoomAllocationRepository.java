package com.college.clubmanagement.repository;

import com.college.clubmanagement.entity.ClubRoomAllocation;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface ClubRoomAllocationRepository extends JpaRepository<ClubRoomAllocation, Integer> {
    java.util.Optional<com.college.clubmanagement.entity.ClubRoomAllocation> findByClub_ClubId(Integer clubId);
    java.util.List<com.college.clubmanagement.entity.ClubRoomAllocation> findByClub_Council_CouncilId(Integer councilId);
}
