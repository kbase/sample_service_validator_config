# Automation Scripts

These scripts are meant to be executed by GHA workflows. They all call complementary Python scripts. These Python scripts may be found in the sister directories `export` and `validate`.

As such, they may encode certain values which are otherwise parameters to the upstream Python scripts. After all, part of the reason for automation is to standardize these parameters.

If at some point in the future these scripts themselves need parameterization (e.g. through environment variables set in the GHA workflow), we can make the adjustments here.
