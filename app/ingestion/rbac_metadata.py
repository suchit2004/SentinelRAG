from enum import IntEnum

class Role(IntEnum):
    EMPLOYEE = 1
    EXECUTIVE = 2
    ADMIN = 3

    @classmethod
    def from_str(cls, role_str: str) -> "Role":
        try:
            return cls[role_str.upper()]
        except KeyError:
            return cls.EMPLOYEE

# Map source PDF filenames to their minimum required roles
DOCUMENT_ROLE_MAPPING = {
    "financial_report.pdf": Role.EXECUTIVE,
    "IPO-IndustryReport.pdf": Role.EMPLOYEE
}

def get_required_role_for_doc(filename: str) -> Role:
    """
    Returns the Role required to access a document based on its filename.
    Defaults to Role.ADMIN for unrecognized/new documents to be secure.
    """
    # Extract basename in case a path is passed
    import os
    basename = os.path.basename(filename)
    return DOCUMENT_ROLE_MAPPING.get(basename, Role.ADMIN)

def has_access(user_role: Role, required_role: Role) -> bool:
    """
    Returns True if user_role has access to the required_role.
    """
    return user_role >= required_role
