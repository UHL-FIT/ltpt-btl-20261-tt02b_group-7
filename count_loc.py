import os

def count_loc(root_dir):
    total_lines = 0
    total_code_lines = 0
    # Bỏ qua các thư mục không chứa source code nghiệp vụ
    exclude_dirs = {'.venv', 'tests', '__pycache__', 'dist', 'build', '.git'}
    
    print(f"{'File Path':<45} | {'Total Lines':<15} | {'Code Lines':<20}")
    print("-" * 85)
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Lọc bỏ các thư mục không cần thiết
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        
        for file in filenames:
            if file.endswith('.py'):
                # Chỉ tính các file python
                filepath = os.path.join(dirpath, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        lines_count = len(lines)
                        
                        # Tính dòng code thực tế (Bỏ qua dòng trống và dòng comment)
                        code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
                        
                        total_lines += lines_count
                        total_code_lines += code_lines
                        
                        rel_path = os.path.relpath(filepath, root_dir)
                        print(f"{rel_path:<45} | {lines_count:<10} | {code_lines:<20}")
                except Exception as e:
                    pass
                    
    print("-" * 85)
    print(f"{'TOTAL':<45} | {total_lines:<15} | {total_code_lines:<20}")

if __name__ == '__main__':
    # Lấy thư mục gốc của project
    root = os.path.dirname(os.path.abspath(__file__))
    count_loc(root)
