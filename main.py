import subprocess
import sys
import os
import argparse
import time

def run_test(executable, input_file: str, expected_output_file: str, name: str, lang: str = "python", show_failed_output: bool = False) -> bool:
    isCorr = False
    with open(expected_output_file, 'r') as f:
        expected_output = f.read().strip()

    with open(input_file, 'r') as infile:
        start_time = time.time()
        if lang == "java":
            result = subprocess.run(['java', executable], stdin=infile, capture_output=True, text=True)
        elif lang == "python":
            result = subprocess.run([sys.executable, executable], stdin=infile, capture_output=True, text=True)
        else:
            result = subprocess.run([executable], stdin=infile, capture_output=True, text=True)
        end_time = time.time()

    actual_output = result.stdout.strip()
    duration = end_time - start_time
    print(f"{name} -", end=" ")
    if actual_output == expected_output:
        print(f"Test Passed! Time: {duration:.4f}s")
        isCorr = True
    else:
        print(f"Test Failed! Time: {duration:.4f}s")
        if show_failed_output:
            print(f"\nExpected Output:\n{expected_output}\n")
            print(f"Actual Output:\n{actual_output}\n")
    print("-------")
    return isCorr

def compile_cpp(source_file: str) -> str:
    executable = "./" + os.path.splitext(os.path.basename(source_file))[0]
    compilation = subprocess.run(["g++", source_file, "-o", executable], capture_output=True)
    if compilation.returncode != 0:
        print(f"Compilation failed for {source_file}:")
        print(compilation.stderr.decode())
        sys.exit(1)
    return executable

def compile_c(source_file: str) -> str:
    executable = "./" + os.path.splitext(os.path.basename(source_file))[0]
    compilation = subprocess.run(["gcc", source_file, "-o", executable], capture_output=True)
    if compilation.returncode != 0:
        print(f"Compilation failed for {source_file}:")
        print(compilation.stderr.decode())
        sys.exit(1)
    return executable

def compile_java(source_file: str) -> str:
    class_file = os.path.splitext(os.path.basename(source_file))[0]
    compilation = subprocess.run(["javac", source_file], capture_output=True)
    if compilation.returncode != 0:
        print(f"Compilation failed for {source_file}:")
        print(compilation.stderr.decode())
        sys.exit(1)
    return class_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run tests on scripts for BRUTE with public input/output file pairs.")
    parser.add_argument('script_path', help="Path to the script or source file to be tested (Python, C, C++, or Java).")
    parser.add_argument('directory_path', help="Directory containing input and expected output files.")
    parser.add_argument('-f', action='store_true', help="Flag to show detailed output for failed tests (expected vs actual).")
    
    args = parser.parse_args()
    
    script_path = args.script_path
    dir_path = args.directory_path
    show_failed_output = args.f  

    dir_files = sorted([(dir_path + "/" + name) for name in os.listdir(dir_path)])

    _, ext = os.path.splitext(script_path)
    
    if ext == ".py":
        executable = script_path
        lang = "python"
    elif ext == ".cpp":
        executable = compile_cpp(script_path)
        lang = "cpp"
    elif ext == ".c":
        executable = compile_c(script_path)
        lang = "c"
    elif ext == ".java":
        executable = compile_java(script_path)
        lang = "java"
    else:
        print(f"Unsupported script type: {ext}")
        sys.exit(1)

    count_corr = 0
    count_files = len(dir_files) // 2
    
    if count_files == 0:
        print("No test cases found.")
        sys.exit(0)

    for i in range(0, len(dir_files), 2):
        input_file = dir_files[i]
        expected_output_file = dir_files[i + 1]
        if run_test(executable, input_file, expected_output_file, os.path.basename(input_file), lang=lang, show_failed_output=show_failed_output):
            count_corr += 1
    
    print(f"Passed {count_corr} out of {count_files} - {round((count_corr / count_files) * 100, 1)}%")

    if lang in ["cpp", "c"] and os.path.exists(executable):
        os.remove(executable)
    elif lang == "java":
        class_file = executable + ".class"
        if os.path.exists(class_file):
            os.remove(class_file)
