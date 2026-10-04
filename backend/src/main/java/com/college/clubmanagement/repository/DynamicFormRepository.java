package com.college.clubmanagement.repository;
import com.college.clubmanagement.entity.DynamicForm;
import org.springframework.data.jpa.repository.JpaRepository;
public interface DynamicFormRepository extends JpaRepository<DynamicForm, Integer> {    java.util.List<com.college.clubmanagement.entity.DynamicForm> findByClub_ClubId(Integer clubId);
    java.util.List<com.college.clubmanagement.entity.DynamicForm> findByClub_ClubIdAndCreatedBy_RollNumber(Integer clubId, String rollNumber);
}
