import os

base_dir = r"backend\src\main\java\com\college\clubmanagement\controller"
club_path = os.path.join(base_dir, "ClubController.java")

with open(club_path, 'r') as f:
    content = f.read()

# Replace the simplistic forms logic
old_forms_logic = """model.addAttribute("forms", formRepository.findAll().stream().filter(f -> f.getClub().getClubId().equals(id)).collect(Collectors.toList()));"""
new_forms_logic = """List<DynamicForm> allForms = formRepository.findAll().stream().filter(f -> f.getClub().getClubId().equals(id)).collect(Collectors.toList());"""

content = content.replace(old_forms_logic, new_forms_logic)

# Now, insert the filtering logic AFTER isMember, isSuper, etc are defined.
# I need to insert it right before `return "club";`

old_return = """return "club";"""
new_return = """
        List<DynamicForm> visibleForms = allForms.stream().filter(f -> {
            if ("ALL".equals(f.getTargetAudience())) return true;
            if ("THIS_CLUB".equals(f.getTargetAudience())) return isMember;
            if ("PORS_ONLY".equals(f.getTargetAudience())) {
                return isSuper || isCouncilGenSec || (myMembership != null && myMembership.getRole() != null);
            }
            return false;
        }).collect(Collectors.toList());
        model.addAttribute("forms", visibleForms);

        return "club";"""

content = content.replace(old_return, new_return)

with open(club_path, 'w') as f:
    f.write(content)

print("ClubController Forms Target Audience Filter patched.")
