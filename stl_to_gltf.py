import glob
import os

def get_stl_files(current_dir):
      stl_files = glob.glob(os.path.join(current_dir, "*.stl"))
      return stl_files

if __name__ == "__main__":
      current__directory = os.path.dirname(os.path.abspath(__file__))
      print(get_stl_files(current__directory))
