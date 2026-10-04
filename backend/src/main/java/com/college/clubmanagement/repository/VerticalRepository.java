package com.college.clubmanagement.repository;

import com.college.clubmanagement.entity.Vertical;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface VerticalRepository extends JpaRepository<Vertical, Integer> {
    java.util.List<com.college.clubmanagement.entity.Vertical> findByClub_ClubId(Integer clubId);
}
