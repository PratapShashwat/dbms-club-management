package com.college.clubmanagement.service;
import com.college.clubmanagement.entity.SystemLog;
import com.college.clubmanagement.repository.SystemLogRepository;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
@Service
public class LoggingService {
    private final SystemLogRepository repo;
    public LoggingService(SystemLogRepository repo) { this.repo = repo; }
    public void log(String actor, String action, String details) {
        SystemLog log = new SystemLog();
        log.setTimestamp(LocalDateTime.now());
        log.setActor(actor);
        log.setAction(action);
        log.setDetails(details);
        repo.save(log);
    }
}