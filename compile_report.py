#!/usr/bin/env python
import subprocess
import os

os.chdir(r"D:\Imran\METU\Coursework\CE4011\Assignment3")
result = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], 
                       capture_output=True, text=True)
print("Return code:", result.returncode)
if "Output written" in result.stdout:
    print("✓ PDF successfully generated")
elif "Error" in result.stdout or result.returncode != 0:
    print("✗ Compilation errors detected")
    print(result.stdout[-1000:] if len(result.stdout) > 1000 else result.stdout)
else:
    print("Compilation completed")
    
# Check PDF file size
pdf_size = os.path.getsize("main.pdf")
print(f"PDF size: {pdf_size:,} bytes")
