"""Real Claude CLI JSON responses for testing"""

SIMPLE_TEXT = [
    '{"type":"assistant","message":{"content":[{"type":"text","text":"Hello"}]},"session_id":"df83d374-79dd-4100-be18-fd7e4bccc33b","uuid":"408d2155-b3f8-4044-a00e-cedd765d3eaa"}',
]

TOOL_USE_SEQUENCE = [
    '{"type":"assistant","message":{"content":[{"type":"text","text":"Let me check that file"}]},"session_id":"df83d374-79dd-4100-be18-fd7e4bccc33b","uuid":"408d2155-b3f8-4044-a00e-cedd765d3eaa"}',
    '{"type":"assistant","message":{"content":[{"type":"tool_use","id":"toolu_123","name":"Read","input":{"file_path":"test.py"}}]},"session_id":"df83d374-79dd-4100-be18-fd7e4bccc33b","uuid":"78f33550-6bd1-4fa4-98a3-94257f97bf7d"}',
    '{"type":"user","message":{"role":"user","content":[{"type":"tool_result","content":"file contents here","is_error":false,"tool_use_id":"toolu_123"}]},"session_id":"df83d374-79dd-4100-be18-fd7e4bccc33b","uuid":"1b9893ae-1fbd-4b73-88b2-0e7a4b5d215c","tool_use_result":{"stdout":"file contents here","stderr":"","interrupted":false}}',
    '{"type":"assistant","message":{"content":[{"type":"text","text":"I see the file contains..."}]},"session_id":"df83d374-79dd-4100-be18-fd7e4bccc33b","uuid":"408d2155-b3f8-4044-a00e-cedd765d3eaa"}',
]

ERROR_RESPONSE = [
    '{"type":"user","message":{"role":"user","content":[{"type":"tool_result","content":"<tool_use_error>File does not exist.</tool_use_error>","is_error":true,"tool_use_id":"toolu_123"}]},"session_id":"df83d374-79dd-4100-be18-fd7e4bccc33b","uuid":"1b9893ae-1fbd-4b73-88b2-0e7a4b5d215c","tool_use_result":"Error: File does not exist."}',
]
