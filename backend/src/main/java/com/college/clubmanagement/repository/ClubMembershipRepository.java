package com.college.clubmanagement.repository;

import com.college.clubmanagement.entity.ClubMembership;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface ClubMembershipRepository extends JpaRepository<ClubMembership, Integer> {
}
