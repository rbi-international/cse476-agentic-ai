"""
Prove authentication (salted hash, weak-password reject), authorization (ownership
and roles, the McHire IDOR), and auditing (append-only trail). All offline and
deterministic. McHire failed the first two links; this shows each one closing.
"""

import sys

sys.path.insert(0, "src")

from cse476.auth import (
    AUTH_MAP,
    AuditLog,
    Role,
    can_access,
    hash_password,
    is_weak_password,
    require_role,
    verify_password,
    why_all_three,
)

ok = True


def chk(label, cond):
    global ok
    print(f"  [{'pass' if cond else 'FAIL'}] {label}")
    ok = ok and cond


print("\n1. AUTHENTICATION: store a salted hash, never the password")
salt, stored = hash_password("correct-horse-battery")
chk("the stored value is not the password", stored != "correct-horse-battery")
chk("the right password verifies", verify_password("correct-horse-battery", salt, stored))
chk("a wrong password does not", not verify_password("123456", salt, stored))
s2, h2 = hash_password("correct-horse-battery")
chk("same password, different salt, different hash", h2 != stored)

print("\n2. weak passwords are rejected (the McHire authentication bug)")
chk("123456 is weak", is_weak_password("123456") is True)
chk("password is weak", is_weak_password("password") is True)
chk("too-short is weak", is_weak_password("abc12") is True)
chk("a strong one passes", is_weak_password("correct-horse-battery") is False)

print("\n3. AUTHORIZATION: you reach your own records, not everyone's (the IDOR)")
chk("alice reads her own record", can_access("alice", "alice") is True)
chk("alice CANNOT read bob's record", can_access("alice", "bob") is False)
chk("an admin can read any record", can_access("alice", "bob", role="admin") is True)

print("\n4. roles enforce least privilege")
viewer = Role(name="viewer", permissions=frozenset({"read"}))
recruiter = Role(name="recruiter", permissions=frozenset({"read", "contact"}))
chk("viewer may read", require_role(viewer, "read") is True)
chk("viewer may NOT contact", require_role(viewer, "contact") is False)
chk("recruiter may contact", require_role(recruiter, "contact") is True)
chk("nobody gets a permission they lack", require_role(viewer, "delete") is False)

print("\n5. AUDITING: an append-only trail of who did what")
log = AuditLog()
log.record("alice", "read", "record:alice", allowed=True)
log.record("alice", "read", "record:bob", allowed=False)   # an IDOR attempt
log.record("alice", "read", "record:carol", allowed=False)
chk("all attempts are recorded", len(log.entries) == 3)
chk("denied attempts are findable", len(log.denied()) == 2)
chk("the trail is queryable by user", len(log.by_user("alice")) == 3)
chk("a denied attempt names the target", log.denied()[0].target == "record:bob")

print("\n6. the mapping and framing are honest")
chk("authentication is proving who you are", "who you are" in AUTH_MAP["authentication"])
chk("authorization checks ownership and role", "what you may do" in AUTH_MAP["authorization"])
chk("IDOR is named", "IDOR" in AUTH_MAP["the McHire authorization bug"])
chk("append-only is explained", "not evidence" in AUTH_MAP["why append only"])
w = why_all_three()
chk("it is a chain", "break in any link" in w["the_chain"])
chk("authz is where least privilege lands", "least privilege" in w["least_privilege_link"])

print("\n" + ("ALL PASS" if ok else "SOMETHING FAILED"))
sys.exit(0 if ok else 1)
