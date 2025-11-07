import json
import shutil
from codebase_genius import RepoMapper

# Use a small, public test repository
TEST_REPO = "https://github.com/github/gitignore.git"

if __name__ == "__main__":
    mapper = RepoMapper()
    mapping_result = mapper.map_repository(TEST_REPO)

    print("\n--- Repo Mapping Result ---")
    print(json.dumps(mapping_result, indent=2))

    # Clean up the cloned directory after inspection
    if mapping_result.get("status") == "success":
        shutil.rmtree(mapping_result["local_path"])
        print(f"\nCleaned up {mapping_result['local_path']}")
