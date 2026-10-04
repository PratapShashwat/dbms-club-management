import os

base_dir = r"backend\src\main\java\com\college\clubmanagement\controller"
club_path = os.path.join(base_dir, "ClubController.java")

with open(club_path, 'r') as f:
    content = f.read()

# Strip the last '}'
content = content.rstrip()
if content.endswith('}'):
    content = content[:-1]

new_method = """
    @PostMapping("/club/{id}/remove-member")
    public String removeMember(@PathVariable Integer id, @RequestParam String rollNumber, @RequestParam Integer membershipId, HttpSession session) {
        ClubMembership cm = membershipRepository.findById(membershipId).orElseThrow();
        if(cm.getRole() != null && "GenSec".equalsIgnoreCase(cm.getRole().getTitle())) return "redirect:/club/" + id + "?error=Cannot+kick+GenSecs!";
        membershipRepository.delete(cm);
        loggingService.log(session.getAttribute("USER_ROLL").toString(), "Kick Member", rollNumber + " removed from club " + id);
        return "redirect:/club/" + id + "?success=MemberKicked";
    }
}
"""

with open(club_path, 'w') as f:
    f.write(content + new_method)

print("ClubController patched safely.")
