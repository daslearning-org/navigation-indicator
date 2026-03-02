# replace_manifest.py
import os
import shutil

def before_apk_assemble(build):
    # Path to the generated manifest in the build directory
    build_dir = "/home/somnath/codes/git/my-org/navigation-indicator/app/.buildozer/android/platform/build-arm64-v8a/dists/navindi"
    # Adjust the dist name if needed (check your actual build dir)
    generated_manifest_main = os.path.join(build_dir, "src/main/AndroidManifest.xml")
    generated_manifest = os.path.join(build_dir, "AndroidManifest.xml")
    custom_manifest = "/home/somnath/codes/git/my-org/navigation-indicator/app/hookers/xml_full.xml"

    if os.path.exists(custom_manifest):
        print("Replacing AndroidManifest.xml with custom version")
        shutil.copyfile(custom_manifest, generated_manifest)
        shutil.copyfile(custom_manifest, generated_manifest_main)
        print("Manifest replacement executed!")
    else:
        print("Custom manifest not found!")