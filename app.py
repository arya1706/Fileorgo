from flask import Flask, render_template, request, jsonify
import os
import shutil
from flask_cors import CORS
import datetime
import logging
import pathlib

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(filename='file_organizer.log', level=logging.INFO)

SORTED_FOLDER = "sorted_files"
os.makedirs(SORTED_FOLDER, exist_ok=True)

# Enhanced file type categories with more extensions
FILE_TYPES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg", ".ico"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".3gp"],
    "Documents": [".pdf", ".docx", ".txt", ".pptx", ".xlsx", ".doc", ".ppt", ".xls", ".rtf", ".odt", ".csv"],
    "Music": [".mp3", ".wav", ".aac", ".flac", ".m4a", ".wma", ".ogg", ".mid", ".midi"],
    "Compressed": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
    "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".php", ".rb", ".go", ".swift"],
    "Executables": [".exe", ".msi", ".app", ".dmg", ".sh", ".bat"],
    "Others": []
}

def get_file_size(size):
    """Get file size in human-readable format"""
    size_bytes = size
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"
def organize_files(folder_path):
    folder_path = os.path.normpath(folder_path)
    print(folder_path)

    if not os.path.exists(folder_path):
        return {"error": "Folder path does not exist"}
    
    try:
        # Statistics dictionary
        stats = {
            "total_files": 0,
            "organized_files": 0,
            "total_size": 0,
            "categories": {},
            "start_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Create category folders
        for category in FILE_TYPES.keys():
            category_path = os.path.join(folder_path, category)
            os.makedirs(category_path, exist_ok=True)
            stats["categories"][category] = {"count": 0, "size": 0}

        # Sort files
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            
            if os.path.isdir(file_path) or not os.path.isfile(file_path):
                continue
                
            stats["total_files"] += 1
            file_size = os.path.getsize(file_path)
            stats["total_size"] += file_size
            
            file_ext = os.path.splitext(filename)[1].lower()
            moved = False
            
            for category, extensions in FILE_TYPES.items():
                if file_ext in extensions:
                    destination = os.path.join(folder_path, category, filename)
                    # Handle duplicate filenames
                    if os.path.exists(destination):
                        base, ext = os.path.splitext(filename)
                        counter = 1
                        while os.path.exists(destination):
                            new_filename = f"{base}_{counter}{ext}"
                            destination = os.path.join(folder_path, category, new_filename)
                            counter += 1
                    
                    shutil.move(file_path, destination)
                    # Update stats after the move
                    stats["categories"][category]["count"] += 1
                    stats["categories"][category]["size"] += file_size
                    stats["organized_files"] += 1
                    print(f"{file_path} -> {destination}")
                    moved = True
                    break
            
            if not moved:
                destination = os.path.join(folder_path, "Others", filename)
                if os.path.exists(destination):
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(destination):
                        new_filename = f"{base}_{counter}{ext}"
                        destination = os.path.join(folder_path, "Others", new_filename)
                        counter += 1
                shutil.move(file_path, destination)
                # Update stats for "Others" after the move
                stats["categories"]["Others"]["count"] += 1
                stats["categories"]["Others"]["size"] += file_size
                stats["organized_files"] += 1
        print(stats)
        # Convert sizes to human-readable format
        stats["total_size"] = get_file_size(stats["total_size"])
        print(stats["total_size"])
        for category in stats["categories"]:
            print("This works")
            stats["categories"][category]["size"] = get_file_size(stats["categories"][category]["size"])
            print("this too")

        # Log the organization activity
        logging.info(f"Organized {stats['organized_files']} files in {folder_path}")
                
        return {
            "success": "Files organized successfully",
            "stats": stats
        }
    except Exception as e:
        logging.error(f"Error organizing files: {str(e)}")
        return {"error": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/organize', methods=['POST', 'OPTIONS'])
def organize():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"})
        
    data = request.get_json()
    
    if not data or 'folderPath' not in data:
        return jsonify({"error": "No folder path provided"}), 400
        
    folder_path = data['folderPath']
    result = organize_files(folder_path)
    
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
