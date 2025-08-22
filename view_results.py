#!/usr/bin/env python
"""
Quick viewer for AI news automation results
Usage: python view_results.py [latest|all|stats]
"""

import os
import sys
import json
import glob
from datetime import datetime

# Add project root to Python path for imports
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from scripts.utils import today_path


def get_latest_content_dir():
    """Get the most recent content directory"""
    content_dirs = glob.glob("content/*/*/*")
    if not content_dirs:
        return None

    # Sort by date (newest first)
    content_dirs.sort(reverse=True)
    return content_dirs[0]


def show_stats():
    """Show statistics about collected data"""
    print("📊 AI News Automation Statistics")
    print("=" * 50)

    # Latest data
    latest_data_dir = get_latest_content_dir()
    if latest_data_dir:
        date_str = latest_data_dir.replace("content/", "")
        print(f"📅 Latest run: {date_str}")

        # Check data files
        data_dir = latest_data_dir.replace("content/", "data/")
        if os.path.exists(data_dir):
            metadata_file = os.path.join(data_dir, "metadata.json")
            if os.path.exists(metadata_file):
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                print(f"📰 Articles collected: {metadata.get('count', 0)}")
                print(f"🔗 Sources: {', '.join(metadata.get('sources', []))}")
                print(f"⏰ Collected at: {metadata.get('collected_at', 'Unknown')}")

    # Count all content directories
    all_content_dirs = glob.glob("content/*/*/*")
    print(f"📁 Total runs: {len(all_content_dirs)}")

    # Show recent runs
    print("\n📋 Recent runs:")
    for i, dir_path in enumerate(sorted(all_content_dirs, reverse=True)[:5]):
        date_str = dir_path.replace("content/", "")
        print(f"  {i+1}. {date_str}")


def show_latest_content():
    """Show the latest generated content"""
    latest_dir = get_latest_content_dir()
    if not latest_dir:
        print("❌ No content found. Run the workflow first:")
        print("   python run.py collect")
        print("   python run.py process")
        return

    print(f"📰 Latest AI News Results ({latest_dir.replace('content/', '')})")
    print("=" * 60)

    # Show social media format
    social_file = os.path.join(latest_dir, "format_a_social.md")
    if os.path.exists(social_file):
        print("\n🔥 SOCIAL MEDIA FORMAT:")
        print("-" * 30)
        with open(social_file, "r", encoding="utf-8") as f:
            content = f.read()
            # Show first 5 articles
            lines = content.split("\n")
            for i, line in enumerate(lines[:15]):
                if line.strip():
                    print(line)
            if len(lines) > 15:
                print(f"... and {len(lines) - 15} more lines")

    # Show APA format
    apa_file = os.path.join(latest_dir, "format_b_apa.md")
    if os.path.exists(apa_file):
        print("\n📚 APA CITATION FORMAT (first 5):")
        print("-" * 30)
        with open(apa_file, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")
            for i, line in enumerate(lines[:10]):
                if line.strip():
                    print(line)

    print(f"\n📁 Full files available at: {latest_dir}/")
    print("   - format_a_social.md (Social media format)")
    print("   - format_b_apa.md (APA citation format)")
    print("   - format_c_design.txt (Design format)")


def show_all_content():
    """Show all available content directories"""
    content_dirs = glob.glob("content/*/*/*")
    if not content_dirs:
        print("❌ No content found. Run the workflow first.")
        return

    print("📁 All Available Results:")
    print("=" * 40)

    for i, dir_path in enumerate(sorted(content_dirs, reverse=True)):
        date_str = dir_path.replace("content/", "")
        files = os.listdir(dir_path)
        print(f"{i+1}. {date_str} ({len(files)} files)")

        # Show file sizes
        for file in files:
            file_path = os.path.join(dir_path, file)
            size = os.path.getsize(file_path)
            print(f"   📄 {file} ({size} bytes)")


def main():
    if len(sys.argv) < 2:
        print("Usage: python view_results.py [latest|all|stats]")
        print("\nOptions:")
        print("  latest  - Show latest generated content")
        print("  all     - Show all available content directories")
        print("  stats   - Show statistics")
        return

    command = sys.argv[1]

    if command == "latest":
        show_latest_content()
    elif command == "all":
        show_all_content()
    elif command == "stats":
        show_stats()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: latest, all, stats")


if __name__ == "__main__":
    main()
