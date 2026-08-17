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
    .replace("{", '&#x7B;')\

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
                'name': 'PCLCustomHelpBuilder',
                'output_url': '',
            }
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f)
    except BaseException as e:
        logging.error(f'加载配置失败: {e}')
        exit()
    NAME = config['name']
    OUTPUT_URL = config['output_url']

def load_contents():
    global base_contents, doc_tags
    logging.info('开始加载文件布局')
    doc_tags = {}
    base_contents = []
    def load_path(path='', docpath=''):
        global doc_tags
        output = []
        contents_path = os.path.join(BASE_PATH, 'docs', path)
        items = os.listdir(contents_path)
        for item in items:
            if item.startswith('.'):
                continue
            item_path = os.path.join(contents_path, item)
            if os.path.isfile(item_path) and item.endswith('.md'):
                if (item == 'index.md' and path != '') or os.path.exists(os.path.join(contents_path, item[:-3])):
                    continue
                post = frontmatter.load(item_path)
                output.append({
                    'name': post.get('title', post.get('name', item[:-3])),
                    'file': path+item,
                    'visiable': post.get('visiable', True),
                    'entrance': post.get('entrance', False),
                    'tags': post.get('tags', []),
                    'index': post.get('index', 0),
                })
                if not isinstance(post.get('visiable', True), bool):
                    logging.error(f'Visiable错误: {path+item}: {post.get('visiable', True)}')
                    exit()
                if not isinstance(post.get('entrance', False), bool):
                    logging.error(f'Entrance错误: {path+item}: {post.get('entrance', True)}')
                    exit()
                if not isinstance(post.get('tags', []), list):
                    logging.error(f'Tags列表错误: {path+item}: {post.get('tags', [])}')
                    exit()
                if not isinstance(post.get('index', 0), int):
                    logging.error(f'Index错误: {path+item}: {post.get('index', 0)}')
                    exit()
                for t in post.get('tags', []): # type: ignore
                    if t not in doc_tags:
                        doc_tags[t] = []
                    doc_tags[t].append(docpath+post.get('name', item[:-3])) # type: ignore
            elif os.path.isdir(item_path):
                if os.path.exists(os.path.join(item_path, 'config.json')):
                    with open(os.path.join(item_path, 'config.json'), 'r', encoding='utf-8') as f:
                        config = json.load(f)
                else:
                    config = {}
                have_index_file = os.path.exists(os.path.join(contents_path, f'{item}.md'))
                if have_index_file:
                    index_config = frontmatter.load(os.path.join(contents_path, f'{item}.md'))
                else:
                    index_config = {}
                output.append({
                    'name': index_config.get('name', config.get('name', item)),
                    'file': os.path.join(contents_path, f'{item}.md') if have_index_file else False,
                    'folded': config.get('folded', False),
                    'visiable': config.get('visiable', True),
                    'sub': load_path(path+item+'/', path+config.get('name', item)+'/'),
                    'index': index_config.get('index', config.get('index', 0)),
                })
                if not isinstance(config.get('visiable', True), bool):
                    logging.error(f'Visiable错误: {path+item}: {config.get('visiable', True)}')
                    exit()
                if not isinstance(config.get('index', config.get('index', 0)), int):
                    logging.error(f'Index错误: {path+item}: {config.get('index', config.get('index', 0))}')
                    exit()
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
    markdown = mistune.create_markdown(renderer='ast', plugins=['table','strikethrough'])
    def analysis_para(para_data, **attr):
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
                    if 'textattr' in attr:
                        style = ''
                        t = f'body/para/text/style_text'
                        load_template(t)
                        if 'blod' in attr['textattr']:
                            load_template(f'body/para/text/bold')
                            style += templates[f'body/para/text/bold']
                        if 'italic' in attr['textattr']:
                            load_template(f'body/para/text/italic')
                            style += templates[f'body/para/text/italic']
                        if 'strikethrough' in attr['textattr']:
                            load_template(f'body/para/text/strikethrough')
                            style += templates[f'body/para/text/strikethrough']
                        para += replaces(templates[t],{
                            'content': token['raw'],
                            'style': style
                        })
                    else:
                        para += escape_xaml(token['raw'])
                case 'inline_html':
                    para += escape_xaml(token['raw'])
                case 'strong':
                    para += analysis_para(token['children'], textattr=attr.get('textattr', [])+['blod'])
                case 'emphasis':
                    para += analysis_para(token['children'], textattr=attr.get('textattr', [])+['italic'])
                case 'strikethrough':
                    para += analysis_para(token['children'], textattr=attr.get('textattr', [])+['strikethrough'])
                case 'codespan':
                    t = f'body/para/inlinecode'
                    load_template(t)
                    para += replaces(templates[t],{
                        'content':escape_xaml(token['raw'][0])+escape_xaml(token['raw'][1:], no_cb=True)
                    })
                case 'link':
                    url = unquote(token['attrs']['url'])
                    # 网址链接
                    if url.startswith('http://') or url.startswith('https://'):
                        t = f'body/para/event_btn'
                        url = ['打开网页', url]
                    # 帮助页
                    elif url.startswith('help!'):
                        t = f'body/para/event_btn'
                        url = ['打开帮助', url[5:]]
                    # 自定义功能按钮
                    elif url.startswith('event!'):
                        t = f'body/para/event_btn'
                        url = url[6:].split('!', maxsplit=1)
                    # 本帮助内跳转
                    elif url.startswith('jump!'):
                        t = f'body/para/event_btn'
                        url = ['打开帮助', OUTPUT_URL+url[5:]+'.json']
                    elif url.startswith('/'):
                        t = f'body/para/event_btn'
                        url = ['打开帮助', OUTPUT_URL+url[1:]+'.json']
                    # 复制文本
                    else:
                        t = f'body/para/event_btn'
                        url = ['复制文本', url]
                    load_template(t)
                    para += replaces(templates[t],{
                        'type':url[0],
                        'data':escape_xaml(url[1]),
                        'content': analysis_para(token['children'], **attr)
                    })
                case 'image':
                    t = f'body/para/image'
                    load_template(t)
                    url = token['attrs']['url']
                    if url.startswith('/'):
                        url = os.path.join(OUTPUT_URL, '.public', url[1:]).replace('\\', '/')
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
                    if len(token['children'][0].get('children', [])) > 0:
                        if token['children'][0]['children'][0].get('raw', '') == '[warn]':
                            token['children'][0]['children'].pop(0)
                            t = f'body/quote/warn'
                        elif token['children'][0]['children'][0].get('raw', '') == '[tip]':
                            token['children'][0]['children'].pop(0)
                            t = f'body/quote/tip'
                        else:
                            t = f'body/quote/main'
                    else:
                        t = f'body/quote/main'
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
    
    def contents_xaml(hold_name, path='', indent=0, cdata=base_contents):
        load_template('sidebar/item')
        load_template('sidebar/item_hold')
        load_template('sidebar/item_more')
        output = ''
        for c in sorted(cdata, key=lambda x: x['index']):
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
    def tags_xaml(hold = None, up = []):
        load_template('sidebar/tag')
        load_template('sidebar/item')
        load_template('sidebar/item_tag')
        output = ''
        for t in list(doc_tags.keys()):
            if hold == t:
                output += replaces(templates['sidebar/item_hold'],{
                    'indent': 0,
                    'name': t+': '+str(len(doc_tags[t])),
                })
            else:
                if t in up:
                    output += replaces(templates['sidebar/item_tag'],{
                        'indent': 0,
                        'name': t+': '+str(len(doc_tags[t])),
                        'url': OUTPUT_URL+'.tags/'+t+'.json'
                    })
                else:
                    output += replaces(templates['sidebar/item'],{
                        'indent': 0,
                        'name': t+': '+str(len(doc_tags[t])),
                        'url': OUTPUT_URL+'.tags/'+t+'.json'
                    })
        return replaces(templates['sidebar/tag'],{
            'tags': output
        })
    def footer_xaml():
        return replaces(templates['sidebar/footer'],{
            'version':VERSION
        })

    def analysis_contents(contents=base_contents, namepath=''):
        global entrance
        # 层级下生成文件
        occupied_name = []
        for content in sorted(contents if namepath != '' else contents + [{
            'name': NAME+' 目录', 
            'file': False, 
            'mainpage': True, 
            'sub': base_contents
        }], key=lambda x: int(x.get('index', 0))):
            if content.get('mainpage') and entrance:
                continue
            doc_name = content['name']
            
            if doc_name in occupied_name:
                logging.error(f'contents 文档名重复: {doc_name}')
                exit()
            if doc_name == 'Custom':
                logging.error(f'contents 禁止使用的文档名: {doc_name}')
                exit()
            logging.info(f'生成文件: {namepath}{doc_name}')
            occupied_name.append(doc_name)

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
                def subdoc(*a, **kwa):
                    def _(docdata, path=''):
                        sdoutput = []
                        for sd in sorted(docdata.get('sub',[]), key=lambda x: x['index']):
                            if sd['visiable']:
                                sdoutput.append(f'- [{sd['name']}](jump!{namepath+(doc_name+'/' if not content.get('mainpage') else '')+path+sd['name']})')
                                if 'sub' in sd:
                                    sdoutput.append(_(sd, path+sd['name']+'/'))
                        return sdoutput
                    def join_with_indent(items, depth=0) :
                        lines = []
                        for item in items:
                            if isinstance(item, str):
                                lines.append(" " * (depth * 2) + item)
                            elif isinstance(item, list):
                                lines.append(join_with_indent(item, depth + 1))
                        return "\n".join(lines)
                    sdoutput = join_with_indent(_(*a, **kwa))
                    return sdoutput

                raw_data = '\n'.join((
                    f'# {doc_name}',
                    f'',
                    subdoc(content)
                ))
            
            body = analysis_level(markdown(raw_data))

            # 页脚
            load_template('sidebar/footer')
            footer = footer_xaml()

            # 标签
            if doc_tags:
                tags = tags_xaml(up=content.get('tags', []))
            else:
                tags = ''

            page = replaces(templates['page'],{
                'contents':contents_xaml(namepath+(doc_name if not content.get('mainpage') else '')),
                'tag':tags,
                'body':body,
                'name':NAME,
                'footer':footer
            })

            if not content.get('mainpage'):
                os.makedirs(os.path.join(BASE_PATH, 'output', namepath), exist_ok=True)
                with open(os.path.join(BASE_PATH, 'output', namepath+doc_name+'.xaml'), 'w', encoding='utf-8') as f:
                    f.write(page)
                with open(os.path.join(BASE_PATH, 'output', namepath+doc_name+'.json'), 'w', encoding='utf-8') as f:
                    f.write(json.dumps({'Title':f'{NAME} | {doc_name}'}))
            
            if content.get('entrance') or (content.get('mainpage') and not entrance):
                if entrance:
                    logging.error(f'contents 多个入口: {content['file']}')
                    exit()
                entrance = True
                with open(os.path.join(BASE_PATH, 'output', 'Custom.xaml'), 'w', encoding='utf-8') as f:
                    f.write(page)
                with open(os.path.join(BASE_PATH, 'output', 'Custom.json'), 'w', encoding='utf-8') as f:
                    f.write(json.dumps({'Title':f'{NAME} | {doc_name}'}))

            if content.get('sub',[]) and not content.get('mainpage'):
                analysis_contents(content['sub'], namepath+doc_name+'/')
    def analysis_tags():
        load_template('page')
        for t in list(doc_tags.keys()):
            os.makedirs('output/.tags', exist_ok=True)
            raw_data = '\n'.join((
                f'# 标签 {t}',
                f'',
                *[
                    f'- [{tdoc}](jump!{tdoc})'
                    for tdoc in doc_tags[t]
                ]
            ))
            body = analysis_level(markdown(raw_data))
            tags = tags_xaml(hold=t)
            load_template('sidebar/footer')
            footer = footer_xaml()

            page = replaces(templates['page'],{
                'contents':contents_xaml(''),
                'tag':tags,
                'body':body,
                'name':NAME,
                'footer':footer
            })
            with open(os.path.join(BASE_PATH, 'output', '.tags', f'{t}.xaml'), 'w', encoding='utf-8') as f:
                f.write(page)
            with open(os.path.join(BASE_PATH, 'output', '.tags', f'{t}.json'), 'w', encoding='utf-8') as f:
                f.write(json.dumps({'Title':f'{NAME} | 标签 {t}'}))
    def copy_public_file():
        logging.info('开始复制public文件')
        shutil.copytree(os.path.join(BASE_PATH, 'public'), os.path.join(BASE_PATH, 'output/.public'), dirs_exist_ok=True)

    analysis_contents()
    analysis_tags()
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