import sys
import json
from git import Repo


def generate_manifest(output_filename):
    repo = Repo(".")
    manifest = {
        "source": {
            "commit_hash": repo.head.object.hexsha,
            "commit_message": repo.head.object.message.strip("\n"),
            "committer": {
                "name": repo.head.object.committer.name,
                "email": repo.head.object.committer.email,
            },
            "committed_at": repo.head.object.committed_datetime.isoformat(),
            "author": {
                "name": repo.head.object.author.name,
                "email": repo.head.object.author.email,
            },
            "authored_at": repo.head.object.authored_datetime.isoformat(),
        }
    }
    with open(output_filename, "w") as f:
        json.dump(manifest, f, indent=4)


def main():
    # assert correct number of arguments.
    if len(sys.argv) > 2:
        raise RuntimeError(f"Too many arguments provided to create_manifest.py")

    if len(sys.argv) == 1:
        print(f"Output directory is required.")
        sys.exit(1)

    output_directory = sys.argv[1]

    generate_manifest(f"{output_directory}/manifest.json")


if __name__ == "__main__":
    main()
