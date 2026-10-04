import os

repo_file = r"backend\src\main\java\com\college\clubmanagement\repository\ClubMembershipRepository.java"
with open(repo_file, "r") as f:
    content = f.read()

if "findByStudentRollNumberEager" not in content:
    content = content.replace("public interface ClubMembershipRepository extends JpaRepository<ClubMembership, Integer> {", 
                              "public interface ClubMembershipRepository extends JpaRepository<ClubMembership, Integer> {\n" +
                              "    @org.springframework.data.jpa.repository.Query(\"SELECT m FROM ClubMembership m JOIN FETCH m.club LEFT JOIN FETCH m.role WHERE m.student.rollNumber = :rollNumber\")\n" +
                              "    java.util.List<ClubMembership> findByStudentRollNumberEager(@org.springframework.data.repository.query.Param(\"rollNumber\") String rollNumber);\n")
    with open(repo_file, "w") as f:
        f.write(content)

ctrl_file = r"backend\src\main\java\com\college\clubmanagement\controller\DashboardController.java"
with open(ctrl_file, "r") as f:
    content = f.read()

# Replace isGenSec
old_gen_sec = '''boolean isGenSec = clubMembershipRepository.findAll().stream()
                .anyMatch(m -> m.getStudent().getRollNumber().equals(rollNumber) && m.getRole() != null && "GenSec".equals(m.getRole().getTitle()));'''
new_gen_sec = '''var memberships = clubMembershipRepository.findByStudentRollNumberEager(rollNumber);
        boolean isGenSec = memberships.stream()
                .anyMatch(m -> m.getRole() != null && "GenSec".equals(m.getRole().getTitle()));'''
content = content.replace(old_gen_sec, new_gen_sec)

# Replace myClubs
old_my_clubs = '''List<Club> myClubs = clubMembershipRepository.findAll().stream()
                .filter(m -> m.getStudent().getRollNumber().equals(rollNumber))
                .map(m -> m.getClub())
                .filter(c -> c != null)
                .collect(Collectors.toList());'''
new_my_clubs = '''List<Club> myClubs = memberships.stream()
                .map(m -> m.getClub())
                .filter(c -> c != null)
                .collect(Collectors.toList());'''
content = content.replace(old_my_clubs, new_my_clubs)

with open(ctrl_file, "w") as f:
    f.write(content)

print("Eager fetching applied to Dashboard")
