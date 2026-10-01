package com.college.clubmanagement.repository;

import com.college.clubmanagement.entity.Club;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface ClubRepository extends JpaRepository<Club, Integer> {
}
