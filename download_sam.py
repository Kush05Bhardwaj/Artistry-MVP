# download_sam.py
"""
Download SAM (Segment Anything Model) checkpoint without running the pipeline.
"""

import os
import urllib.request
from pathlib import Path

# SAM model download URL
SAM_MODEL_URL = "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "sam_vit_b_01ec64.pth")

def download_sam_model():
    """Download SAM ViT-B model checkpoint."""
    
    # Create models directory if it doesn't exist
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # Check if model already exists
    if os.path.exists(MODEL_PATH):
        file_size = os.path.getsize(MODEL_PATH) / (1024 * 1024)  # MB
        print(f"✅ SAM model already exists: {MODEL_PATH}")
        print(f"   Size: {file_size:.1f} MB")
        return
    
    print(f"📥 Downloading SAM model...")
    print(f"   URL: {SAM_MODEL_URL}")
    print(f"   Destination: {MODEL_PATH}")
    print(f"   Size: ~375 MB (this may take a few minutes)\n")
    
    def progress_hook(count, block_size, total_size):
        """Show download progress."""
        downloaded = count * block_size
        percent = min(100, int(downloaded * 100 / total_size))
        downloaded_mb = downloaded / (1024 * 1024)
        total_mb = total_size / (1024 * 1024)
        
        # Progress bar
        bar_length = 50
        filled = int(bar_length * percent / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        print(f"\r[{bar}] {percent}% ({downloaded_mb:.1f}/{total_mb:.1f} MB)", end='', flush=True)
    
    try:
        urllib.request.urlretrieve(SAM_MODEL_URL, MODEL_PATH, progress_hook)
        print("\n\n✅ Download complete!")
        print(f"   Model saved to: {MODEL_PATH}")
        
        # Verify file size
        file_size = os.path.getsize(MODEL_PATH) / (1024 * 1024)
        print(f"   File size: {file_size:.1f} MB")
        
        if file_size < 300:
            print("\n⚠️  Warning: File size seems smaller than expected.")
            print("   The download may have failed. Please try again.")
        else:
            print("\n🎉 SAM model ready to use!")
            
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        print("\nAlternative: Download manually from:")
        print(f"   {SAM_MODEL_URL}")
        print(f"   Save to: {MODEL_PATH}")

if __name__ == "__main__":
    print("="*60)
    print("SAM (Segment Anything Model) Downloader")
    print("="*60 + "\n")
    
    download_sam_model()
    
    print("\n" + "="*60)
    print("Next steps:")
    print("  1. Run: python main_pipeline.py")
    print("  2. The pipeline will use the downloaded SAM model")
    print("="*60)
