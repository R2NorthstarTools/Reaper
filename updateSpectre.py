import os
import shutil
from git.repo.base import Repo

# I just didn't want to type this out over and over again
cwd = os.getcwd()

# Check that we're actually in the Spectre directory
if os.path.isfile("Spectre.py") == True:
    # Check that data exists. This could still error out if you don't have one of the other two, but if you don't, what are you doing
    if os.path.exists("data") and os.path.isfile(".env") == True:
        whatUpdate = input(
            "Update moves your current data to a new clone of the up to date Spectre repo, test clones a repo and moves your data to that folder, and restore can be used inside a cloned repo to move data back to the original Spectre folder. What would you like to do? [update]/[test]/[restore] "
        )
        if whatUpdate.lower() == "update":

            warning = input(
                "Warning! Running this command updates Spectre, which will remove any local code changes you have! Do you wish to continue? [y]/[n] "
            )

            if warning.lower() == "y":
                # Move to the parent directory (to create the new directory and later delete the old ones)
                os.chdir("../")
                os.rename("Spectre", "SpectreOld")
                os.mkdir("Spectre")

                # Clone the newest GitHub repo version
                Repo.clone_from("https://github.com/itscynxx/Spectre", "Spectre")

                # Remove the "new" config file. There might be a better way to do this, but this works
                os.remove("Spectre/config.json")

                # Move the old data files from the temporary folder into the new Spectre folder
                shutil.move("SpectreOld/data", "Spectre/data")
                shutil.move("SpectreOld/.env", "Spectre")
                shutil.move("SpectreOld/config.json", "Spectre")

                # Print that the system hasn't imploded yet
                print("Moved Spectre's data files succesfully!")
                print("Deleting old Spectre files...")

                # Remove temporary folders
                shutil.rmtree("SpectreOld")

            elif warning.lower() == "n":
                print("Stopping update...")

            else:
                print("Unrecognized input given, stopping update...")

        if whatUpdate.lower() == "test":

            whatRepo = input(
                "Please paste the url of the branch or repo you want to test. "
            )
            # Make sure the link has Spectre in the name
            if "Spectre" in whatRepo:
                # If tree is in the name, auto clone
                if "tree" in whatRepo:
                    print("Branch url found! Automatically cloning the branch url...")
                    # Split on tree, so we get the base url
                    gitUrl = whatRepo.split("/tree")[0]
                    # Split after tree, so we get the branch
                    gitBranch = whatRepo.split("tree/")[1]

                # If tree isn't in the name, manually input branch name
                else:
                    # We already have the url in this case
                    gitUrl = whatRepo
                    # Just getting the branch we need
                    manualBranch = input(
                        "Base repo found! Please enter the name of the branch you'd like to clone (leave blank for main) "
                    )
                    if manualBranch is not None:
                        # Setting the common variable to the manually inputted one
                        gitBranch = manualBranch
                    else:
                        # Fallback to main
                        gitBranch = "main"
                os.chdir("../")
                # Clone from given url, given branch, and put the repo clone and data into a folder matching the branch name
                Repo.clone_from(
                    url=gitUrl, branch=gitBranch, to_path=f"Spectre-Branch_{gitBranch}"
                )
                os.remove(f"Spectre-Branch_{gitBranch}/config.json")
                shutil.move("Spectre/data", f"Spectre-Branch_{gitBranch}/data")
                shutil.move("Spectre/.env", f"Spectre-Branch_{gitBranch}")
                shutil.move("Spectre/config.json", f"Spectre-Branch_{gitBranch}")

            else:
                print("Clone a valid Spectre repo :P")

        if whatUpdate.lower() == "restore":
            # Make sure we're in a cloned repo
            if "Spectre-Branch_" in cwd:
                # Make sure we have data
                if os.path.isfile(".env") and os.path.exists("data") == True:
                    # Make sure we have a Spectre path to put stuff into
                    if os.path.exists("../Spectre"):
                        print("Restoring original Spectre data...")
                        shutil.move(f"{cwd}/data", "../Spectre/data")
                        shutil.move(f"{cwd}/.env", "../Spectre")
                        shutil.move(f"{cwd}/config.json", "../Spectre")
                        removeData = input(
                            "Finished moving data files! Would you like to delete the cloned repo's files? [y]/[n] "
                        )
                        if removeData.lower() == "y":
                            print("Removing cloned repo's files...")
                            shutil.rmtree(cwd)
                        else:
                            print("Keeping cloned repo's files...")
                    else:
                        print(f"No original Spectre folder found in {cwd('../')}")
            else:
                print('Run "Restore" in a cloned testing repo!')
    else:
        print("Run the file inside the Spectre directory that has your data!")
else:
    print("Run the file inside the Spectre directory!")
