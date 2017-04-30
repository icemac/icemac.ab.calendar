import icemac.addressbook.generations.utils


@icemac.addressbook.generations.utils.evolve_addressbooks
def evolve(addressbook):
    """Set permissions on users again to allow them to edit themselves."""
    for principal in addressbook.principals.values():
        # Side effect: set entries in permission map to allow user to edit his
        # own data.
        principal.roles = principal.roles
