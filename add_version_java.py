import os
import glob
import re

entity_dir = r"backend\src\main\java\com\college\clubmanagement\entity"
entities = ["Club.java", "Council.java", "DynamicForm.java", "ClubMembership.java", "ClubRoomAllocation.java"]

version_field = '''
    @Version
    @Column(name = "opt_version")
    private Long optVersion = 0L;

'''

for entity in entities:
    filepath = os.path.join(entity_dir, entity)
    with open(filepath, "r") as f:
        content = f.read()

    # Add import
    if "jakarta.persistence.Version" not in content:
        content = content.replace("jakarta.persistence.*;", "jakarta.persistence.*;\nimport jakarta.persistence.Version;")
    
    # Add field right after class declaration
    if "private Long optVersion" not in content:
        content = re.sub(r'(public class [A-Za-z]+ \{)', r'\1\n' + version_field, content)

        # Add getter and setter
        getter_setter = '''
    public Long getOptVersion() { return optVersion; }
    public void setOptVersion(Long optVersion) { this.optVersion = optVersion; }
'''
        content = content[:content.rfind('}')] + getter_setter + "\n}"

    with open(filepath, "w") as f:
        f.write(content)

print("Added @Version to entities")
