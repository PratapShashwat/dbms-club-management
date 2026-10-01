package com.college.clubmanagement.service;

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
}