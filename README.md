# Club Management System (DBMS Project)

A full-stack, enterprise-grade Club & Council Management System built with Java Spring Boot, MySQL, and Thymeleaf. Designed with a custom Y2K/Neobrutalist user interface and built to handle highly concurrent multi-user environments.

## Core Features

- **Role-Based Access Control (RBAC):** Three distinct tiers of permissions: SuperAdmin, Council General Secretary (GenSec), and Club Members.
- **Dynamic Form Builder:** Clubs can dynamically create custom application forms (with text, number, and date fields) and track student submissions.
- **POR Management:** Complete lifecycle management for Positions of Responsibility (POR). SuperAdmins can dynamically create new POR titles and assign them custom JSON permissions.
- **System Audit Logging:** Every critical action (appointing members, deleting clubs, submitting forms) is tracked in an immutable System_Log table for accountability.
- **Y2K Neobrutalist UI:** A uniquely styled frontend using Space Mono typography, hard shadows, and high-contrast borders for a brutalist aesthetic.

## Advanced Architectural Highlights

- **Live Data Polling (Real-Time Sync):** Implemented targeted AJAX background polling on highly-contested views (like the Club Dashboard). If another user modifies the club data, the client instantly detects the version mismatch and alerts the user to refresh.
- **Optimistic Locking:** Fully mitigates "Last Write Wins" race conditions. Entities use @Version tracking so concurrent edits to the same resource safely throw an OptimisticLockException rather than silently overwriting data.
- **N+1 Query Eradication:** Heavily optimized JPA Repositories using @Query and JOIN FETCH. The application strictly avoids .findAll() streaming bottlenecks, ensuring O(1) network trips even with thousands of rows in the remote database.
- **Transactional Atomicity:** All controllers are strictly bound by @Transactional boundaries, ensuring that multi-table inserts/updates automatically rollback if any network or integrity failure occurs mid-request.

## Tech Stack
- **Backend:** Java 17, Spring Boot (Web, Data JPA)
- **Database:** Aiven MySQL 8.x (Cloud Hosted)
- **Frontend:** HTML5, CSS3, Thymeleaf, Bootstrap 5.3
- **Connection Pool:** HikariCP
- **Build Tool:** Maven

## Setup & Deployment

1. Clone the repository.
2. Set your remote database password as an environment variable: \="your_password".
3. Compile the app: mvn clean compile.
4. Run the server: mvn spring-boot:run.
5. Access the application at http://localhost:8080.
