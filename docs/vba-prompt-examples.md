# VBA Prompt Generation Examples

## ✅ Correct Approach: Generate VBA Prompts

The system should generate **detailed requirements** for VBA code generation, not the actual VBA code.

### English Examples

**User Request:** "automate formatting for all documents"

**❌ WRONG (VBA Code):**
```vba
For Each doc In Documents
    doc.Range.Font.Name = "Calibri"
    doc.Range.Font.Size = 11
Next doc
```

**✅ CORRECT (VBA Prompt):**
```
VBA Requirement: 
- Objects: All Word documents in specified folder
- Conditions: Documents must be .docx format
- Actions: Apply consistent formatting (Calibri 11pt, 1.5 line spacing)
- Expected Result: All documents formatted uniformly and saved
```

### Chinese Examples

**用户请求：** "批量处理Excel工作表"

**❌ 错误 (VBA代码):**
```vba
For Each ws In Worksheets
    ws.Range("A1").Value = "标题"
Next ws
```

**✅ 正确 (VBA提示):**
```
VBA需求：
- 对象：当前工作簿中的所有工作表
- 条件：工作表包含数据且非隐藏状态
- 操作：删除空行，统一表头格式，添加边框
- 预期结果：格式统一的工作表并汇总到新表
```

## 🎯 Task Categorization

### 1. Content Generation → Content Prompts
**Input:** "write a business letter"
**Output:** Content details (recipient, purpose, tone, length)

### 2. Function Operations → VBA Prompts  
**Input:** "automate document formatting"
**Output:** VBA requirements (objects, conditions, actions, results)

### 3. Direct Commands → UI Steps
**Input:** "make text bigger"  
**Output:** Select text → Home → Font Size → 14pt

## 🔄 Example Conversation Flow

```
👤 User: 自动化处理多个Excel文件
🤖 Assistant: 应用选择：0=Word, 1=Excel
             功能操作任务→VBA生成，请详细描述自动化需求

👤 User: 1
🤖 Assistant: 已选择Excel。请继续描述具体任务。

👤 User: 合并多个文件的数据到一个汇总表
🤖 Assistant: VBA需求：
             - 对象：指定文件夹中的所有Excel文件
             - 条件：文件格式为.xlsx，包含数据
             - 操作：提取每个文件的数据范围
             - 预期结果：创建汇总工作簿，按文件名分别汇总数据
```

## 🎪 Benefits

1. **Clear Requirements:** Next AI system gets precise VBA generation requirements
2. **No Code Mixing:** Separates requirement gathering from code generation
3. **Better Prompts:** More detailed and structured prompts for VBA generation
4. **Language Consistency:** Prompts match user's language (Chinese/English)