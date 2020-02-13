# Run Job Cleanup

Run jobs currently just kind of hang around forever.  Use this to clean them up.

Update the `deploy/deployment.yml` and `deploy/rbac.yml` with the namespace where you are deploying your run jobs (may be `spinnaker`), and then create the resources.