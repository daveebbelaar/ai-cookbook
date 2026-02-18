# دوره تصادف MCP برای توسعه دهندگان پایتون

پروتکل زمینه Model (MCP) یک چارچوب قدرتمند است که با ارائه یک روش استاندارد برای اتصال مدل ها با منابع و ابزارهای داده خارجی ، توسعه دهندگان را قادر می سازد تا برنامه های AI را با مدل های بزرگ زبان (LLMS) بسازند.این دوره تصادف شما را از طریق اصول MCP ، از درک مفاهیم اصلی آن گرفته تا اجرای سرورها و مشتریانی که از آنها استفاده می کنند ، منابع و ابزارهای خود را راهنمایی می کنند.

## فهرست مطالب

1.
2. [درک MCP] (./ 2-درک-mcp/readme.md)
3. [تنظیم سرور ساده با Python SDK] (.
4.
5.
6. [در حال اجرا با Docker] (./ 6-run-with-docker/readme.md)
7. [مدیریت چرخه عمر] (.

## تنظیم محیط توسعه خود

بیایید با تنظیم محیط خود شروع کنیم.MCP Python SDK هر آنچه را که برای ساختن سرور و مشتری نیاز داریم فراهم می کند.

`` `bash
# با استفاده از UV (توصیه شده)
UV PIP نصب -r الزامات .txt

# یا استفاده از PIP
pip install -r نیاز. txt
`` `

ابزارهای MCP CLI ابزارهای مفیدی را برای توسعه و آزمایش ارائه می دهند:

`` `bash
# سرور را با بازرس MCP تست کنید
MCP Dev Server.py

# سرور را در دسک تاپ کلود نصب کنید
MCP Server.py را نصب کنید

# مستقیماً سرور را اجرا کنید
mcp run server.py
`` `

## منابع و مراحل بعدی

منابع اصلی برای تعمیق دانش MCP شما:

- [مستندات پروتکل زمینه مدل] (https://modelContextProtocol.io)
- [مشخصات پروتکل متن مدل] (https://spec.modelContextProtocol.io)
- [مخزن Python SDK Github] (https://github.com/modelContextProtocol/python-sdk)
- [سرورهای رسمی پشتیبانی شده] (https://github.com/modelcontextprotocol/servers)
- [معماری هسته MCP] (https://modelContextProtocol.io/docs/concepts/architecture)