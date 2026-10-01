package com.college.clubmanagement.repository;

import com.college.clubmanagement.entity.Council;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface CouncilRepository extends JpaRepository<Council, Integer> {
}
