#!/usr/bin/env python3
import argparse
import base64
import html
import json
import mimetypes
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


CONFIG_PATH = Path.home() / '.config' / 'azure-devops' / 'config.json'
OUT_ROOT = Path('/tmp/ado-workitems')
API_VERSION = '7.0'
COMMENTS_API_VERSION = '7.0-preview'


class PlainTextParser(HTMLParser):
    block_tags = {
        'address',
        'article',
        'aside',
        'blockquote',
        'br',
        'div',
        'dl',
        'fieldset',
        'figcaption',
        'figure',
        'footer',
        'form',
        'h1',
        'h2',
        'h3',
        'h4',
        'h5',
        'h6',
        'header',
        'hr',
        'li',
        'main',
        'nav',
        'ol',
        'p',
        'pre',
        'section',
        'table',
        'tr',
        'ul',
    }

    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in self.block_tags:
            self.parts.append('\n')

    def handle_endtag(self, tag):
        if tag in self.block_tags:
            self.parts.append('\n')

    def handle_data(self, data):
        self.parts.append(data)

    def text(self):
        raw = html.unescape(''.join(self.parts))
        lines = []
        for line in raw.splitlines():
            cleaned = re.sub(r'[ \t]+', ' ', line).strip()
            if cleaned:
                lines.append(cleaned)
        return '\n'.join(lines)


def die(message):
    print(f'error: {message}', file=sys.stderr)
    sys.exit(1)


def load_config():
    if not CONFIG_PATH.exists():
        die(f'missing config: {CONFIG_PATH}')
    with CONFIG_PATH.open() as handle:
        config = json.load(handle)
    missing = [key for key in ('pat', 'organization', 'project') if not config.get(key)]
    if missing:
        die(f'missing config key(s): {", ".join(missing)}')
    return config


def extract_id(value):
    value = value.strip()
    if re.fullmatch(r'#?\d+', value):
        return value.lstrip('#')

    parsed = urllib.parse.urlparse(value)
    if parsed.scheme and parsed.netloc:
        match = re.search(r'/_workitems/edit/(\d+)', parsed.path)
        if match:
            return match.group(1)
        match = re.search(r'[?&]workitem=(\d+)', parsed.query, re.IGNORECASE)
        if match:
            return match.group(1)

    match = re.search(r'(?:PBI|bug|task|feature|user story|work item)?\s*#?(\d{3,})', value, re.IGNORECASE)
    if match:
        return match.group(1)

    die(f'could not find a work item ID in: {value}')


def auth_header(pat):
    token = base64.b64encode(f':{pat}'.encode()).decode()
    return f'Basic {token}'


def request_json(url, auth):
    request = urllib.request.Request(url, headers={'Authorization': auth, 'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(request) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        body = error.read().decode('utf-8', errors='replace')
        die(f'Azure DevOps HTTP {error.code} for {url}: {body[:500]}')


def download(url, auth, path):
    request = urllib.request.Request(url, headers={'Authorization': auth})
    try:
        with urllib.request.urlopen(request) as response:
            path.write_bytes(response.read())
            return response.headers.get_content_type()
    except urllib.error.HTTPError as error:
        print(f'warning: could not download {url}: HTTP {error.code}', file=sys.stderr)
        return None


def html_to_text(value):
    if not value:
        return ''
    parser = PlainTextParser()
    parser.feed(str(value))
    return parser.text()


def first_field(fields, *names):
    for name in names:
        value = fields.get(name)
        if value:
            return value
    return None


def person(value):
    if isinstance(value, dict):
        return value.get('displayName') or value.get('uniqueName') or ''
    return value or ''


def collect_embedded_urls(*html_values):
    urls = []
    seen = set()
    pattern = re.compile(r'https://dev\.azure\.com/[^"\'<>\s]+?(?:attachments|_apis/wit/attachments)/[^"\'<>\s]+', re.I)
    for value in html_values:
        for match in pattern.findall(str(value or '')):
            url = html.unescape(match)
            if url not in seen:
                seen.add(url)
                urls.append(url)
    return urls


def extension_for(content_type, url):
    parsed_name = Path(urllib.parse.urlparse(url).path).name
    suffix = Path(parsed_name).suffix
    if suffix:
        return suffix
    guessed = mimetypes.guess_extension(content_type or '')
    return guessed or '.bin'


def safe_filename(value):
    value = re.sub(r'[^A-Za-z0-9._-]+', '-', value).strip('-')
    return value[:120] or 'attachment'


def download_attachments(work_item, comments, auth, out_dir):
    attachments_dir = out_dir / 'attachments'
    attachments_dir.mkdir(parents=True, exist_ok=True)
    downloads = []
    seen = set()

    def add_download(url, label):
        if not url or url in seen:
            return
        seen.add(url)
        index = len(downloads) + 1
        content_type = download(url, auth, attachments_dir / f'.probe-{index}')
        probe = attachments_dir / f'.probe-{index}'
        ext = extension_for(content_type, url)
        path = attachments_dir / f'{index:02d}-{safe_filename(label)}{ext}'
        if probe.exists():
            probe.rename(path)
            downloads.append({'url': url, 'path': str(path), 'contentType': content_type or 'unknown'})

    for relation in work_item.get('relations') or []:
        if relation.get('rel') == 'AttachedFile':
            attrs = relation.get('attributes') or {}
            label = attrs.get('name') or relation.get('url', '').split('/')[-1] or 'attachment'
            add_download(relation.get('url'), label)

    fields = work_item.get('fields') or {}
    html_fields = [
        fields.get('System.Description'),
        fields.get('Microsoft.VSTS.Common.AcceptanceCriteria'),
        fields.get('Microsoft.VSTS.TCM.ReproSteps'),
        fields.get('Microsoft.VSTS.TCM.SystemInfo'),
    ]
    html_fields.extend(comment.get('text') for comment in comments.get('comments') or [])

    for index, url in enumerate(collect_embedded_urls(*html_fields), start=1):
        add_download(url, f'embedded-{index}')

    return downloads


def format_section(title, text):
    if not text:
        return ''
    return f'\n## {title}\n{text.strip()}\n'


def markdown_summary(work_item, comments, downloads):
    fields = work_item.get('fields') or {}
    work_type = fields.get('System.WorkItemType') or 'Work Item'
    title = fields.get('System.Title') or '(untitled)'
    state = fields.get('System.State') or ''
    assigned = person(fields.get('System.AssignedTo')) or 'Unassigned'
    priority = fields.get('Microsoft.VSTS.Common.Priority') or ''
    tags = fields.get('System.Tags') or ''
    area = fields.get('System.AreaPath') or ''
    iteration = fields.get('System.IterationPath') or ''

    parts = [f'# {work_type} #{work_item.get("id")}: {title}', '']
    meta = [f'**State:** {state}', f'**Assigned:** {assigned}']
    if priority:
        meta.append(f'**Priority:** {priority}')
    parts.append(' | '.join(meta))

    description = html_to_text(fields.get('System.Description'))
    acceptance = html_to_text(fields.get('Microsoft.VSTS.Common.AcceptanceCriteria'))
    repro = html_to_text(first_field(fields, 'Microsoft.VSTS.TCM.ReproSteps', 'Microsoft.VSTS.TCM.SystemInfo'))

    for heading, text in (('Description', description), ('Acceptance Criteria', acceptance), ('Repro/System Info', repro)):
        section = format_section(heading, text)
        if section:
            parts.append(section.rstrip())

    if downloads:
        parts.append('\n## Images and Attachments')
        for item in downloads:
            parts.append(f'- `{item["path"]}` ({item["contentType"]})')

    comment_items = comments.get('comments') or []
    if comment_items:
        parts.append('\n## Comments')
        for comment in comment_items:
            author = person(comment.get('createdBy')) or 'Unknown'
            date = comment.get('createdDate') or ''
            text = html_to_text(comment.get('text'))
            parts.append(f'\n### {author} - {date}\n{text or "(empty)"}')

    footer = []
    if tags:
        footer.append(f'Tags: {tags}')
    if area or iteration:
        footer.append(f'Area: {area} | Iteration: {iteration}')
    if footer:
        parts.append('\n---')
        parts.extend(footer)

    return '\n'.join(parts).strip() + '\n'


def main():
    parser = argparse.ArgumentParser(description='Fetch an Azure DevOps work item with comments and attachments.')
    parser.add_argument('work_item', help='Work item ID, #ID, or Azure DevOps URL')
    parser.add_argument('--out-root', default=str(OUT_ROOT), help='Output root directory')
    args = parser.parse_args()

    config = load_config()
    work_id = extract_id(args.work_item)
    auth = auth_header(config['pat'])
    org = urllib.parse.quote(config['organization'], safe='')
    project = urllib.parse.quote(config['project'], safe='')
    out_dir = Path(args.out_root) / work_id
    out_dir.mkdir(parents=True, exist_ok=True)

    base = f'https://dev.azure.com/{org}/{project}/_apis/wit/workitems/{work_id}'
    work_item_url = f'{base}?api-version={API_VERSION}&$expand=All'
    comments_url = f'{base}/comments?api-version={COMMENTS_API_VERSION}'

    work_item = request_json(work_item_url, auth)
    comments = request_json(comments_url, auth)

    (out_dir / 'workitem.json').write_text(json.dumps(work_item, indent=2), encoding='utf-8')
    (out_dir / 'comments.json').write_text(json.dumps(comments, indent=2), encoding='utf-8')

    downloads = download_attachments(work_item, comments, auth, out_dir)
    summary = markdown_summary(work_item, comments, downloads)
    (out_dir / 'summary.md').write_text(summary, encoding='utf-8')

    print(summary)
    print(f'\nSaved raw files to: {out_dir}', file=sys.stderr)


if __name__ == '__main__':
    main()
