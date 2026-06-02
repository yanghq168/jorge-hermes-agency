When creating new backup repositories or similar infrastructure, user prefers creating NEW repositories rather than reusing or modifying existing ones. Example: when migrating from OpenClaw to Hermes, user explicitly requested new repos `jorge-hermes-skills` and `jorge-hermes-agency` instead of using the existing `jorge-ai-repository`. Always ask before modifying existing user-created resources.
§
User expects HTML-styled emails for content platforms (小红书, 公众号). Plain text emails are unacceptable — they complained "没有UI" and I upgraded both scripts to HTML with proper styling (渐变色头部, 卡片布局, 标签云). Future content scripts must use HTML templates, not plain text.
§
Assistant has elevated access to user's infrastructure: SSH access to Tencent Cloud server (82.156.225.39, user ai-worker, passwordless sudo), GitHub account (yanghq168), and QQ email (569545015@qq.com via SMTP). This means assistant can execute commands on the remote server, push/pull GitHub repos, and send emails programmatically.
§
Content script 敏感词规范：极端情绪词需替换 — "拉黑"→"屏蔽"，"逼"→"让"，"滚"→"走"。用户明确要求所有脚本遵循，core-research-v1.md 已固化此规范。
§
GitHub账号下无aivideo仓库 — yanghq168/aivideo 不存在，搜索0结果。之前的aivideo部署用的是本地备份（aivideo.bak）而非从GitHub拉取。当前网站已从备份恢复。
§
远程服务器SSH key `jorge_server` 不在GitHub账号的SSH Keys里，git clone git@github.com 会 Host key verification failed。需要token-based HTTPS方式或用户自己在GitHub添加该公钥。
§
用户对内容平台内容的偏好已固化到 content-platforms skill：①B方案（中性词）②推送时间差异化③每日一次。
§
品牌矩阵（已更新）：
- 小红书："权权的HERMES"（新品牌，已替换旧品牌"权权养的虾"）
- 头条号："围炉家常话"
- 微信/抖音："权权管家"
- 通用发件人格式：权权的HERMES（平台名）
- 邮件接收：569545015@qq.com

内容规范：
- 敏感词替换：极端情绪词需中性化（拉黑→屏蔽，逼→让，滚→走）
- 邮件格式：必须为HTML样式，不可纯文本
- 推送频率：每日一次/平台
- 推送时间需差异化（避免多平台同时推送）
§
抖音热搜选题采集任务已部署：每天17:00自动抓取抖音热搜榜TOP 50，按生活情感/职场搞钱/轻科普三类分类，生成趋势分析和选题建议，直接推送到Lark对话（不发邮件）。脚本路径：~/.hermes/cron/scripts/douyin-hotsearch-daily.py，任务ID：42fe9944998e。
§
内容平台矩阵推送时间汇总（已固化）：
- 07:00 公众号「围炉家常话」（邮件+Lark）
- 17:00 抖音热搜选题（Lark消息）
- 20:30 头条号「围炉家常话」（邮件+Lark）
- 21:30 小红书旅游攻略（邮件+Lark）
所有任务使用品牌名「权权的HERMES」，旧品牌「权权养的虾」已废弃。
§
内容复制格式验证：飞书复制格式会丢，但邮件客户端（QQ邮箱）直接复制内容粘贴到公众号，格式能保留。用户使用此方式发布内容。
§
用户无法从飞书对话框复制格式——粘贴后格式丢失。解决方案：MD文件必须作为附件发送（MEDIA:路径），不能直接粘贴在对话框里。发送公众号文章等MD内容时，一律用 send_message + MEDIA:file.md 方式，用户再下载到本地复制到公众号后台。