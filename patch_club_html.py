import os

template_dir = r"backend\src\main\resources\templates"
club_file = os.path.join(template_dir, "club.html")

with open(club_file, 'r') as f:
    content = f.read()

# Replace header
content = content.replace('<th th:if="${canEditPors}">Demote</th>', '<th th:if="${canEditMembers or canEditPors}">Actions</th>')

# Replace column content
old_col = """                                <td th:if="${canEditPors}">
                                    <form th:if="${m.role != null and m.role.title != 'GenSec'}" th:action="@{/club/{id}/remove-por(id=${club.clubId})}" method="POST">
                                        <input type="hidden" name="rollNumber" th:value="${m.student.rollNumber}">
                                        <input type="hidden" name="membershipId" th:value="${m.membershipId}">
                                        <button class="btn btn-sm btn-danger">Demote</button>
                                    </form>
                                </td>"""

new_col = """                                <td th:if="${canEditMembers or canEditPors}">
                                    <div class="d-flex gap-2">
                                        <form th:if="${canEditPors and m.role != null and m.role.title != 'GenSec'}" th:action="@{/club/{id}/remove-por(id=${club.clubId})}" method="POST">
                                            <input type="hidden" name="rollNumber" th:value="${m.student.rollNumber}">
                                            <input type="hidden" name="membershipId" th:value="${m.membershipId}">
                                            <button class="btn btn-sm btn-warning">Demote POR</button>
                                        </form>
                                        <form th:if="${canEditMembers}" th:action="@{/club/{id}/remove-member(id=${club.clubId})}" method="POST">
                                            <input type="hidden" name="rollNumber" th:value="${m.student.rollNumber}">
                                            <input type="hidden" name="membershipId" th:value="${m.membershipId}">
                                            <button class="btn btn-sm btn-danger" th:text="${m.role == null ? 'Kick Member' : 'Kick & Demote'}"></button>
                                        </form>
                                    </div>
                                </td>"""

content = content.replace(old_col, new_col)

with open(club_file, 'w') as f:
    f.write(content)

print("club.html updated safely.")
