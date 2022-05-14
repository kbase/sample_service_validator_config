import sys
import json
import pygit2
import datetime

def generate_manifest(output_filename):
    repo = pygit2.Repository('.')
    commit = repo.revparse_single('HEAD')
    committer_time = datetime.datetime.fromtimestamp(commit.committer.time) + datetime.timedelta(minutes=commit.committer.offset)
    author_time = datetime.datetime.fromtimestamp(commit.author.time) + datetime.timedelta(minutes=commit.author.offset)
    manifest = {
        "git": {
            "commit_hash": commit.hex,
            "commit_message": commit.message.strip("\n"),
            "committer": {
                "name": commit.committer.name,
                "email": commit.committer.email,
            },
            "committed_at": committer_time.isoformat(),
            "author": {
                "name": commit.author.name,
                "email": commit.author.email,
            },
            "authored_at": author_time.isoformat(),
        },
        "files": {
            "groups.json": None,
            "manifest.json": None,
            "metadata_validation.yml": None,
            "ontology_validators.yml": None,
            "pint_unit_definitions.txt": None,
            "README.md": None,
            "sample_fields.html": None,
            "sample_uploader_mappings.yml": None,
            "schemas.json": None,
            "templates": {
                "enigma_template.yml": None,
                "sesar_template.yml": None
            }
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
