# -*- coding: utf-8 -*-
'''
@Author: xtfge
@E-mail: xtfge_0915@163.com
@Date: 2020-03-21 15:36:55
@LastEditors: zhangbo
@LastEditTime: 2020-03-30 19:41:29
@Desc:Cesium3dTileset爬虫程序
'''
import os
import getopt
import requests
import json
import sys
import msvcrt
import time

credit = '''本程序及利用本程序获得的资源严禁在网络上公开传播及用于商业用途，对于使用不当造成的法律后果，本程序的开发者不承担任何连带责任。'''


def writeContent(content, filename):
    """写b3dm文件"""
    if content is None:
        return
    with open(filename, "wb") as code:
        code.write(content)


def get_dir(path):
    '''获得文件夹'''
    return os.path.dirname(path)+'/'


def exists(path):
    '''判断路径是否存在'''
    return os.path.exists(path)


def get_ext(path):
    '''获得文件扩展名'''
    filename, ext = os.path.splitext(path)
    return ext


def create_dir(path):
    '''创建文件夹'''
    os.makedirs(path)


def walkTree(root, callback, base=''):
    '''遍历树,获得content'''
    if 'children' in root and root['children'] is None:
        if 'content' in root and root['content'] is not None and callable(callback):
            if('url' in root['content'] and base != ''):
                root['content']['url'] = os.path.join(
                    base, root['content']['url'])
            elif('uri' in root['content'] and base != ''):
                root['content']['uri'] = os.path.join(
                    base, root['content']['uri'])
            callback(root['content'])
    else:
        if 'content' in root and root['content'] is not None and callable(callback):
            if('url' in root['content'] and base != ''):
                root['content']['url'] = os.path.join(
                    base, root['content']['url'])
            elif('uri' in root['content'] and base != ''):
                root['content']['uri'] = os.path.join(
                    base, root['content']['uri'])
            callback(root['content'])
        if 'children' in root:
            children = root['children']
            for child in children:
                walkTree(child, callback,base)


class Cesium3dtileset:
    def __init__(self, url, headers=None,mate=False):
        self.url = url
        if headers is None:
            headers = {
                'user-agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
            }
        self.mate=mate
        self.success = 0
        self.fail = 0
        self.headers = headers
        self.root = self.get(self.url, True)
        self.json = []
        if(INFO.basePath==''):
            INFO.basePath=get_dir(self.url)
        self.base_path=get_dir(self.url).replace(INFO.basePath,"")

    def pull(self, path, create=False):
        '''拉取tileset内容'''
        if exists(path) == False:
            if create:
                create_dir(path)
            else:
                raise Exception('路径'+path+'不存在')
        # 写json文件
        if(self.root is None):
            return
        if self.mate:
            print('[%d/%d]正在拉取 %s' %
                (INFO.success+INFO.fail, INFO.count, self.url))
        else:
            print('[%d]正在拉取 %s' %
                (INFO.success+INFO.fail, self.url))
        if self.root is None:
            return

        writeContent(self.root, os.path.join(path, self.base_path,os.path.basename(self.url)))

        tree = self.parse()

        def download(content):
            try:
                bolb=content['url']
            except Exception:
                bolb=content['uri']
            if (isinstance(content, dict)):
                _dir = get_dir(bolb)
                if(exists(os.path.join(path, _dir)) == False):
                    create_dir(os.path.join(path, _dir))

                if(get_ext(bolb) == '.json'):
                    # 由于cesium3dtilset中的路径是相对路径
                    # 所以子tile的路径要加上父tile的路径
                    # url = os.path.join(self.base_path, bolb)
                    # print(INFO.basePath, bolb)
                    tileset = Cesium3dtileset(
                        os.path.join(INFO.basePath, bolb),mate=self.mate)
                    # tileset.base_path = get_dir(url)
                        
                    # 如果content是json文件，创建一个新的Cesium3dTileset
                    tileset.pull(path, create)
                elif get_ext(bolb) == '.b3dm':
                    bolbContent = self.get(os.path.join(
                        get_dir(self.url), os.path.basename(bolb)), True)
                    if self.mate:
                        print('[%d/%d]正在拉取 %s' % (INFO.success+INFO.fail, INFO.count,
                                              os.path.join(
                        get_dir(self.url), os.path.basename(bolb))))
                    else:
                        print('[%d]正在拉取 %s' % (INFO.success+INFO.fail,
                                              os.path.join(
                        get_dir(self.url), os.path.basename(bolb))))
                    if(exists(os.path.join(path, bolb))):
                        return
                    writeContent(bolbContent, os.path.join(path,self.base_path, os.path.basename(bolb)))
        walkTree(tree['root'], download, self.base_path)

    def parse(self):
        try:
            root = json.loads(self.root)
        except Exception:
            root = None
        return root

    def get(self, url, info=False):
        response = requests.get(url.strip(), headers=self.headers)
        if(response.status_code != 200 and info):
            print('\n资源%s拉取失败，错误原因%d\n' % (url, response.status_code))
            INFO.fail += 1
            return None
        if info:
            INFO.success += 1
        return response.content

    def get_mate(self):
        '''获取资源数'''
        root = self.parse()

        def count(content):
            # global baseURL
            # sys.stdout.flush()
            try:
                bolb=content['url']
            except Exception:
                bolb=content['uri']
            try:
                ext = get_ext(bolb)
            except Exception:
                ext = get_ext(bolb)
            if(ext == '.b3dm'):
                INFO.count += 1

            elif(ext == '.json'):
                if(get_dir(bolb) != ''):
                    url = bolb
                else:
                    url = os.path.join(self.base_path, bolb)
                if(get_dir(bolb) != ''):
                    self.base_path = get_dir(bolb)

                INFO.count += 1
                child = self.get(os.path.join(get_dir(self.url), url))
                if(child is not None):
                    try:
                        root = json.loads(child.decode('utf-8'))
                        walkTree(root['root'], count, self.base_path)
                    except Exception:
                        pass
            sys.stdout.write('\r正在收集资源（已收集%s），请稍候...' % INFO.count)
        if self.parse() is not None:
            walkTree(self.parse()['root'], count)
        self.base_path = ''


class INFO:
    fail = 0
    success = 0
    count = 1
    basePath=""


if __name__ == "__main__":
    url = None
    output = None
    forced = False
    mate=False
    try:
        opts, args = getopt.getopt(sys.argv[1:], "-h-u:-o:-f-i")
    except getopt.GetoptError:
        print('get-3dtileset.py -u <url> -o <output> -f <forceed-create>')
        sys.exit(2)

    for opt_name, opt_value in opts:
        if opt_name in ('-h'):
            print('get-3dtileset.py -u <url> -o <output> [-f]')
            exit()
        if opt_name in ('-u'):
            url = opt_value
        if opt_name in ('-o'):
            output = opt_value
        if opt_name in ('-f'):
            forced = True
        if opt_name in ('-i'):
            mate = True

    if(url is None):
        exit('请输入正确的URL地址')
    if output is None:
        exit('请设置正确的输出路径')
    if(exists(output) == False and forced == False):
        exit('路径'+output+'不存在，请查检输入或使用使用-f参数')
    print(credit, end='', flush=True)
    print('\n')
    print('同意上述协议？(同意y|不同意[n])', end='', flush=True)
    input = b''
    while 1:
        ch = msvcrt.getch()
        # 回车
        if ch == b'\r':
            msvcrt.putch(b'\n')

            break
        # 退格
        elif ch == b'\b':
            input = ''
            msvcrt.putch(b'\b')
            msvcrt.putch(b' ')
            msvcrt.putch(b'\b')

        # Esc
        elif ch == b'\x1b':
            break
        else:
            input = ch
            # msvcrt.putch(b'\b')
            msvcrt.putch(ch)
    if(input.decode('utf-8') != 'Y' and input.decode('utf-8') != 'y'):
        exit()
    tile = Cesium3dtileset(url,mate=mate)
    if mate:
        tile.get_mate()
        print('\n')
    tile.pull(output, forced)
    if INFO.count:
        print('下载完成，成功%d(%.2f%s),失败%d(%.2f%s)' % (INFO.success,100*INFO.success/INFO.count,'%',INFO.fail,100*INFO.fail/INFO.count,'%'))
