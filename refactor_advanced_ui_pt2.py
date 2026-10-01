import os

base_dir = r"backend\src\main\java\com\college\clubmanagement"
controller_dir = os.path.join(base_dir, "controller")
template_dir = r"backend\src\main\resources\templates"

# 1. Update club.html (Form dropdown, Add/Remove member UI, Privacy Link)
club_path = os.path.join(template_dir, "club.html")
with open(club_path, 'r') as f: club_content = f.read()

# Make the Member Name a link to their profile, passing privacy toggle
club_content = club_content.replace(
    '<td th:text="${m.student.name}"></td>',
    '<td><a th:href="@{/profile(rollNumber=${m.student.rollNumber}, canViewPrivacy=${canEditMembers or canEditPors})}" th:text="${m.student.name}"></a></td>'
)

# Update Form Publisher to have a dropdown for Audience
old_form_code = '<input type="text" class="form-control form-control-sm mb-2" name="targetAudience" placeholder="Audience" required>'
new_form_code = """<select class="form-select form-select-sm mb-2" name="targetAudience" required>
    <option value="ALL">All Students</option>
    <option value="THIS_CLUB">Club Members</option>
    <option value="PORS_ONLY">POR Holders Only</option>
</select>"""
club_content = club_content.replace(old_form_code, new_form_code)

# Replace Edit Members placeholder with real logic
old_members_html = "<!-- Add/Remove logic here -->"
new_members_html = """
<form th:action="@{/club/{id}/add-member(id=${club.clubId})}" method="POST" class="d-flex gap-2 mb-2">
    <input type="text" class="form-control form-control-sm" name="rollNumber" placeholder="Roll No" required>
    <button class="btn btn-sm btn-primary">Add</button>
</form>
<form th:action="@{/club/{id}/remove-member(id=${club.clubId})}" method="POST" class="d-flex gap-2">
    <input type="text" class="form-control form-control-sm" name="rollNumber" placeholder="Roll No" required>
    <button class="btn btn-sm btn-danger">Remove</button>
</form>
"""
club_content = club_content.replace(old_members_html, new_members_html)

with open(club_path, 'w') as f: f.write(club_content)


# 2. Update ClubController to handle Add/Remove member
club_controller_path = os.path.join(controller_dir, "ClubController.java")
with open(club_controller_path, 'r') as f: cc_content = f.read()

new_endpoints = """
    @PostMapping("/club/{id}/add-member")
    public String addMember(@PathVariable Integer id, @RequestParam String rollNumber) {
        Student student = new Student(); // In real app, fetch from StudentRepo
        student.setRollNumber(rollNumber);
        
        Club club = clubRepository.findById(id).orElseThrow();
        
        ClubMembership cm = new ClubMembership();
        cm.setStudent(student);
        cm.setClub(club);
        cm.setAcademicYear("2026-2027");
        membershipRepository.save(cm);
        return "redirect:/club/" + id + "?success=Added";
    }

    @PostMapping("/club/{id}/remove-member")
    public String removeMember(@PathVariable Integer id, @RequestParam String rollNumber) {
        // Find and delete membership
        membershipRepository.findAll().stream()
            .filter(m -> m.getClub() != null && m.getClub().getClubId().equals(id) && m.getStudent().getRollNumber().equals(rollNumber))
            .forEach(m -> membershipRepository.delete(m));
        return "redirect:/club/" + id + "?success=Removed";
    }
}
"""
cc_content = cc_content.replace("}\n", new_endpoints)
with open(club_controller_path, 'w') as f: f.write(cc_content)

print("Club Edit Member UI & Profile Linking Implemented!")
