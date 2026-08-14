import os
import logging
import shutil
import datetime
import json
import mistune
import frontmatter
from urllib.parse import unquote

BASE_PATH = os.path.dirname(__file__)
templates = {}
entrance = False
VERSION = 'v0.1'

def escape_xaml(text, **kwargs):
    if text is None:
        return ''
    b = text.replace('&', '&amp;')\
    .replace('<', '&lt;')\
    .replace('>', '&gt;')\
    .replace('"', '&quot;')\
    .replace("'", '&apos;')\
    .replace('"', '&quot;')\

    if not kwargs.get('no_cb'):
        b = b.replace("{", '{}{')
    return b

def load_template(names, noxaml = False):
    global templates
    if not isinstance(names, list):
        names = [names]
    for n in names:
        if n not in templates:
            t_path = os.path.join(BASE_PATH, 'templates', n + ('' if noxaml else '.xaml'))
            try:
                with open(t_path, 'r', encoding='utf-8') as f:
                    templates[n] = f.read()
            except FileNotFoundError:
                logging.error(f'模板文件不存在: {t_path}')
                exit()
            except Exception as e:
                logging.error(f'加载模板失败: {t_path}, 错误: {e}')
                exit()

def replaces(string: str, s: dict):
    output = string
    for l, d in s.items():
        output = output.replace('{'+l+'}', str(d))
    return output

def load_config():
    global OUTPUT_URL, NAME
    logging.info('开始加载配置')
    config_path = os.path.join(BASE_PATH, 'config.json')
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            assert 'name' in config, '无 name 字段'
            assert 'output_url' in config, '无 url 字段'
        else:
            config = {
                'name': 'PCLCustomHelpBuilder'
            }
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f)
    except BaseException as e:
        logging.error(f'加载配置失败: {e}')
        exit()
    NAME = config['name']
    OUTPUT_URL = config['output_url']

def load_contents():
    global base_contents
    logging.info('开始加载文件布局')
    base_contents = []
    def load_path(path=''):
        output = []
        contents_path = os.path.join(BASE_PATH, 'docs', path)
        items = os.listdir(contents_path)
        for item in items:
            if item.startswith('.'):
                continue
            item_path = os.path.join(contents_path, item)
            if os.path.isfile(item_path) and item.endswith('.md'):
                if item == 'index.md' and path != '':
                    continue
                post = frontmatter.load(item_path)
                output.append({
                    'name': post.get('name', item[:-3]),
                    'file': path+item,
                    'visiable': post.get('visiable', True),
                    'entrance': post.get('entrance', False),
                })
            elif os.path.isdir(item_path):
                have_index_file = os.path.exists(os.path.join(item_path, 'index.md'))
                if os.path.exists(os.path.join(item_path, 'config.json')):
                    with open(os.path.join(item_path, 'config.json'), 'r', encoding='utf-8') as f:
                        config = json.load(f)
                else:
                    config = {}
                output.append({
                    'name': config.get('name', item),
                    'file': os.path.join(item_path, 'index.md') if have_index_file else False,
                    'folded': config.get('folded', False),
                    'visiable': config.get('visiable', True),
                    'sub': load_path(path+item+'/')
                })
        return output
    try:    
        base_contents = load_path()
    except Exception as e:
        logging.error(f'加载 contents 时发生错误: {e}')
        exit()

def build_file():
    logging.info('开始生成输出文件')
    shutil.rmtree('output',ignore_errors=True)
    os.makedirs('output', exist_ok=True)
    markdown = mistune.create_markdown(renderer='ast', plugins=['table'])

    def analysis_contents(contents=base_contents, namepath=''):
        global entrance
        def contents_xaml(hold_name, path='', indent=0, cdata=base_contents):
            load_template('sidebar/item')
            load_template('sidebar/item_hold')
            load_template('sidebar/item_more')
            output = ''
            for c in cdata:
                if c.get('visiable') or path in hold_name:
                    if path+c['name'] == hold_name:
                        output += replaces(templates['sidebar/item_hold'],{
                            'indent': indent * 20,
                            'name': c['name'],
                        })
                    else:
                        if not (c.get('folded') and not (hold_name.startswith(path+c['name']+'/') or hold_name == path+c['name'])):
                            output += replaces(templates['sidebar/item'],{
                                'indent': indent * 20,
                                'name': c['name'],
                                'url': OUTPUT_URL+path+c['name']+'.json',
                            })
                        else:
                            output += replaces(templates['sidebar/item_more'],{
                                'indent': indent * 20,
                                'name': c['name'],
                                'url': OUTPUT_URL+path+c['name']+'.json',
                            })
                    if c.get('sub',[]):
                        if not (c.get('folded') and not (hold_name.startswith(path+c['name']+'/') or hold_name == path+c['name'])):
                            output += contents_xaml(hold_name, path+c['name']+'/', indent+1, c['sub'])
            return output
        def analysis_para(para_data):
            def data_to_text(link_data):
                raw = ''
                for c in link_data:
                    if 'raw' in c:
                        raw += c['raw']
                    elif 'children' in c:
                        raw +=  data_to_text(c['children'])
                return raw
            para = ''
            for tokenindex, token in enumerate(para_data, start=1):
                match token['type']:
                    case 'linebreak':
                        t = f'body/para/lb'
                        load_template(t)
                        para += templates[t]
                    case 'text':
                        para += escape_xaml(token['raw'])
                    case 'inline_html':
                        para += escape_xaml(token['raw'])
                    case 'emphasis':
                        t = f'body/para/italic'
                        load_template(t)
                        para += replaces(templates[t],{
                            'content':analysis_para(token['children'])
                        })
                    case 'strong':
                        t = f'body/para/bold'
                        load_template(t)
                        para += replaces(templates[t],{
                            'content':analysis_para(token['children'])
                        })
                    case 'codespan':
                        t = f'body/para/inlinecode'
                        load_template(t)
                        para += replaces(templates[t],{
                            'content':escape_xaml(token['raw'][0])+escape_xaml(token['raw'][1:], no_cb=True)
                        })
                    case 'link':
                        # 网址链接
                        if token['attrs']['url'].startswith('http://') or token['attrs']['url'].startswith('https://'):
                            t = f'body/para/event_btn'
                            url = ['打开网页', token['attrs']['url']]
                        # public/内文件链接
                        elif token['attrs']['url'].startswith('/'):
                            t = f'body/para/event_btn'
                            url = ['打开网页', os.path.join(OUTPUT_URL, 'public', token['attrs']['url'])]
                        # 帮助页
                        elif token['attrs']['url'].startswith('help!'):
                            t = f'body/para/event_btn'
                            url = ['打开帮助', token['attrs']['url'][5:]]
                        # 自定义功能按钮
                        elif token['attrs']['url'].startswith('event!'):
                            t = f'body/para/event_btn'
                            url = unquote(token['attrs']['url'])[6:].split('!', maxsplit=1)
                        # 本帮助内跳转
                        elif token['attrs']['url'].startswith('jump!'):
                            t = f'body/para/event_btn'
                            url = ['打开帮助', OUTPUT_URL+token['attrs']['url'][5:]+'.json']
                        # 复制文本
                        else:
                            t = f'body/para/event_btn'
                            url = ['复制文本', token['attrs']['url']]
                        load_template(t)
                        para += replaces(templates[t],{
                            'type':url[0],
                            'data':url[1],
                            'content': analysis_para(token['children'])
                        })
                    case 'image':
                        t = f'body/para/image'
                        load_template(t)
                        url = token['attrs']['url']
                        if url.startswith('/'):
                            url = os.path.join(OUTPUT_URL, 'public', url[1:]).replace('\\', '/')
                        para += replaces(templates[t],{
                            'image':url,
                            'title': data_to_text(token['children'])
                        })
            return para
        def analysis_level(level_tokens, **kwargs):
            body = ''
            for tokenindex, token in enumerate(level_tokens, start=1):
                match token['type']:
                    case 'heading':
                        t = f'body/h{token['attrs']['level']}'
                        load_template(t)
                        body += replaces(templates[t],{
                            'content':analysis_para(token['children'])
                        })
                    case 'paragraph':
                        t = f'body/para'
                        load_template(t)
                        body += replaces(templates[t],{
                            'content':analysis_para(token['children'])
                        })
                    case 'block_text':
                        t = f'body/para'
                        load_template(t)
                        body += replaces(templates[t],{
                            'content':analysis_para(token['children'])
                        })
                    case 'block_quote':
                        t = f'body/quote'
                        load_template(t)
                        body += replaces(templates[t],{
                            'content':analysis_level(token['children'])
                        })
                    case 'list':
                        if token['attrs']['ordered']:
                            t = f'body/list/number_list'
                        else:
                            t = f'body/list'
                        load_template(t)
                        body += replaces(templates[t],{
                            'items':analysis_level(token['children'])
                        })
                    case 'list_item':
                        t = 'body/list/item'
                        load_template(t)
                        body += replaces(templates[t],{
                            'content':analysis_level(token['children'])
                        })
                    case 'block_code':
                        h_lang = 'info' in token.get('attrs',{})
                        if h_lang:
                            if token['attrs']['info'] == 'xaml' and token['raw'].startswith('<!-- pcl -->'):
                                t = f'body/source_code'
                                load_template(t)
                                body += replaces(templates[t],{
                                    'content':token['raw']
                                })
                                continue
                            t = f'body/codeblock_lang'
                        else:
                            t = f'body/codeblock'
                        load_template(t)

                        para_content = []
                        l = len(token['raw'].splitlines())
                        for index, line in enumerate(token['raw'].splitlines(), start=1):
                            para_content.append({
                                'raw': line,
                                'type': 'text'
                            })
                            if index != l:
                                para_content.append({'type': 'linebreak'})

                        if h_lang:
                            body += replaces(templates[t],{
                                'lang':token['attrs']['info'],
                                'content':analysis_para(para_content)
                            })
                        else:
                            body += replaces(templates[t],{
                                'content':analysis_para(para_content)
                            })
                    case 'thematic_break':
                        t = f'body/hr'
                        load_template(t)
                        body += templates[t]
                    case 'block_html':
                        t = f'body/para'
                        load_template(t)
                        body += replaces(templates[t],{
                            'content':analysis_para([{
                                'raw': token['raw'],
                                'type': 'text'
                            }])
                        })
                    case 'table':
                        t = [
                            f'body/table',
                            f'body/table/definitions/column',
                            f'body/table/definitions/row',
                        ]
                        load_template(t)

                        t_head = {}
                        t_body = {}
                        for c in token['children']:
                            if c['type'] == 'table_head':
                                t_head = c
                            if c['type'] == 'table_body':
                                t_body = c

                        body += replaces(templates[t[0]],{
                            'head-definitions':' '.join([templates[t[1]]] * len(t_head['children'])),
                            'head-items':analysis_level(t_head['children'], table_type='head'),
                            'body-row-definitions':' '.join([templates[t[2]]] * len(t_body['children'])),
                            'body-column-definitions':' '.join([templates[t[1]]] * len(t_head['children'])),
                            'body-items':' '.join([
                                analysis_level(row['children'], table_type='body', table_bottom=(rowindex==len(t_body['children'])), table_row=rowindex-1)
                                for rowindex, row in enumerate(t_body['children'], start=1)
                            ]),
                        })
                    case 'table_cell':
                        if kwargs.get('table_type') == 'head':
                            if tokenindex == 1:
                                t = f'body/table/head/left'
                            elif tokenindex == len(level_tokens):
                                t = f'body/table/head/right'
                            else:
                                t = f'body/table/head/middle'
                            load_template(t)
                            body += replaces(templates[t],{
                                'column-index':tokenindex-1,
                                'content':analysis_para(token['children'])
                            })
                        elif kwargs.get('table_type') == 'body':
                            if kwargs.get('table_bottom'):
                                if tokenindex == 1:
                                    t = f'body/table/body/left'
                                elif tokenindex == len(level_tokens):
                                    t = f'body/table/body/right'
                                else:
                                    t = f'body/table/body/bottom'
                            else:
                                if tokenindex == 1:
                                    t = f'body/table/body/middleleft'
                                elif tokenindex == len(level_tokens):
                                    t = f'body/table/body/middleright'
                                else:
                                    t = f'body/table/body/middle'
                            load_template(t)
                            body += replaces(templates[t],{
                                'column-index':tokenindex-1,
                                'row-index':kwargs.get('table_row'),
                                'content':analysis_para(token['children'])
                            })
            return body

        # 层级下生成文件
        occupied_name = []
        for content in contents:
            if content['name'] in occupied_name:
                logging.error(f'contents 文档名重复: {content['name']}')
                exit()
            if content['name'] == 'Custom':
                logging.error(f'contents 禁止使用的文档名: {content['name']}')
                exit()
            logging.info(f'生成文件: {content['name']}')
            occupied_name.append(content['name'])

            load_template('page')
            if content['file'] != False:
                if 'file' not in content:
                    logging.error(f'contents 未引用文档: {content}')
                    exit()
                doc_file_path = os.path.join(BASE_PATH, 'docs', content['file'])
                if not os.path.exists(doc_file_path):
                    logging.error(f'contents 未知引用文档: {content['file']}')
                    exit()

                with open(doc_file_path,'r',encoding='utf-8') as f:
                    raw_data = frontmatter.load(f).content
            else:
                raw_data = '\n'.join((
                    f'# {content['name']}',
                    f'',
                    *[
                        f'- [{sub['name']}](help!{OUTPUT_URL+namepath+content['name']+'/'+sub['name']+'.json'})' for sub in content.get('sub',[])
                    ],
                ))
            
            body = analysis_level(markdown(raw_data))

            # 页脚
            load_template('sidebar/footer')
            footer = replaces(templates['sidebar/footer'],{
                'ver':VERSION
            })

            page = replaces(templates['page'],{
                'contents':contents_xaml(namepath+content['name']),
                'body':body,
                'name':NAME,
                'footer':footer
            })

            os.makedirs(os.path.join(BASE_PATH, 'output', namepath), exist_ok=True)
            with open(os.path.join(BASE_PATH, 'output', namepath+content['name']+'.xaml'), 'w', encoding='utf-8') as f:
                f.write(page)
            with open(os.path.join(BASE_PATH, 'output', namepath+content['name']+'.json'), 'w', encoding='utf-8') as f:
                f.write(json.dumps({'Title':f'{NAME} | {content['name']}'}))

            if content.get('entrance'):
                if entrance:
                    logging.error(f'contents 多个入口: {content['file']}')
                    exit()
                entrance = True
                with open(os.path.join(BASE_PATH, 'output', 'Custom.xaml'), 'w', encoding='utf-8') as f:
                    f.write(page)
                with open(os.path.join(BASE_PATH, 'output', 'Custom.json'), 'w', encoding='utf-8') as f:
                    f.write(json.dumps({'Title':f'{NAME} | {content['name']}'}))

            if content.get('sub',[]):
                analysis_contents(content['sub'], namepath+content['name']+'/')

    def copy_public_file():
        logging.info('开始复制public文件')
        shutil.copytree(os.path.join(BASE_PATH, 'public'), os.path.join(BASE_PATH, 'output/public'), dirs_exist_ok=True)

    analysis_contents()
    copy_public_file()

LOG_FORMAT = '[%(asctime)s %(levelname)s] - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def setup_logging():
    shutil.rmtree('log', ignore_errors=True)
    os.makedirs('log', exist_ok=True)
    log_filename = f'log/log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log'

    # 根 logger 配置
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # 文件 handler
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logging.info(f'日志文件: {log_filename}')

def main():
    logging.info('主程序开始')
    os.makedirs('public', exist_ok=True)
    os.makedirs('output', exist_ok=True)
    load_config()
    load_contents()
    build_file()

if __name__ == '__main__':
    setup_logging()
    main()