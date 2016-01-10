import xml.etree.cElementTree as ElementTree
from files import download_file

__author__ = 'Gyfis'


def load_xml(url_string, filename):
    e = ElementTree.parse(download_file(url_string, filename))
    return e.getroot()
