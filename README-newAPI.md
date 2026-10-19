# make new API work

This file describes the "modules" to check/migrate to the new API.

Before only unittests were used to check the API.
Now the modules are used to check/migrate the real current Artifactory-API.
The tests have the part `real` in the name of the test class, 
e.g. `TestUsersReal` or `TestGroupsReal`.

Users, Groups, Repositories (incl. Replication) and Permissions are needed to migrate the Artifactory to the new instance.

## modules to migrate/check

- AQL
- Artifact
- Overwork Replication tests - because they do not use the defined test objects.

## modules working with new/current API

- Users (with: 7.77.7)
- Groups (with: 7.77.7)
- Repositories (with: 7.77.7)
- Repository Replication (with: 7.77.7)
- Permissions (with: 7.77.7)