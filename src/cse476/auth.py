"""
Authentication, authorization, and auditing: who are you, what may you do, prove it.

Unit 6 Lecture 3. Lecture 2 ended on least privilege: an agent should only be able
to do what its job needs. That immediately raises a question it could not answer:
who is asking, and how does the system know. Least privilege is meaningless if
anyone can claim to be anyone. This lecture supplies the missing machinery.

Three questions, and every secure system has to answer all three. Picture a
building with a guard and keycards:

    Authentication   the guard checks your ID at the door.  Who are you?
    Authorization    your keycard opens only certain rooms. What may you do?
    Auditing         every swipe is written to a log.       What happened, provably?

McDonald's McHire, from last lecture, failed the first two at once, which is why
64 million applicants were exposed. The recruiter login accepted the password
123456 (authentication: anyone could get in), and once in, changing an id number
in the address let you read any applicant's record (authorization: the system
never checked that the record was yours). Neither failure is exotic. Both are a
missing line of the code below.

    Authentication
    hash_password / verify_password   store a salted hash, never the password
    is_weak_password                  reject the 123456 class of passwords
    Authorization
    can_access                        you reach your own records, not everyone's
    Role / require_role               least privilege as enforced roles
    Auditing
    AuditLog / AuditEntry             append only: who, what, when, allowed or not
    AUTH_MAP                          the ideas, named
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass, field

# ---------------------------------------------------------------- authentication

def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    """
    Turn a password into a salted hash. Returns (salt, hash_hex).

    The salt is random per password, so identical passwords hash differently and a
    precomputed lookup table is useless. The hash is deliberately slow (many
    iterations), so guessing at scale is expensive. You store the salt and the
    hash. You never store the password itself, because you never need to: to check
    a login you hash the attempt the same way and compare.
    """
    salt = salt or secrets.token_hex(8)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return salt, digest.hex()


def verify_password(password: str, salt: str, expected_hex: str) -> bool:
    """
    Check a password attempt against the stored salt and hash.

    Hash the attempt with the stored salt, then compare in constant time.
    Constant-time comparison matters: a normal string compare returns faster when
    the first characters differ, and an attacker can measure that timing to guess
    the hash character by character. hmac.compare_digest closes that leak.
    """
    _, got = hash_password(password, salt)
    return hmac.compare_digest(got, expected_hex)


_COMMON_PASSWORDS = frozenset(
    {"123456", "password", "12345678", "qwerty", "111111", "123456789", "admin"}
)


def is_weak_password(password: str) -> bool:
    """
    Reject the class of password McHire accepted. True means unacceptable.

    A password is weak if it is too short or is one of the well-known common ones.
    McHire's recruiter account used 123456, which this refuses outright. This is
    the cheapest, highest-value check in authentication, and it was the whole
    difference between a private system and 64 million exposed records.
    """
    if len(password) < 8:
        return True
    return password.lower() in _COMMON_PASSWORDS


# ---------------------------------------------------------------- authorization

def can_access(user_id: str, record_owner_id: str, role: str = "user") -> bool:
    """
    Decide whether a user may reach a specific record. The check McHire skipped.

    A normal user may reach only records they own. An admin may reach any. The
    McHire flaw was that any logged-in user could read any applicant's record just
    by changing the id in the request, because this ownership check did not exist.
    That vulnerability has a name, IDOR, insecure direct object reference, and it
    is one of the most common access-control failures in real systems.
    """
    if role == "admin":
        return True
    return user_id == record_owner_id


@dataclass(frozen=True)
class Role:
    """
    A named role carrying a set of permissions. Least privilege, made enforceable.

    Lecture 2's least privilege said grant the minimum. A role is how you say that
    concretely: a 'viewer' role holds only read, a 'recruiter' holds read and
    contact, an 'admin' holds all of it. You assign a person the smallest role that
    lets them do their job, and the system enforces it, rather than trusting
    everyone to stay in their lane.
    """

    name: str
    permissions: frozenset[str]

    def allows(self, permission: str) -> bool:
        return permission in self.permissions


def require_role(role: Role, permission: str) -> bool:
    """Gate an action on a role holding the needed permission."""
    return role.allows(permission)


# ---------------------------------------------------------------- auditing

@dataclass(frozen=True)
class AuditEntry:
    """One line of the trail: who did what to what, when, and was it allowed."""

    who: str
    action: str
    target: str
    allowed: bool
    when: str = "2026-01-01T00:00:00Z"  # fixed for deterministic tests


@dataclass
class AuditLog:
    """
    An append-only record of access decisions. Compliance and auditing, in code.

    You record both the allowed and the denied attempts, because the denied ones
    are often the more interesting: a burst of denied accesses to other people's
    records is exactly the signature of an IDOR attack in progress. Compliance
    frameworks require this trail so that, after an incident, you can answer who
    saw what and when. A system that cannot answer that has no accountability.
    """

    entries: list[AuditEntry] = field(default_factory=list)

    def record(self, who: str, action: str, target: str, allowed: bool) -> None:
        self.entries.append(AuditEntry(who=who, action=action, target=target, allowed=allowed))

    def denied(self) -> list[AuditEntry]:
        """The denied attempts, where an attack in progress shows up first."""
        return [e for e in self.entries if not e.allowed]

    def by_user(self, who: str) -> list[AuditEntry]:
        """Everything one identity did, the question an auditor asks first."""
        return [e for e in self.entries if e.who == who]


# ---------------------------------------------------------------- the mapping

AUTH_MAP: dict[str, str] = {
    "authentication": "proving who you are; store a salted hash, never the password",
    "authorization": "deciding what you may do; check ownership and role every time",
    "auditing": "an append-only record of who did what, so it can be proven later",
    "the McHire authentication bug": "the password 123456 was accepted, so anyone got in",
    "the McHire authorization bug": "any logged-in user could read any record by changing an id (IDOR)",
    "least privilege, enforced": "roles carry the minimum permissions, and the system checks them",
    "why append only": "a log an attacker can edit is not evidence; it must be tamper resistant",
}


def why_all_three() -> dict[str, str]:
    """
    Why you need all three, and how McHire proves it, for the exam.

    The three are a chain, and a break anywhere fails the whole system. Strong
    authorization is useless if authentication lets anyone in as anyone. Perfect
    authentication is useless if, once in, you can reach everything. And both are
    useless for accountability without an audit trail to reconstruct what
    happened. McHire had a weak first link and a missing second, so the third,
    even if present, could only record the disaster, not prevent it.
    """
    return {
        "authentication": "who are you; McHire accepted 123456, so this link broke",
        "authorization": "what may you do; McHire never checked record ownership (IDOR)",
        "auditing": "what happened; the trail proves it after the fact but cannot prevent it",
        "the_chain": "a break in any link fails the system; you need all three",
        "least_privilege_link": "authorization is where Lecture 2's least privilege gets enforced",
    }
