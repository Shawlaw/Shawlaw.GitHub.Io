#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import os.path
import subprocess
import time


class Article:
    def __init__(self, r_path, title, last_modified_time):
        self.r_path = r_path
        self.title = title
        self.last_modified_time = last_modified_time

    def __lt__(self, other):  # override <操作符
        if self.last_modified_time < other.last_modified_time:
            return True
        return False

    def to_md_link(self):
        return '{} - [{}]({})'.format(self.get_readable_file_edit_time(), self.title, self.r_path)

    def to_cmt_msg(self):
        return '{} - {}'.format(self.get_readable_file_edit_time(), self.title)

    def get_readable_file_edit_time(self):
        # return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(file_path)))
        return time.strftime("%Y-%m-%d", time.localtime(self.last_modified_time))


def parse_exist(src_md_file_path):
    exist_link_set = set()
    if os.path.exists(src_md_file_path):
        with open(src_md_file_path, 'rt', encoding='utf-8') as f:
            for line in f:
                match_result = re.search(r'(?<=\()\.[^ ]+(?=\))', line)
                if match_result is not None:
                    match_text = match_result.group()
                    exist_link_set.add(match_text)
    return exist_link_set


def parse_folder(folder_path):
    all_article_link_dict = dict()
    for parent, dir_names, filenames in os.walk(folder_path, followlinks=True):
        # 每个目录是一次遍历
        r_path = os.path.relpath(parent, folder_path)
        if r_path.startswith(".") or r_path.__contains__("\\."):
            # 忽略所有.开头的文件/文件夹
            continue
        for filename in filenames:
            file_path = os.path.join(parent, filename)
            if str(filename).endswith(".md"):
                try_create_article(folder_path, file_path, all_article_link_dict)
    # print(all_article_link_dict)
    return all_article_link_dict


def try_create_article(top_folder_path, md_file_path, result_dict):
    with open(md_file_path, 'rt', encoding='utf-8') as f:
        file_edit_time = os.path.getmtime(md_file_path)
        for line in f:
            match_result = re.search(r'(?<=^# ).+(?=$)', line)
            if match_result is not None:
                match_text = match_result.group()
                web_rpath = convert_rpath_to_web_rpath(os.path.relpath(md_file_path, top_folder_path))
                result_dict[web_rpath] = Article(web_rpath, match_text, file_edit_time)


def convert_rpath_to_web_rpath(local_rpath):
    return "./" + (local_rpath.replace("\\", "/")[:-3])


def update_index_md(idx_md_file_path, folder_path):
    current_idx = parse_exist(idx_md_file_path)
    latest_link_dict = parse_folder(folder_path)
    for idx in current_idx:
        # 把已有的超链从dict里去除
        if idx in latest_link_dict:
            latest_link_dict.pop(idx)
    if len(latest_link_dict) < 1:
        return
    new_link_list = list(latest_link_dict.values())
    new_link_list.sort()
    # print(new_link_list)
    with open(idx_md_file_path, 'at+', encoding='utf-8') as f:
        for link in new_link_list:
            f.write("\r\n")
            f.write(link.to_md_link())
    new_link_list_cmt_msg = map(lambda x: x.to_cmt_msg(), new_link_list)
    git_cmt_msg_detail = '" -m "'.join(new_link_list_cmt_msg)
    with subprocess.Popen(
            r'git add . && git commit -m "新增{}篇文章" -m "{}"'.format(len(new_link_list), git_cmt_msg_detail),
            shell=True, encoding="utf8",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE) as p:
        output, errors = p.communicate()
        lines = output.strip()
    print(lines)


if __name__ == '__main__':
    cwd = os.getcwd()
    # print(cwd)
    update_index_md(os.path.join(cwd, "index.md"), cwd)
