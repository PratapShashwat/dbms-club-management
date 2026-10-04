import os

base_dir = r"backend\src\main\java\com\college\clubmanagement\controller"
auth_path = os.path.join(base_dir, "AuthController.java")

with open(auth_path, 'r') as f:
    content = f.read()

# Replace the login logic
old_logic = """if ("superadmin".equals(rollNumber) && "superadmin".equals(password)) {
            session.setAttribute("USER_ROLL", "0"); session.setAttribute("USER_NAME", "Super Admin"); session.setAttribute("IS_SUPER_ADMIN", true);
            return "redirect:/";
        }
        Student student = studentRepository.findById(rollNumber).orElse(null);"""

new_logic = """if (("superadmin".equals(rollNumber) && "superadmin".equals(password)) || 
            ("0".equals(rollNumber) && "superadmin".equals(password))) {
            session.setAttribute("USER_ROLL", "0"); 
            session.setAttribute("USER_NAME", "Super Admin"); 
            session.setAttribute("IS_SUPER_ADMIN", true);
            return "redirect:/";
        }
        Student student = studentRepository.findById(rollNumber).orElse(null);"""

content = content.replace(old_logic, new_logic)

with open(auth_path, 'w') as f:
    f.write(content)

print("AuthController patched to allow roll number 0 as superadmin.")
