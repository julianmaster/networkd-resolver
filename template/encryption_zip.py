import os
import py_compile
import shutil
import sys
import zipfile
from io import BytesIO

BUILD_FOLDER = "../Build"


class ZipUtilities:

    def __init__(self, file, mode, compression, substitution=[]):
        self.zip_file = zipfile.PyZipFile(file, mode, compression, False)
        self.substitution = substitution

    def add_file(self, source_file, destination_file=None, run_substitution=True):
        # Check source file extension
        source_root, source_ext = os.path.splitext(source_file)
        source_basename = os.path.basename(source_file)
        if source_ext != ".py" and source_ext != ".pyc":
            raise RuntimeError('Files source must end with ".py" or ".pyc"')

        # Check destination file extension
        if destination_file and source_file != destination_file:
            destination_root, destination_ext = os.path.splitext(destination_file)
            if destination_ext != ".pyc":
                raise RuntimeError('Files destination must end with ".pyc"')
        else:
            destination_file = source_root + ".pyc"

        # Prepare temp file with substitution words
        if source_ext == ".py":
            temp_text = open(source_file).read()
            # Substitution
            if run_substitution:
                for source_text, destination_text in self.substitution:
                    temp_text = temp_text.replace("import " + source_text, "import " + destination_text)
                    if "from " + source_text in temp_text:
                        temp_text = temp_text.replace("from " + source_text, "from " + destination_text)
                    else:
                        temp_text = temp_text.replace(source_text, destination_text)

            with open(os.path.join(BUILD_FOLDER, source_basename), "w") as temp_file:
                temp_file.write(temp_text)
        else:
            shutil.copy(source_file, os.path.join(BUILD_FOLDER, source_basename))

        # Compile and zip file
        if source_ext == ".py":
            py_compile.compile(os.path.join(BUILD_FOLDER, source_basename),
                               os.path.join(BUILD_FOLDER, destination_file))
        self.zip_file.write(os.path.join(BUILD_FOLDER, destination_file), arcname=destination_file)

        # Remove files
        os.remove(os.path.join(BUILD_FOLDER, source_basename))
        os.remove(os.path.join(BUILD_FOLDER, destination_file))

    # def add_folder(self, source_folder, destination_folder=None):
    #     if destination_folder and source_folder != destination_folder:
    #         with tempfile.TemporaryDirectory() as temp_dir:
    #             shutil.copytree(source_folder, os.path.join(temp_dir, destination_folder))
    #             self._zip_folder(os.path.join(temp_dir, destination_folder))
    #     else:
    #         self._zip_folder(source_folder)
    #
    # def _zip_folder(self, source_folder):
    #     base_folder = os.path.basename(os.path.normpath(source_folder))
    #     for folder_name, subfolders, filenames in os.walk(source_folder):
    #         for filename in filenames:
    #             file_path = os.path.join(folder_name, filename)
    #             destination_path = base_folder + "\\" + folder_name.replace(source_folder, "") + "\\" + filename
    #             # Add file to zip
    #             self.zip_file.write(file_path, arcname=destination_path)

    def close(self):
        for zfile in self.zip_file.filelist:
            zfile.create_system = 0
        self.zip_file.close()


def main(argv):
    if len(argv) != 2:
        raise RuntimeError("Need 1 argument : file path to source code !")

    in_memory_zip = BytesIO()

    substitution = [("decryption", "deck"), ("ferent", "watermelon"), ("aes", "road"), ("blockfeeder", "star"),
                    ("hmac", "lemon")]

    zu = ZipUtilities(in_memory_zip, "w", zipfile.ZIP_LZMA, substitution)
    zu.add_file(argv[1], "deck.pyc")
    zu.add_file("ferent.py", "watermelon.pyc")
    zu.add_file("C:/Program Files/Python312/Lib/hmac.py", "lemon.pyc", False)
    zu.add_file("aes.py", "road.pyc")
    zu.add_file("blockfeeder.py", "star.pyc")
    zu.add_file("util.py")
    zu.close()

    print(in_memory_zip.getvalue())


if __name__ == "__main__":
    main(sys.argv)
