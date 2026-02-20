# Email to Markdown API 参考

## 概述
---
这是一个用于从邮箱获取邮件内容并转换为 Markdown 格式的 Python 脚本。使用 `imaplib` 连接邮件服务器，`mailparser` 解析邮件，`BeautifulSoup` 转换 HTML 到 Markdown。

## 使用方式
---

### 基本使用
```bash
python3 get_email.py
```

### 配置
编辑 `get_email.py` 中的 `config` 字典：

```python
config = {
    'emailProvider': 'gmail',
    'emailAddress': 'your.email@gmail.com',
    'emailPassword': 'your_app_password',  # Gmail 需要应用专用密码
    'imapServer': 'imap.gmail.com',
    'imapPort': 993,
    'folder': 'INBOX',
    'searchCriteria': 'ALL',
    'savePath': './emails',
    'maxEmails': 8
}
```

## 配置参数说明
---

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `emailProvider` | str | `'gmail'` | 邮箱提供商 |
| `emailAddress` | str | 必填 | 邮箱地址 |
| `emailPassword` | str | 必填 | 邮箱密码或应用专用密码 |
| `imapServer` | str | `'imap.gmail.com'` | IMAP 服务器地址 |
| `imapPort` | int | `993` | IMAP 端口（SSL） |
| `folder` | str | `'INBOX'` | 邮箱文件夹 |
| `searchCriteria` | str | `'ALL'` | 搜索条件 |
| `savePath` | str | `'./emails'` | 保存路径 |
| `maxEmails` | int | `8` | 最多处理邮件数量 |
| `filterMode` | str | `'none'` | 过滤模式: none/whitelist/blacklist |
| `filterList` | list | `[]` | 过滤关键词列表 |

## 函数参考
---

### decode_str(s)

解码邮件头字符串，支持多种字符编码。

**参数**:
- `s` (str): 需要解码的字符串

**返回**:
- `str`: 解码后的字符串

**示例**:
```python
decoded = decode_str("=?UTF-8?B?5Y+w5Zu+?=")
```

---

### html_to_markdown(html_content)

将 HTML 内容转换为 Markdown 格式。

**参数**:
- `html_content` (str): HTML 内容字符串

**返回**:
- `str`: Markdown 格式内容

**转换规则**:
| HTML 元素 | Markdown 格式 |
|-----------|---------------|
| `<h1>` | `# 标题` |
| `<h2>` | `## 标题` |
| `<h3>` | `### 标题` |
| `<ul>/<li>` | `- 列表项` |
| `<ol>/<li>` | `1. 列表项` |
| `<a href="...">` | `[文本](链接)` |
| `<img src="...">` | `![alt](src)` |
| `<script>`/`<style>` | 移除 |

**示例**:
```python
html = "<h1>Hello</h1><p>World</p>"
markdown = html_to_markdown(html)
# 输出: "# Hello\n\nWorld"
```

---

### parse_email_with_mailparser(email_path)

使用 mail-parser 解析邮件文件。

**参数**:
- `email_path` (str): .eml 邮件文件路径

**返回**:
- `mailparser.parsed邮件对象` 或 `None`: 解析成功返回邮件对象，失败返回 None

**邮件对象属性**:
- `subject`: 邮件主题
- `from_`: 发件人信息列表
- `to`: 收件人信息列表
- `date`: 发送时间
- `text_plain`: 纯文本正文列表
- `text_html`: HTML 正文列表
- `attachments`: 附件列表

**示例**:
```python
msg = parse_email_with_mailparser('temp_email.eml')
if msg:
    print(msg.subject)
    print(msg.from_)
```

---

### save_email_as_markdown(email_path, output_dir)

将邮件保存为 Markdown 文件。

**参数**:
- `email_path` (str): 原始邮件文件路径 (.eml)
- `output_dir` (str): 输出目录

**返回**:
- `str` or `None`: 成功返回保存的文件路径，失败返回 None

**处理流程**:
1. 使用 mail-parser 解析邮件
2. 生成文件名：`{时间戳}_{安全主题}.md`
3. 构建 Markdown 内容
4. 保存附件到同名文件夹

**文件名生成规则**:
```python
timestamp = msg.date.strftime('%Y%m%d_%H%M%S')  # 或当前时间
safe_subject = re.sub(r'[\\/*?:"<>|]', '_', subject)
filename = f"{timestamp}_{safe_subject}.md"
```

**示例**:
```python
output_path = save_email_as_markdown('temp_email.eml', './emails')
if output_path:
    print(f"已保存到: {output_path}")
```

---

### main()

主函数，执行完整的邮件获取和转换流程。

**处理流程**:
1. 创建保存目录 (`os.makedirs`)
2. 检查已存在的邮件文件（用于去重）
3. 使用 IMAP SSL 连接到服务器
4. 登录邮箱
5. 选择邮箱文件夹
6. 根据搜索条件搜索邮件
7. 逐个处理邮件：
   - 获取邮件内容 (RFC822)
   - 临时保存为 .eml 文件
   - 解析并转换为 Markdown
   - 检查是否已存在
   - 保存到文件
   - 清理临时文件
8. 断开与服务器的连接

**返回值**: 无（直接在控制台输出）

**示例**:
```python
if __name__ == "__main__":
    main()
```

## 搜索条件
---

支持 IMAP 标准搜索条件：

| 条件 | 说明 | 示例 |
|------|------|------|
| `ALL` | 所有邮件 | `'ALL'` |
| `UNSEEN` | 未读邮件 | `'UNSEEN'` |
| `SEEN` | 已读邮件 | `'SEEN'` |
| `SINCE` | 指定日期之后 | `'SINCE "01-Feb-2026"'` |
| `BEFORE` | 指定日期之前 | `'BEFORE "28-Feb-2026"'` |
| `FROM` | 指定发件人 | `'FROM "sender@example.com"'` |
| `SUBJECT` | 主题包含关键词 | `'SUBJECT "meeting"'` |

**组合示例**:
```python
# 2026年2月未读邮件
'SINCE "01-Feb-2026" UNSEEN'
```

## 去重机制
---

程序通过检查输出目录中已存在的 `.md` 文件来判断邮件是否已处理：

```python
existing_files = set(f for f in os.listdir(config['savePath']) if f.endswith('.md'))

if filename in existing_files:
    print(f"Email already exists, skip: {filename}")
```

## 过滤机制

支持白名单和黑名单过滤模式，基于发件人和主题匹配关键词。

```python
config = {
    'filterMode': 'blacklist',  # none/whitelist/blacklist
    'filterList': ['JPM', 'Jefferies']  # keywords
}
```

| Mode | Behavior |
|------|----------|
| `none` | Process all emails |
| `whitelist` | Only process emails containing keywords |
| `blacklist` | Skip emails containing keywords |

**Matching**: Case-insensitive, matches against sender email and subject line.

## 附件处理
---

**保存位置**: 与 Markdown 文件同名的文件夹中

```
emails/
├── 20260218_xxx_主题.md
└── 20260218_xxx_主题/
    ├── 附件1.pdf
    └── 附件2.png
```

**支持格式**:
- 自动检测 Base64 编码并解码
- 支持 bytes 和 str 类型的 payload
- 失败时跳过该附件，继续处理

## 错误处理
---

| 错误类型 | 处理方式 |
|----------|----------|
| 连接失败 | 打印错误信息，程序退出 |
| 认证失败 | 打印错误信息，程序退出 |
| 解析失败 | 打印错误信息，跳过该邮件 |
| 保存失败 | 打印错误信息，跳过该邮件 |
| 附件保存失败 | 打印错误信息，继续处理 |

## Gmail 配置
---

1. 启用 IMAP 访问：
   - 设置 → 查看所有设置 → 转发和 POP/IMAP → 启用 IMAP

2. 生成应用专用密码：
   - Google 账户 → 安全 → 两步验证 → 应用专用密码
   - 生成新密码，替换配置中的 `emailPassword`

## 依赖安装
---

```bash
pip install mailparser beautifulsoup4
```

## 输出目录结构
---

```
get_email/
├── get_email.py                    # 主程序
├── emails/                         # 邮件保存目录
│   ├── 20260214_xxx_主题1.md
│   ├── 20260214_xxx_主题1/         # 附件目录
│   │   └── 附件文件
│   ├── 20260215_xxx_主题2.md
│   └── 20260215_xxx_主题2/
│       └── 附件文件
└── temp_email.eml                  # 临时文件（处理后自动删除）
```

## Markdown 输出格式
---

```markdown
# 邮件主题

## 发件人信息
- **发件人**: 发件人姓名 (email@example.com)
- **收件人**: 收件人1, 收件人2
- **发送时间**: 2026-02-18 10:27:28+00:00

## 邮件正文

邮件正文内容...

## 附件
- [附件文件名](附件目录/附件文件名)
```

---
**版本**: 1.2
**最后更新**: 2026-02-20
