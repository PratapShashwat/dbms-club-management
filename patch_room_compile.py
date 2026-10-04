import os

base_dir = r"backend\src\main\java\com\college\clubmanagement\controller"
template_dir = r"backend\src\main\resources\templates"

# Fix CouncilController
council_file = os.path.join(base_dir, "CouncilController.java")
with open(council_file, "r") as f: content = f.read()
content = content.replace('room.getBuildingName() + " to " + club.getName()', '"Room " + room.getRoomId() + " to " + club.getName()')
with open(council_file, "w") as f: f.write(content)

# Fix gensec.html
gensec_file = os.path.join(template_dir, "gensec.html")
with open(gensec_file, "r") as f: content = f.read()
content = content.replace("a.room.buildingName + ' ' + a.room.roomNumber", "'Room ' + a.room.roomId")
content = content.replace("r.buildingName + ' ' + r.roomNumber", "'Room ' + r.roomId")
with open(gensec_file, "w") as f: f.write(content)

# Fix club.html
club_file = os.path.join(template_dir, "club.html")
with open(club_file, "r") as f: content = f.read()
content = content.replace("allocatedRoom.room.buildingName + ' ' + allocatedRoom.room.roomNumber", "'Room ' + allocatedRoom.room.roomId")
with open(club_file, "w") as f: f.write(content)

print("Room properties patched!")
