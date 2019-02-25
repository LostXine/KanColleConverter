# coding=utf-8
import json
import re
import traceback
from collections import OrderedDict


# 主程序设置
main_config = {}
# Regular expression for comments
comment_re = re.compile('(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?', re.DOTALL | re.MULTILINE)


def parse_json(filename):
    """ Parse a JSON file
        First remove comments and then use the json module package
        Comments look like :
            // ...
        or
            /*
            ...
            */
    """
    with open(filename, 'r', encoding="utf-8") as f:
        content = ''.join(f.readlines())
        # Looking for comments
        match = comment_re.search(content)
        while match:
            # single line comment
            content = content[:match.start()] + content[match.end():]
            match = comment_re.search(content)
        # print content
        # Return json file
        return json.loads(content, object_pairs_hook=OrderedDict)


def save_json(name, js):
    with open(name, 'w', encoding='utf-8') as json_file:
        json.dump(js, json_file, ensure_ascii=False, indent=4)


def load_json(name):
    try:
        return parse_json('./data/%s.json' % name)
    except json.decoder.JSONDecodeError:
        print("ERROR while parsing %s.json" % name)
        traceback.print_exc()
        return []


def load_vars():
    try:
        global main_config
        main_config = parse_json('./config.json')
    except:
        traceback.print_exc()
        print("Parse config.json failed.")


def load_config():
    load_vars()


if __name__ == "__main__":
    load_config()
