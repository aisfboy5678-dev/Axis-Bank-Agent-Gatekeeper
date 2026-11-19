import os
import shutil
import zipfile
import glob

def package_submission():
    desktop_dir = "/Users/asifansari/Desktop"
    workspace_dir = "/Users/asifansari/Downloads/Axis-Agent-Gatekeeper "
    staging_dir = os.path.join(desktop_dir, "63936_AgentGate")
    zip_path = os.path.join(desktop_dir, "63936_AgentGate.zip")

    print(f"1. Preparing staging directory: {staging_dir}")
    if os.path.exists(staging_dir):
        shutil.rmtree(staging_dir)
    if os.path.exists(zip_path):
        os.remove(zip_path)

    os.makedirs(staging_dir, exist_ok=True)

    # 1. Top-level files
    pdf_report = os.path.join(workspace_dir, "Axis_Bank_Agent_Gatekeeper_Report.pdf")
    prompts_doc = os.path.join(workspace_dir, "PROMPTS.md")
    
    shutil.copy2(pdf_report, os.path.join(staging_dir, "Axis_Bank_Agent_Gatekeeper_Report.pdf"))
    shutil.copy2(prompts_doc, os.path.join(staging_dir, "PROMPTS.md"))
    print("   Copied Axis_Bank_Agent_Gatekeeper_Report.pdf and PROMPTS.md to top level.")

    # 2. Demo Video from Desktop
    video_matches = (
        glob.glob(os.path.join(desktop_dir, "Screen Recording 2026-11-20*.mov")) +
        glob.glob(os.path.join(desktop_dir, "Screen Recording 2026-11-20*.mp4")) +
        glob.glob(os.path.join(desktop_dir, "*.mov")) +
        glob.glob(os.path.join(desktop_dir, "*.mp4"))
    )
    if video_matches:
        latest_video = max(video_matches, key=os.path.getmtime)
        ext = os.path.splitext(latest_video)[1]
        dest_video = os.path.join(staging_dir, f"Demo_Video{ext}")
        shutil.copy2(latest_video, dest_video)
        print(f"   Copied video: {os.path.basename(latest_video)} -> Demo_Video{ext} ({os.path.getsize(dest_video)/(1024*1024):.2f} MB)")
    else:
        print("   WARNING: No .mov or .mp4 found on Desktop.")

    # 3. Screenshots subfolder
    screenshots_dir = os.path.join(staging_dir, "Screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)
    screenshot_patterns = [
        os.path.join(desktop_dir, "Screenshot 2026-11-18*"),
        os.path.join(desktop_dir, "Screenshot 2026-11-19*"),
        os.path.join(desktop_dir, "Screenshot 2026-11-20*"),
    ]
    copied_count = 0
    for pat in screenshot_patterns:
        for f in sorted(glob.glob(pat)):
            shutil.copy2(f, screenshots_dir)
            copied_count += 1
            print(f"   Copied screenshot: {os.path.basename(f)}")
    print(f"   Total {copied_count} screenshots copied into Screenshots/.")

    # 4. Complete project folder
    proj_dest = os.path.join(staging_dir, "Axis-Agent-Gatekeeper")
    os.makedirs(proj_dest, exist_ok=True)

    proj_files = [
        "app.py",
        "requirements.txt",
        "PROMPTS.md",
        "README.md",
        "generate_pdf_report.py",
        "test_gatekeeper.py",
        "Axis_Bank_Agent_Gatekeeper_Report.pdf",
        ".gitignore"
    ]
    for pf in proj_files:
        src_f = os.path.join(workspace_dir, pf)
        if os.path.exists(src_f):
            shutil.copy2(src_f, proj_dest)

    data_src = os.path.join(workspace_dir, "data")
    data_dest = os.path.join(proj_dest, "data")
    if os.path.exists(data_src):
        shutil.copytree(data_src, data_dest, dirs_exist_ok=True)

    print("   Project folder staged successfully (excluding .git and .venv).")

    # 5. Compress into ZIP
    print(f"\n2. Creating ZIP archive: {zip_path}")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(staging_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            for file in files:
                if file.startswith('.') and file != '.gitignore':
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(staging_dir))
                zipf.write(file_path, arcname)

    zip_size = os.path.getsize(zip_path)
    print(f"\n✅ ZIP file created successfully!")
    print(f"   Path: {zip_path}")
    print(f"   Size: {zip_size / (1024*1024):.2f} MB ({zip_size:,} bytes)")

    # 6. List all contents of ZIP
    print("\n3. Contents of 63936_AgentGate.zip:")
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        for info in zipf.infolist():
            size_kb = info.file_size / 1024
            print(f"   {info.filename:<65} {size_kb:>8.1f} KB")

if __name__ == "__main__":
    package_submission()
