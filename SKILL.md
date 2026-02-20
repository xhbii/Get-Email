# Email to Markdown Converter

## 元数据
---
name: email-to-markdown
description: 当用户需要获取指定邮箱（如Gmail）的邮件完整内容（包括邮件正文和附件）并保存为Markdown格式时使用。使用 imaplib + mailparser + BeautifulSoup 实现。

## 触发条件
---
### 适用场景 (When to use)
- 用户明确要求获取指定邮箱的邮件并保存为Markdown格式
- 需要导出邮件内容用于文档整理、备份或分享
- 需处理包含附件的邮件并将其保存到本地

### 不适用场景 (When NOT to use)
- 用户仅需要查看邮件列表而不需要导出内容
- 需要对邮件进行复杂的邮件服务器管理操作
- 要求导出为非Markdown格式的文档

## 输入输出结构
---
### 输入 (Input)
```python
config = {
    'emailProvider': 'gmail',        # 邮箱提供商，目前支持 gmail
    'emailAddress': 'user@example.com',  # 邮箱地址
    'emailPassword': 'securepassword',  # 邮箱密码或应用专用密码
    'imapServer': 'imap.gmail.com',   # IMAP服务器地址
    'imapPort': 993,                  # IMAP端口，默认993（SSL加密）
    'folder': 'INBOX',                # 邮箱文件夹，默认收件箱
    'searchCriteria': 'ALL',          # 搜索条件，默认获取所有邮件
    'savePath': './emails',           # 保存路径，默认当前目录下的emails文件夹
    'maxEmails': 8                    # 最多处理邮件数量，默认8封
}
```

### 输出 (Output)
程序直接在控制台输出处理结果，无返回值。

```
=== 邮件获取与转换工具 ===
已有邮件文件数量: 8
正在连接到 gmail 邮箱服务器...
登录成功
当前文件夹: INBOX
正在搜索邮件 (最多 8 封)...
找到 8 封邮件待处理
正在处理邮件...
邮件已存在，跳过: xxx.md

=== 处理完成 ===
```

## 文件结构
---
```
get_email/
├── get_email.py           # 主程序脚本
├── emails/                # 邮件保存目录
│   ├── 20260214_xxx_主题1.md
│   ├── 20260214_xxx_主题1/
│   │   └── 附件文件
│   └── 20260215_xxx_主题2.md
└── temp_email.eml         # 临时邮件文件（处理后自动删除）
```

## 邮件内容Markdown格式
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

## 核心函数
---

### decode_str(s)
解码邮件头字符串。

**参数**:
- `s` (str): 需要解码的字符串

**返回**:
- `str`: 解码后的字符串

---

### html_to_markdown(html_content)
将HTML内容转换为Markdown格式。

**参数**:
- `html_content` (str): HTML内容

**返回**:
- `str`: Markdown格式内容

**转换规则**:
- h1 → `# 标题`
- h2 → `## 标题`
- h3 → `### 标题`
- ul/ol → 无序/有序列表
- a → `[文本](链接)`
- img → `![alt](src)`
- 移除 script 和 style 标签

---

### parse_email_with_mailparser(email_path)
使用 mail-parser 解析邮件文件。

**参数**:
- `email_path` (str): 邮件文件路径

**返回**:
- `mailparser.parse_from_file` 返回的邮件对象

---

### save_email_as_markdown(email_path, output_dir)
将邮件保存为Markdown文件。

**参数**:
- `email_path` (str): 原始邮件文件路径
- `output_dir` (str): 输出目录

**返回**:
- `str` or `None`: 保存的文件路径，失败返回 None

**处理流程**:
1. 使用 mail-parser 解析邮件
2. 生成文件名：`{时间戳}_{主题}.md`
3. 构建 Markdown 内容
4. 保存附件到同名文件夹

---

### main()
主函数，执行完整的邮件获取和转换流程。

**处理流程**:
1. 创建保存目录
2. 检查已存在的邮件文件
3. 连接到 IMAP 服务器
4. 登录邮箱
5. 选择邮箱文件夹
6. 搜索邮件
7. 逐个处理邮件并保存为 Markdown
8. 断开连接

## 去重机制
---
程序通过检查 `emails` 文件夹中已存在的 `.md` 文件来判断邮件是否已处理，避免重复下载。

```python
existing_files = set(f for f in os.listdir(config['savePath']) if f.endswith('.md'))
```

## 附件处理
---
- 支持多种附件类型
- 附件保存到与 Markdown 文件同名的文件夹中
- 自动处理 Base64 编码的附件

## 失败处理
---
- 连接失败：打印错误信息并退出
- 解析失败：打印错误信息，跳过该邮件继续处理
- 保存失败：打印错误信息，继续处理其他邮件

## 安全注意事项
---
- 密码以明文形式存储在配置中
- Gmail 需要使用应用专用密码（App Password）
- 建议使用环境变量或密钥管理服务存储密码

## 依赖
---
- imaplib (Python 标准库)
- mailparser
- beautifulsoup4

---
**版本**: 1.1
**最后更新**: 2026-02-20
