import json
import httpx
import re
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from app.config import settings


class AIService(ABC):
    @abstractmethod
    async def generate_outline(self, description: str, page_count: Optional[int] = None) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def expand_content(self, outline: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def parse_document(self, content: str) -> Dict[str, Any]:
        pass

    def _parse_outline_text(self, text: str) -> Dict[str, Any]:
        pages = []
        lines = text.strip().split('\n')
        current_page = None
        ppt_title = "演示文稿"
        
        for i, line in enumerate(lines[:30]):
            line_stripped = line.strip()
            if 'PPT标题' in line_stripped or 'PPT 标题' in line_stripped:
                title_match = re.search(r'PPT\s*标题[:：]\s*(.+)', line_stripped)
                if title_match:
                    ppt_title = title_match.group(1).strip()
                    ppt_title = re.sub(r'^#+\s*', '', ppt_title).strip()
                    print(f"[DEBUG] Found PPT title: {ppt_title}")
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            if line_stripped.startswith('---') or line_stripped.startswith('___'):
                continue
            
            page_match = re.search(
                r'^(?:#+)?\s*第\s*(\d+)\s*页(?:[:：]\s*(.*))?$',
                line_stripped,
                re.IGNORECASE
            )
            
            if not page_match:
                page_match = re.search(
                    r'^(?:#+)?\s*Slide\s*(\d+)[:：\s]\s*(.*)$',
                    line_stripped,
                    re.IGNORECASE
                )
            
            if page_match:
                if current_page:
                    pages.append(current_page)
                
                title = page_match.group(2) or f"第{page_match.group(1)}页"
                title = title.strip()
                title = re.sub(r'^#+\s*', '', title).strip()
                
                current_page = {
                    "page_index": int(page_match.group(1)),
                    "title": title,
                    "content": [],
                    "layout_type": "single_column"
                }
                print(f"[DEBUG] Matched page: {current_page['page_index']} - {current_page['title']}")
            elif line_stripped.startswith('-') or line_stripped.startswith('•') or line_stripped.startswith('*'):
                if current_page:
                    content = line_stripped.lstrip('-•* ').strip()
                    content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
                    content = re.sub(r'\*\*', '', content)
                    if content:
                        current_page["content"].append(content)
            elif current_page:
                if not line_stripped.startswith('#') and len(line_stripped) > 2:
                    content = re.sub(r'\*\*(.*?)\*\*', r'\1', line_stripped)
                    content = re.sub(r'\*\*', '', content)
                    current_page["content"].append(content)
        
        if current_page:
            pages.append(current_page)
        
        print(f"[DEBUG] Total pages parsed: {len(pages)}")
        for p in pages:
            print(f"[DEBUG] Page {p['page_index']}: {p['title']} - {len(p['content'])} items")
        
        if not pages and text.strip():
            pages.append({
                "page_index": 1,
                "title": "文档内容",
                "content": [line for line in text.split('\n') if line.strip()][:20],
                "layout_type": "single_column"
            })
        
        return {
            "title": ppt_title,
            "pages": pages if pages else [{"page_index": 1, "title": "标题", "content": ["内容"], "layout_type": "single_column"}]
        }


class MockAIService(AIService):
    async def generate_outline(self, description: str, page_count: Optional[int] = None) -> Dict[str, Any]:
        pages = []
        count = page_count or 5
        
        page_templates = [
            {"title": "概述与背景", "content": [f"{description[:15]}的定义与起源", "发展历程与现状", "研究意义与价值"]},
            {"title": "核心概念", "content": ["基本概念解析", "关键术语说明", "核心原理介绍"]},
            {"title": "技术架构", "content": ["系统架构设计", "关键技术组件", "技术选型分析"]},
            {"title": "应用场景", "content": ["典型应用案例", "行业解决方案", "实际效果展示"]},
            {"title": "发展趋势", "content": ["当前挑战分析", "未来发展方向", "机遇与展望"]},
            {"title": "实施建议", "content": ["落地路径规划", "资源配置建议", "风险控制措施"]},
            {"title": "案例分析", "content": ["案例背景介绍", "实施过程详解", "成果与启示"]},
            {"title": "总结与展望", "content": ["核心要点回顾", "关键结论总结", "后续行动计划"]}
        ]
        
        for i in range(count):
            template = page_templates[i % len(page_templates)]
            pages.append({
                "page_index": i + 1,
                "title": template["title"],
                "content": template["content"],
                "layout_type": "single_column"
            })
        
        return {
            "title": f"关于{description[:20]}的演示",
            "pages": pages
        }
    
    async def expand_content(self, outline: Dict[str, Any]) -> Dict[str, Any]:
        pages = outline.get("pages", [])
        for i, page in enumerate(pages):
            if i == 2:
                page["charts"] = [{
                    "type": "bar",
                    "title": "发展趋势分析",
                    "data": {
                        "categories": ["2020", "2021", "2022", "2023", "2024"],
                        "series": [{"name": "增长率", "values": [15, 25, 35, 45, 55]}]
                    }
                }]
            elif i == 3:
                page["tables"] = [{
                    "title": "关键指标对比",
                    "headers": ["指标", "当前值", "目标值", "状态"],
                    "rows": [
                        ["用户增长", "120%", "100%", "达标"],
                        ["收入增长", "85%", "90%", "接近"],
                        ["满意度", "92%", "95%", "良好"]
                    ]
                }]
        return outline
    
    async def parse_document(self, content: str) -> Dict[str, Any]:
        parsed = self._parse_outline_text(content)
        print(f"[MockAIService] Parsed {len(parsed['pages'])} pages from document")
        return parsed


class QwenService(AIService):
    def __init__(self):
        self.api_key = settings.DASHSCOPE_API_KEY
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        self.model = "qwen-turbo"
    
    async def _call_api(self, prompt: str) -> str:
        if not self.api_key:
            raise ValueError("DashScope API Key未配置")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "input": {
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            "parameters": {
                "result_format": "text",
                "temperature": 0.7,
                "max_tokens": 1500
            }
        }
        
        try:
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    async with httpx.AsyncClient(timeout=120.0) as client:
                        response = await client.post(
                            self.base_url,
                            headers=headers,
                            json=payload
                        )
                        response.raise_for_status()
                        result = response.json()
                        if "output" in result and "text" in result["output"]:
                            return result["output"]["text"]
                        elif "message" in result:
                            raise ValueError(f"API Error: {result['message']}")
                        else:
                            raise ValueError(f"Unexpected API response: {result}")
                except (httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError) as e:
                    if attempt < max_retries - 1:
                        print(f"[QwenService] Retry {attempt + 1}/{max_retries} after error: {e}")
                        import asyncio
                        await asyncio.sleep(2)
                        continue
                    raise
        except httpx.HTTPStatusError as e:
            print(f"[QwenService] HTTP error: {e.response.text}")
            raise ValueError(f"AI服务请求失败: {e.response.status_code}")
        except Exception as e:
            print(f"[QwenService] Request error: {e}")
            raise ValueError(f"AI服务请求异常: {str(e)}")
    
    async def generate_outline(self, description: str, page_count: Optional[int] = None) -> Dict[str, Any]:
        page_hint = f"，建议{page_count}页" if page_count else ""
        prompt = f"""请根据以下描述生成PPT大纲，以JSON格式返回。

描述：{description}

要求：
1. 生成一个完整的PPT大纲{page_hint}
2. 每页包含标题和要点
3. 返回格式如下：
{{
    "title": "PPT标题",
    "pages": [
        {{
            "page_index": 1,
            "title": "页面标题",
            "content": ["要点1", "要点2", "要点3"],
            "layout_type": "single_column"
        }}
    ]
}}

请直接返回JSON，不要添加其他说明文字。"""

        try:
            result = await self._call_api(prompt)
            result = result.replace("```json", "").replace("```", "").strip()
            return json.loads(result)
        except json.JSONDecodeError:
            return self._parse_outline_text(result)
    
    async def expand_content(self, outline: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[QwenService] expand_content called with {len(outline.get('pages', []))} pages")
        
        pages_hint = ""
        for i, page in enumerate(outline.get('pages', [])):
            if page.get('content'):
                pages_hint += f"\n第{i+1}页 '{page.get('title', '')}': {', '.join(page.get('content', [])[:3])}"
        
        prompt = f"""请根据以下PPT大纲，为每页生成详细内容，以JSON格式返回。

大纲：
{json.dumps(outline, ensure_ascii=False, indent=2)}

要求：
1. 为每页的要点扩展详细描述，保留在 content 数组中。
2. **必须为至少2-3页添加图表或表格**：
   - 分析内容中的数据、趋势、对比等信息
   - 为包含数据对比、趋势分析的页面生成 `charts` 字段
   - 为包含多维度参数对比、清单的页面生成 `tables` 字段
3. **图表(charts)格式**：
   ```json
   "charts": [
     {{
       "type": "bar",
       "title": "图表标题",
       "data": {{
         "categories": ["类别1", "类别2", "类别3"],
         "series": [
           {{"name": "系列1", "values": [10, 20, 30]}}
         ]
       }}
     }}
   ]
   ```
4. **表格(tables)格式**：
   ```json
   "tables": [
     {{
       "title": "表格标题",
       "headers": ["列1", "列2", "列3"],
       "rows": [
         ["行1数据1", "行1数据2", "行1数据3"],
         ["行2数据1", "行2数据2", "行2数据3"]
       ]
     }}
   ]
   ```
5. 保持JSON格式不变，返回完整的JSON。不要添加 ```json 或其他标记。

**重要提示**：即使原始内容没有明确的数据，也请根据主题内容创造性地生成相关的图表或表格数据，使PPT更加丰富和专业。

请直接返回JSON。"""

        try:
            result = await self._call_api(prompt)
            result = result.replace("```json", "").replace("```", "").strip()
            print(f"[QwenService] expand_content raw result (first 500 chars): {result[:500]}...")
            parsed = json.loads(result)
            
            has_charts_or_tables = False
            for i, page in enumerate(parsed.get("pages", [])):
                charts = page.get("charts", [])
                tables = page.get("tables", [])
                if charts or tables:
                    has_charts_or_tables = True
                print(f"[QwenService] Page {i+1}: charts={len(charts)}, tables={len(tables)}")
            
            if not has_charts_or_tables and len(parsed.get("pages", [])) >= 2:
                print("[QwenService] No charts/tables found, generating based on content...")
                parsed = await self._generate_charts_from_content(parsed)
            
            return parsed
        except json.JSONDecodeError:
            print(f"[QwenService] JSON decode error. Raw result: {result[:200]}...")
            return await self._generate_charts_from_content(outline)
    
    async def _generate_charts_from_content(self, outline: Dict[str, Any]) -> Dict[str, Any]:
        pages = outline.get("pages", [])
        if len(pages) < 2:
            return outline
        
        pages_info = []
        for i, page in enumerate(pages):
            content_text = " ".join(page.get("content", []))
            pages_info.append(f"第{i+1}页 '{page.get('title', '')}': {content_text[:200]}")
        
        prompt = f"""请根据以下PPT各页面的内容，为合适的页面生成图表或表格数据。

PPT标题: {outline.get('title', '演示文稿')}

各页面内容:
{chr(10).join(pages_info)}

要求：
1. 分析每页内容，为包含数据、趋势、对比、列表等信息的页面生成图表或表格
2. 图表数据要与页面内容主题相关，数据要合理、真实感
3. 至少为2-3个页面生成图表或表格
4. 返回JSON格式，只包含需要添加图表/表格的页面信息：
{{
    "pages_with_charts": [
        {{
            "page_index": 2,
            "charts": [{{
                "type": "bar",
                "title": "与该页内容相关的图表标题",
                "data": {{
                    "categories": ["类别1", "类别2", "类别3"],
                    "series": [{{"name": "系列名", "values": [数值1, 数值2, 数值3]}}]
                }}
            }}]
        }},
        {{
            "page_index": 3,
            "tables": [{{
                "title": "与该页内容相关的表格标题",
                "headers": ["列1", "列2", "列3"],
                "rows": [["数据1", "数据2", "数据3"]]
            }}]
        }}
    ]
}}

请直接返回JSON，不要添加其他说明文字。"""

        try:
            result = await self._call_api(prompt)
            result = result.replace("```json", "").replace("```", "").strip()
            charts_data = json.loads(result)
            
            pages_with_charts = charts_data.get("pages_with_charts", [])
            for page_info in pages_with_charts:
                page_idx = page_info.get("page_index", 0) - 1
                if 0 <= page_idx < len(pages):
                    if "charts" in page_info:
                        pages[page_idx]["charts"] = page_info["charts"]
                    if "tables" in page_info:
                        pages[page_idx]["tables"] = page_info["tables"]
                    print(f"[QwenService] Added charts/tables to page {page_idx + 1}")
            
            return outline
        except Exception as e:
            print(f"[QwenService] Failed to generate charts from content: {e}")
            return self._add_default_charts_and_tables(outline)
    
    def _add_default_charts_and_tables(self, outline: Dict[str, Any]) -> Dict[str, Any]:
        pages = outline.get("pages", [])
        if len(pages) < 2:
            return outline
        
        for i, page in enumerate(pages):
            if i == 1:
                page["charts"] = [{
                    "type": "bar",
                    "title": "发展趋势分析",
                    "data": {
                        "categories": ["2020", "2021", "2022", "2023", "2024"],
                        "series": [{"name": "增长率", "values": [15, 25, 35, 45, 55]}]
                    }
                }]
            elif i == 2:
                page["tables"] = [{
                    "title": "关键指标对比",
                    "headers": ["指标", "当前值", "目标值", "状态"],
                    "rows": [
                        ["用户增长", "120%", "100%", "达标"],
                        ["收入增长", "85%", "90%", "接近"],
                        ["满意度", "92%", "95%", "良好"]
                    ]
                }]
            elif i == 3 and len(pages) > 4:
                page["charts"] = [{
                    "type": "pie",
                    "title": "市场份额分布",
                    "data": {
                        "categories": ["产品A", "产品B", "产品C", "其他"],
                        "series": [{"name": "份额", "values": [35, 30, 25, 10]}]
                    }
                }]
        
        print(f"[QwenService] Added default charts/tables to {min(3, len(pages))} pages")
        return outline
    
    async def parse_document(self, content: str) -> Dict[str, Any]:
        parsed = self._parse_outline_text(content)
        
        if len(parsed['pages']) >= 2:
            print(f"[QwenService] Local parsing successful: {len(parsed['pages'])} pages found")
            return parsed
        
        print("[QwenService] Local parsing failed, calling AI...")
        
        prompt = f"""请分析以下文档内容，生成PPT大纲，以JSON格式返回。

文档内容：
{content[:20000]}

要求：
1. **严格遵循文档结构**：文档中已经明确标记了每一页的内容（如"第1页"、"第2页"等），请直接解析这些页面结构，不要自行合并或重新摘要。
2. 提取每页的标题和要点。
3. 返回格式如下：
{{
    "title": "PPT标题",
    "pages": [
        {{
            "page_index": 1,
            "title": "页面标题",
            "content": ["要点1", "要点2", "要点3"],
            "layout_type": "single_column"
        }}
    ]
}}

**Example**:
文档:
#### 第1页：封面
- 标题：年度报告
- 汇报人：张三
#### 第2页：市场概况
- 市场规模增长20%

返回:
{{
    "title": "年度报告",
    "pages": [
        {{
            "page_index": 1,
            "title": "封面",
            "content": ["标题：年度报告", "汇报人：张三"],
            "layout_type": "single_column"
        }},
        {{
            "page_index": 2,
            "title": "市场概况",
            "content": ["市场规模增长20%"],
            "layout_type": "single_column"
        }}
    ]
}}

请直接返回JSON，不要添加其他说明文字。"""

        try:
            result = await self._call_api(prompt)
            result = result.replace("```json", "").replace("```", "").strip()
            parsed_json = json.loads(result)
            
            if not parsed_json.get("pages") or len(parsed_json["pages"]) == 0:
                print("[QwenService] AI returned empty pages, falling back to original content parsing")
                return self._parse_outline_text(content)
                
            return parsed_json
        except json.JSONDecodeError:
            print(f"[QwenService] JSON decode error in parse_document. Raw result: {result[:200]}...")
            print("[QwenService] Fallback to parsing original content")
            return self._parse_outline_text(content)


class KimiService(AIService):
    def __init__(self):
        self.api_key = settings.MOONSHOT_API_KEY
        self.base_url = "https://api.moonshot.cn/v1"
        self.model = "moonshot-v1-8k"
    
    async def _call_api(self, prompt: str) -> str:
        if not self.api_key:
            raise ValueError("Moonshot API Key未配置")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    async def generate_outline(self, description: str, page_count: Optional[int] = None) -> Dict[str, Any]:
        page_hint = f"，建议{page_count}页" if page_count else ""
        prompt = f"""请根据以下描述生成PPT大纲，以JSON格式返回。

描述：{description}

要求：
1. 生成一个完整的PPT大纲{page_hint}
2. 每页包含标题和要点
3. 返回格式如下：
{{
    "title": "PPT标题",
    "pages": [
        {{
            "page_index": 1,
            "title": "页面标题",
            "content": ["要点1", "要点2", "要点3"],
            "layout_type": "single_column"
        }}
    ]
}}

请直接返回JSON，不要添加其他说明文字。"""

        try:
            result = await self._call_api(prompt)
            result = result.replace("```json", "").replace("```", "").strip()
            return json.loads(result)
        except json.JSONDecodeError:
            return self._parse_outline_text(result)
    
    async def expand_content(self, outline: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[KimiService] expand_content called with {len(outline.get('pages', []))} pages")
        
        pages_hint = ""
        for i, page in enumerate(outline.get('pages', [])):
            if page.get('content'):
                pages_hint += f"\n第{i+1}页 '{page.get('title', '')}': {', '.join(page.get('content', [])[:3])}"
        
        prompt = f"""请根据以下PPT大纲，为每页生成详细内容，以JSON格式返回。

大纲：
{json.dumps(outline, ensure_ascii=False, indent=2)}

要求：
1. 为每页的要点扩展详细描述，保留在 content 数组中。
2. **必须为至少2-3页添加图表或表格**：
   - 分析内容中的数据、趋势、对比等信息
   - 为包含数据对比、趋势分析的页面生成 `charts` 字段
   - 为包含多维度参数对比、清单的页面生成 `tables` 字段
3. **图表(charts)格式**：
   ```json
   "charts": [
     {{
       "type": "bar",
       "title": "图表标题",
       "data": {{
         "categories": ["类别1", "类别2", "类别3"],
         "series": [
           {{"name": "系列1", "values": [10, 20, 30]}}
         ]
       }}
     }}
   ]
   ```
4. **表格(tables)格式**：
   ```json
   "tables": [
     {{
       "title": "表格标题",
       "headers": ["列1", "列2", "列3"],
       "rows": [
         ["行1数据1", "行1数据2", "行1数据3"],
         ["行2数据1", "行2数据2", "行2数据3"]
       ]
     }}
   ]
   ```
5. 保持JSON格式不变，返回完整的JSON。不要添加 ```json 或其他标记。

**重要提示**：即使原始内容没有明确的数据，也请根据主题内容创造性地生成相关的图表或表格数据，使PPT更加丰富和专业。

请直接返回JSON。"""

        try:
            result = await self._call_api(prompt)
            result = result.replace("```json", "").replace("```", "").strip()
            print(f"[KimiService] expand_content raw result (first 500 chars): {result[:500]}...")
            parsed = json.loads(result)
            
            has_charts_or_tables = False
            for i, page in enumerate(parsed.get("pages", [])):
                charts = page.get("charts", [])
                tables = page.get("tables", [])
                if charts or tables:
                    has_charts_or_tables = True
                print(f"[KimiService] Page {i+1}: charts={len(charts)}, tables={len(tables)}")
            
            if not has_charts_or_tables and len(parsed.get("pages", [])) >= 2:
                print("[KimiService] No charts/tables found, generating based on content...")
                parsed = await self._generate_charts_from_content(parsed)
            
            return parsed
        except json.JSONDecodeError:
            print(f"[KimiService] JSON decode error. Raw result: {result[:200]}...")
            return await self._generate_charts_from_content(outline)
    
    async def _generate_charts_from_content(self, outline: Dict[str, Any]) -> Dict[str, Any]:
        pages = outline.get("pages", [])
        if len(pages) < 2:
            return outline
        
        pages_info = []
        for i, page in enumerate(pages):
            content_text = " ".join(page.get("content", []))
            pages_info.append(f"第{i+1}页 '{page.get('title', '')}': {content_text[:200]}")
        
        prompt = f"""请根据以下PPT各页面的内容，为合适的页面生成图表或表格数据。

PPT标题: {outline.get('title', '演示文稿')}

各页面内容:
{chr(10).join(pages_info)}

要求：
1. 分析每页内容，为包含数据、趋势、对比、列表等信息的页面生成图表或表格
2. 图表数据要与页面内容主题相关，数据要合理、真实感
3. 至少为2-3个页面生成图表或表格
4. 返回JSON格式，只包含需要添加图表/表格的页面信息：
{{
    "pages_with_charts": [
        {{
            "page_index": 2,
            "charts": [{{
                "type": "bar",
                "title": "与该页内容相关的图表标题",
                "data": {{
                    "categories": ["类别1", "类别2", "类别3"],
                    "series": [{{"name": "系列名", "values": [数值1, 数值2, 数值3]}}]
                }}
            }}]
        }},
        {{
            "page_index": 3,
            "tables": [{{
                "title": "与该页内容相关的表格标题",
                "headers": ["列1", "列2", "列3"],
                "rows": [["数据1", "数据2", "数据3"]]
            }}]
        }}
    ]
}}

请直接返回JSON，不要添加其他说明文字。"""

        try:
            result = await self._call_api(prompt)
            result = result.replace("```json", "").replace("```", "").strip()
            charts_data = json.loads(result)
            
            pages_with_charts = charts_data.get("pages_with_charts", [])
            for page_info in pages_with_charts:
                page_idx = page_info.get("page_index", 0) - 1
                if 0 <= page_idx < len(pages):
                    if "charts" in page_info:
                        pages[page_idx]["charts"] = page_info["charts"]
                    if "tables" in page_info:
                        pages[page_idx]["tables"] = page_info["tables"]
                    print(f"[KimiService] Added charts/tables to page {page_idx + 1}")
            
            return outline
        except Exception as e:
            print(f"[KimiService] Failed to generate charts from content: {e}")
            return self._add_default_charts_and_tables(outline)
    
    def _add_default_charts_and_tables(self, outline: Dict[str, Any]) -> Dict[str, Any]:
        pages = outline.get("pages", [])
        if len(pages) < 2:
            return outline
        
        for i, page in enumerate(pages):
            if i == 1:
                page["charts"] = [{
                    "type": "bar",
                    "title": "发展趋势分析",
                    "data": {
                        "categories": ["2020", "2021", "2022", "2023", "2024"],
                        "series": [{"name": "增长率", "values": [15, 25, 35, 45, 55]}]
                    }
                }]
            elif i == 2:
                page["tables"] = [{
                    "title": "关键指标对比",
                    "headers": ["指标", "当前值", "目标值", "状态"],
                    "rows": [
                        ["用户增长", "120%", "100%", "达标"],
                        ["收入增长", "85%", "90%", "接近"],
                        ["满意度", "92%", "95%", "良好"]
                    ]
                }]
            elif i == 3 and len(pages) > 4:
                page["charts"] = [{
                    "type": "pie",
                    "title": "市场份额分布",
                    "data": {
                        "categories": ["产品A", "产品B", "产品C", "其他"],
                        "series": [{"name": "份额", "values": [35, 30, 25, 10]}]
                    }
                }]
        
        print(f"[KimiService] Added default charts/tables to {min(3, len(pages))} pages")
        return outline
    
    async def parse_document(self, content: str) -> Dict[str, Any]:
        parsed = self._parse_outline_text(content)
        
        if len(parsed['pages']) >= 2:
            print(f"[KimiService] Local parsing successful: {len(parsed['pages'])} pages found")
            return parsed
        
        print("[KimiService] Local parsing failed, calling AI...")
        
        prompt = f"""请分析以下文档内容，生成PPT大纲，以JSON格式返回。

文档内容：
{content[:20000]}

要求：
1. **严格遵循文档结构**：文档中已经明确标记了每一页的内容（如"第1页"、"第2页"等），请直接解析这些页面结构。
2. 提取每页的标题和要点。
3. 返回格式如下：
{{
    "title": "PPT标题",
    "pages": [
        {{
            "page_index": 1,
            "title": "页面标题",
            "content": ["要点1", "要点2", "要点3"],
            "layout_type": "single_column"
        }}
    ]
}}

请直接返回JSON，不要添加其他说明文字。"""

        try:
            result = await self._call_api(prompt)
            result = result.replace("```json", "").replace("```", "").strip()
            parsed_json = json.loads(result)
            
            if not parsed_json.get("pages") or len(parsed_json["pages"]) == 0:
                print("[KimiService] AI returned empty pages, falling back to original content parsing")
                return self._parse_outline_text(content)
                
            return parsed_json
        except json.JSONDecodeError:
            print(f"[KimiService] JSON decode error in parse_document. Raw result: {result[:200]}...")
            print("[KimiService] Fallback to parsing original content")
            return self._parse_outline_text(content)


class AIServiceFactory:
    @staticmethod
    def get_service(model: str = "qwen") -> AIService:
        if model == "kimi" and settings.MOONSHOT_API_KEY:
            return KimiService()
        elif model == "qwen" and settings.DASHSCOPE_API_KEY:
            return QwenService()
        else:
            print(f"[AIServiceFactory] API Key not found for {model}, using MockAIService")
            return MockAIService()
