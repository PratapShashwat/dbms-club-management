import os

base_dir = r"backend\src\main\java\com\college\clubmanagement\controller"
council_path = os.path.join(base_dir, "CouncilController.java")

with open(council_path, 'r') as f:
    content = f.read()

old_auth = """        Integer councilId = null;
        for (ClubMembership m : membershipRepository.findAll()) {
            if (m.getStudent().getRollNumber().equals(rollNumber) && m.getRole() != null && "GenSec".equalsIgnoreCase(m.getRole().getTitle())) {
                councilId = m.getRole().getCouncil().getCouncilId();
                break;
            }
        }
        if (councilId == null) return "redirect:/?error=NotGenSec";
        final Integer cid = councilId;
        
        model.addAttribute("roles", roleRepository.findAll().stream().filter(r -> r.getCouncil().getCouncilId().equals(cid) && r.getClub() != null).collect(Collectors.toList()));
        model.addAttribute("memberships", membershipRepository.findAll().stream().filter(m -> m.getClub() != null && m.getClub().getCouncil().getCouncilId().equals(cid) && m.getRole() != null).collect(Collectors.toList()));
        model.addAttribute("clubs", clubRepository.findAll().stream().filter(c -> c.getCouncil().getCouncilId().equals(cid)).collect(Collectors.toList()));
        model.addAttribute("rooms", roomRepository.findAll());
        model.addAttribute("allocations", roomAllocationRepository.findAll().stream().filter(a -> a.getClub().getCouncil().getCouncilId().equals(cid)).collect(Collectors.toList()));
"""

new_auth = """        Boolean isSuperAdmin = (Boolean) session.getAttribute("IS_SUPER_ADMIN");
        boolean isSuper = (isSuperAdmin != null && isSuperAdmin);

        Integer councilId = null;
        for (ClubMembership m : membershipRepository.findAll()) {
            if (m.getStudent().getRollNumber().equals(rollNumber) && m.getRole() != null && "GenSec".equalsIgnoreCase(m.getRole().getTitle())) {
                councilId = m.getRole().getCouncil().getCouncilId();
                break;
            }
        }
        if (councilId == null && !isSuper) return "redirect:/?error=NotGenSec";
        
        if (isSuper) {
            model.addAttribute("roles", roleRepository.findAll().stream().filter(r -> r.getClub() != null).collect(Collectors.toList()));
            model.addAttribute("memberships", membershipRepository.findAll().stream().filter(m -> m.getClub() != null && m.getRole() != null).collect(Collectors.toList()));
            model.addAttribute("clubs", clubRepository.findAll());
            model.addAttribute("rooms", roomRepository.findAll());
            model.addAttribute("allocations", roomAllocationRepository.findAll());
            model.addAttribute("isSuperAdmin", true);
        } else {
            final Integer cid = councilId;
            model.addAttribute("roles", roleRepository.findAll().stream().filter(r -> r.getCouncil().getCouncilId().equals(cid) && r.getClub() != null).collect(Collectors.toList()));
            model.addAttribute("memberships", membershipRepository.findAll().stream().filter(m -> m.getClub() != null && m.getClub().getCouncil().getCouncilId().equals(cid) && m.getRole() != null).collect(Collectors.toList()));
            model.addAttribute("clubs", clubRepository.findAll().stream().filter(c -> c.getCouncil().getCouncilId().equals(cid)).collect(Collectors.toList()));
            model.addAttribute("rooms", roomRepository.findAll());
            model.addAttribute("allocations", roomAllocationRepository.findAll().stream().filter(a -> a.getClub().getCouncil().getCouncilId().equals(cid)).collect(Collectors.toList()));
        }
"""

content = content.replace(old_auth, new_auth)
with open(council_path, 'w') as f:
    f.write(content)

print("CouncilController updated.")
