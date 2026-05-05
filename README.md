使用opencode+deepseek4-pro对[xadmin](https://github.com/sshwsfc/xadmin)升级，使其支持python3.12+django4.2，同时对标记为废弃、但未正式删除的的api全部做了调整，以下是opencode整理的变动
以下是xadmin升级日志的整理汇总：

---

## xadmin 升级到 Python 3.12 + Django 4.2 完整修复汇总

### 一、项目目标
- 将 xadmin 从 Python 2.7/Django 1.9 升级到 **Python 3.12 + Django 4.2**
- 修复 demo_app 兼容性，支持 django-import-export v4
- 适配 crispy-forms 2.x、django-reversion 6.x 等依赖

### 二、依赖版本更新
| 依赖 | 版本要求 |
|------|----------|
| Django | >=4.0 |
| django-crispy-forms | >=2.5 |
| crispy-bootstrap3 | >=2024.1 |
| django-reversion | >=6.1.0 |
| django-formtools | >=2.5.1 |
| httplib2 | >=0.31.2 |

### 三、核心兼容性修复

#### 1. Django 4.2 适配

| 文件 | 问题 | 修复方式 |
|------|------|----------|
| `views/base.py` | `classonlymethod` 在 Django 4.0 移除 | 自定义 `classonlymethod` 描述符替代 |
| `views/list.py`, `util.py`, `plugins/filters.py` | `FieldDoesNotExist` 导入路径变更 | `from django.db.models.fields import FieldDoesNotExist` |
| `util.py`, `plugins/relate.py` | `LOOKUP_SEP` 路径变更 | `from django.db.models.constants import LOOKUP_SEP` |
| `util.py` | `django.utils.simplejson` 移除 | 直接 `import json` |
| `views/edit.py`, `plugins/inline.py` | `modelform_defines_fields` 在 Django 4.1 移除 | 手动检查 `_meta.fields` 替代 |
| `views/detail.py`, `delete.py`, `plugins/sortablelist.py` | `__all__` → `ALL_FIELDS`, `get_deleted_objects` 签名变更, `context_instance` 移除 | 全部修正 |
| `plugins/filters.py` | `do_filte` 拼写错误 | 修正为 `do_filter` |

#### 2. Django 4.2 弃用 API 修复

| 弃用项 | 影响版本 | 修复方式 |
|--------|----------|----------|
| `default_app_config` | 3.2 弃用，5.0 移除 | 改为 `apps.py` 中 `default = True` |
| `django.template.Context` | 3.0 弃用，5.0 移除 | 移除 4 处引用，改用 `dict` |
| `use_l10n` 模板上下文属性 | 4.0 弃用，5.0 移除 | `getattr(context, 'use_l10n', True)` |
| `RequestContext` / `Context` | 3.0 弃用，5.0 移除 | 重写 `get_context_dict()` |

#### 3. remote_field 变更（Django 4+）
| 原写法 | 新写法 |
|--------|--------|
| `remote_field.to` | `remote_field.model` |
| `self.rel.to` | `self.rel.model` |

**涉及文件**：`relfield.py`, `filters.py`, `util.py`

#### 4. crispy-forms 2.x 适配
| 变更 | 修复方式 |
|------|----------|
| `Pointer` 下标访问 `i[0]`/`i[1]` | 改用 `i.position`/`i.name` |
| `flatatt` 从 `crispy_forms.utils` 移除 | 改为 `from django.forms.utils import flatatt` |

**涉及文件**：`edit.py`, `detail.py`, `form.py`, `ajax.py`, `inline.py`（5处）

#### 5. django-reversion 6.x 适配

| 变更 | 修复方式 |
|------|----------|
| `get_deleted`, `_object_version` API 变更 | 添加 3 个兼容函数：`_get_deleted_versions`, `_get_version_object_data`, `_get_versions_for_object` |

**涉及文件**：`plugins/xversion.py`

#### 6. Python 3 清理

| 清理项 | 数量 | 操作 |
|--------|------|------|
| `from __future__ import ...` | 15处 | 全部移除 |
| `six` 库 (PY2/PY3 分支) | 31处 import + 分支逻辑 | 全部移除 |
| `cls_str = str if six.PY3 else str` | 13处 | 替换为直接用 `str` |

### 四、导出功能修复（django-import-export v4）

| 问题 | 修复方式 |
|------|----------|
| `ImportForm`/`ExportForm` 构造签名变更 | 添加 `resources` 参数 |
| `file_format` → `format` | `ExportForm` 字段名修正 |
| `input_format` → `format` | `ImportForm`/`ConfirmImportForm` 字段名修正 |
| `force_str` 移除 | 改用 Python 3 原生 `bytes.decode()` |
| `_selected_actions` 为空导致 `ValueError` | 防止 `pk__in=['']` |
| 导出文件名 `verbose_name.encode('utf-8')` 输出 bytes | 移除 encode |
| `SimpleListFilter` 不兼容 | 新增 `DjangoFilterWrapper` 桥接类 |
| `export_default_scope` / `export_fixed_scope` | 添加配置支持 |

### 五、布尔字段显示修复（详情页）

| 文件 | 修复 |
|------|------|
| `util.py` | `boolean_icon()` 添加文字标签（是/否/未知），`text-error` → `text-danger` |
| `views/detail.py` | `ResultField` 设置 `allow_tags=True` |
| `views/list.py` | `ResultItem` 设置 `allow_tags=True` |
| `filters.py`, `plugins/export.py` | 移除废弃的 `NullBooleanField` 引用 |

### 六、关键决策记录
- `remote_field.to` → `remote_field.model` 全局替换
- crispy-forms 2.x 中 `Pointer` 改用属性访问替代下标
- `NullBooleanField` 完全移除，`BooleanField(null=True)` 可替代
- `SimpleListFilter` 采用 `DjangoFilterWrapper` 包装而非修改 Django 源码
- `export_fixed_scope` 通过 `getattr(self, 'export_fixed_scope', None)` 读取

---
