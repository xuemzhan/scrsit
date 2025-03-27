# 插件要点说明

**依赖检查:** 在 __init__ 中检查 magic_pdf 是否已安装。

**配置:** 使用 Pydantic 模型 PdfParserConfig 来管理和验证配置。

**异步:** aparse 是核心的异步解析方法。同步 parse 方法通过 asyncio.run 或类似方式包装 aparse（请注意在库代码中使用 asyncio.run 可能有副作用，更好的方式是让调用者管理事件循环）。

**临时文件:** _ensure_pdf_path 负责处理输入，如果输入是内存数据（bytes 或 IO），则创建临时文件供 magic_pdf 使用，并在结束后清理。

**重试:** 使用 tenacity 对 magic_pdf.process 调用进行封装，实现自动重试。

**异步执行同步代码:** 使用 asyncio.to_thread 在独立的线程中运行阻塞的 magic_pdf.process，避免阻塞主事件循环。

**分页处理与进度:**
- 如果能用 pypdf 获取总页数，则根据 page_batch_size 分批调用 magic_pdf。
- 在每批处理后记录进度日志。

**结果映射:** _map_result_to_document 负责将 magic_pdf 返回的（可能分批的）结果字典聚合，并填充到 Document 对象的各个字段（文本内容、图片、表格等）。这部分需要根据 magic_pdf 确切的输出格式进行详细调整。

**错误处理:** 在关键步骤（文件操作、magic_pdf调用、结果映射）使用 try...except 捕获异常，记录详细日志，并最终抛出 ParsingError。

**日志:** 在整个流程中添加了详细的 debug, info, warning, error 日志记录。

**断点续处理:** 这个实现不包含真正的断点续处理。它通过重试来提高单次运行的成功率。实现断点续处理需要将中间状态（例如已处理的页面批次、部分结果）持久化存储，并在下次运行时加载，这会显著增加复杂性。

请务必根据您使用的 MinerU/magic_pdf 库的确切版本和其 process 函数的输入输出规范，仔细调整 _call_magic_pdf_with_retry 中的参数传递和 _map_result_to_document 中的结果解析逻辑。