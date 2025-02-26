import csv
import os
import re
import subprocess
import uuid

from lxml import html


def generate_uuid():
    return str(uuid.uuid4())


def write_data_to_file(file_path, content):
    with open(file_path, "w") as file:
        file.write(content)


def read_file(filename):
    with open(filename, "r") as file:
        contents = file.read()
    return contents


def assert_valid_csv_file(file_path, **kwargs):
    """
    Asserts that the given .csv file is valid.
    A CSV file is considered valid if  all of its rows have the same number of columns.
    """
    assert os.path.exists(file_path) is True
    delimiter = kwargs.get("delimiter", ",")

    with open(file_path, mode="r") as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=delimiter)
        columns_number = len(next(csv_reader))
        assert all(len(row) == columns_number for row in csv_reader) is True


def find_elements_in_html_file(html_file_path, xpath):

    if not os.path.exists(html_file_path):
        raise Exception(f"File [{html_file_path}] does not exist!")

    with open(html_file_path, "r", encoding="utf-8") as html_file:
        content = html_file.read()

    tree = html.fromstring(content)

    elements = tree.xpath(xpath)

    if elements is None:
        raise Exception(f"No element found with xpath: [{xpath}]")

    return elements


def delete_directory(file_name):
    subprocess.run(
        f"rm -rf {file_name}",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def get_screen_size():
    output = subprocess.check_output("xdpyinfo | grep dimensions", shell=True).decode()
    m = re.search(r"dimensions:\s+(\d+x\d+)", output)
    if m:
        return m.group(1)
    else:
        raise RuntimeError("Could not get screen size")
