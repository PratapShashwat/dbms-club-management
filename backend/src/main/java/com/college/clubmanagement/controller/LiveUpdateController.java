package com.college.clubmanagement.controller;

import com.college.clubmanagement.entity.Club;
import com.college.clubmanagement.repository.ClubRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;
import java.util.Map;
import java.util.Optional;

@RestController
public class LiveUpdateController {
    
    private final ClubRepository clubRepository;
    
    public LiveUpdateController(ClubRepository clubRepository) {
        this.clubRepository = clubRepository;
    }
    
    @GetMapping("/api/version/club/{id}")
    public ResponseEntity<?> getClubVersion(@PathVariable Integer id) {
        Optional<Club> club = clubRepository.findById(id);
        if (club.isPresent()) {
            // Return 0 if optVersion is somehow null
            Long version = club.get().getOptVersion() != null ? club.get().getOptVersion() : 0L;
            return ResponseEntity.ok(Map.of("version", version));
        }
        return ResponseEntity.notFound().build();
    }
}
