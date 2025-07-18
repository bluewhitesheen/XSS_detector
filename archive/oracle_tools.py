import requests
import bs4
from urllib.parse import unquote
from bs4 import BeautifulSoup   
from zss import Node, simple_distance


def do_xss_post_request(endpoint, payload):
    html_page = requests.post(url=endpoint, json={"payload": [payload]})
    return unquote(html_page.content)


def write_xss_post_request_output(endpoint, payload, output):
    html_page = do_xss_post_request(endpoint, payload)
    with open(output, 'w') as f:
        f.write(str(html_page))

def bs4_to_tree(tag: bs4.element.Tag, node=Node("html")):
    # print(tag.name, list(map(lambda x:x.name, tag.findChildren(recursive=False))))
    if tag.children:
        for child in tag.findChildren(recursive=False):  # recursive = False b/c otherwise, it messes things up
            node.addkid(bs4_to_tree(child, Node(child.name)))
    return node


def get_parse_tree(html):
    soup = BeautifulSoup(html, 'html.parser')
    dom_tree = (bs4_to_tree(soup.html, Node("html")))
    return dom_tree


def get_distance_between_htmls(html_1, html_2):
    dom_tree_1 = get_parse_tree(html_1)
    dom_tree_2 = get_parse_tree(html_2)
    distance = simple_distance(dom_tree_1, dom_tree_2)
    return distance


def is_same_dom(html_1, html_2):
    distance = get_distance_between_htmls(html_1, html_2)
    return True if distance == 0 else False
