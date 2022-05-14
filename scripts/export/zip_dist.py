import pathlib
import zipfile
import sys

def usage(error_message=None):
    print("zip_dist.py source_dir dest_file")
    print("  source_dir is the directory to archive")
    print("  dest_file is the path and name of the file for the resulting archive file")
    if error_message is not None:
        print(f"ERROR: {error_message}")

def zip_dist(source_dir, dest_file):
    # print(f"WILL zip it: {source_dir}, {dest_dir}")
    dir = pathlib.Path(source_dir)
    with zipfile.ZipFile(dest_file, mode="w") as archive:
        for file_path in dir.rglob("*"):
            archive.write(
                file_path,
                arcname=file_path.relative_to(dir)
            )

def main():
    # assert correct number of arguments.
    if len(sys.argv) > 3:
        usage("Too many arguments")
        sys.exit(1)

    if len(sys.argv) < 3:
        usage("Not enough arguments")
        sys.exit(1)

    source_directory = sys.argv[1]
    dest_file = sys.argv[2]

    zip_dist(source_directory, dest_file)


if __name__ == "__main__":
    main()
