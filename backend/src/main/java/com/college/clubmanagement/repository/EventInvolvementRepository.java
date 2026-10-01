package com.college.clubmanagement.repository;

import com.college.clubmanagement.entity.EventInvolvement;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface EventInvolvementRepository extends JpaRepository<EventInvolvement, Integer> {
}
