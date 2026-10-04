import os
ctrl_file = r"backend\src\main\java\com\college\clubmanagement\controller\AuthController.java"
with open(ctrl_file, "r") as f:
    content = f.read()

content = content.replace('membershipRepository.findByStudent_RollNumber(rollNumber)', 'membershipRepository.findByStudentRollNumberEager(rollNumber)')

with open(ctrl_file, "w") as f:
    f.write(content)

print("Fixed AuthController")
