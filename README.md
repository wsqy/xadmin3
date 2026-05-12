# xadmin 升级及自定义菜单改动总结

## 概述

将 [xadmin](https://github.com/sshwsfc/xadmin) 从 Python 2.7 / Django 1.9 升级到 **Python 3.12 + Django 4.2**，并新增自定义菜单分组、手风琴折叠、三级目录等配置功能。轮流使用 OpenCode+Claude Code使用DeepSeek V4 Pro模型完成。

---

## 一、依赖版本更新

| 依赖 | 要求 |
|------|------|
| Python | 3.12 |
| Django | 4.2 |
| django-crispy-forms | >=2.5 |
| crispy-bootstrap3 | >=2024.1 |
| django-reversion | >=6.1.0 |
| django-formtools | >=2.5.1 |
| httplib2 | >=0.31.2 |

---

## 二、Django 4.2 兼容性修复

### 2.1 核心 API 替换

| 文件 | 问题 | 修复 |
|------|------|------|
| `views/base.py` | `classonlymethod` 在 Django 4.0 移除 | 自定义描述符替代 |
| `views/base.py` | `getfullargspec` Python 3.13 将移除 | 改用 `inspect.signature`，并适配绑定方法自动剥离 `self` 的参数偏移 |
| `views/base.py` | `context.use_l10n` Django 4.0 弃用 / 5.0 移除 | 删除该行 |
| `views/list.py`, `util.py`, `plugins/filters.py`, `plugins/aggregation.py` | `FieldDoesNotExist` 在 Django 4.2 中位于 `django.core.exceptions` | 保持现有导入（已是正确位置） |
| `util.py`, `plugins/relate.py` | `LOOKUP_SEP` 路径变更 | `from django.db.models.constants import LOOKUP_SEP` |
| `util.py` | `django.utils.simplejson` 移除 | 直接 `import json` |

### 2.2 remote_field 变更（Django 4+）

| 原写法 | 新写法 |
|--------|--------|
| `remote_field.to` | `remote_field.model` |
| `self.rel.to` | `self.rel.model` |

涉及文件：`relfield.py`, `filters.py`, `util.py`

### 2.3 Django 弃用 API 修复

| 弃用项 | 影响范围 | 修复方式 |
|--------|----------|----------|
| `default_app_config` | Django 3.2 弃用，5.0 移除 | `apps.py` 中设 `default = True` |
| `django.template.Context` | 3.0 弃用，5.0 移除 | 移除引用，改用 `dict` |
| `RequestContext` / `Context` | 3.0 弃用，5.0 移除 | 重写 `get_context_dict()` |
| `force_str` / `smart_str` | Django 5.0 弃用，5.2 移除 | 在 `xadmin/util.py` 中自定义包装函数，所有 26 个文件改为从 `xadmin.util` 导入 |
| `NullBooleanField` | Django 4.0 移除 | 移除所有引用 |

### 2.4 模型操作补充修复

| 文件 | 修复 |
|------|------|
| `views/edit.py`, `plugins/inline.py` | `modelform_defines_fields` 在 Django 4.1 移除，改用手动检查 |
| `views/detail.py`, `delete.py` | `ALL_FIELDS` 常量、`get_deleted_objects` 签名修正 |
| `plugins/sortablelist.py` | `context_instance` 移除 |
| `plugins/filters.py` | 修正方法名拼写 `do_filte` → `do_filter` |

---

## 三、第三方依赖适配

### 3.1 crispy-forms 2.x

| 变更 | 修复方式 |
|------|----------|
| `Pointer` 下标访问 `i[0]`/`i[1]` | 改用 `i.position`/`i.name` |
| `flatatt` 从 `crispy_forms.utils` 移除 | 改为 `from django.forms.utils import flatatt` |

涉及文件：`edit.py`, `detail.py`, `form.py`, `ajax.py`, `inline.py`（5 处）

### 3.2 django-reversion 6.x

添加 3 个兼容函数适配 API 变更：

```python
_get_deleted_versions(model)       # 获取已删除对象的 Version
_get_version_object_data(version)  # 反序列化 Version 对象
_get_versions_for_object(model, pk) # 获取特定对象的所有 Version
```

涉及文件：`plugins/xversion.py`

### 3.3 django-import-export v4

| 问题 | 修复 |
|------|------|
| `ImportForm`/`ExportForm` 签名变更 | 添加 `resources` 参数 |
| 字段名 `file_format` → `format` | 全部修正 |
| `force_str` 移除 | 改用 Python 3 原生 `bytes.decode()` |
| `_selected_actions` 空值 | 防止 `pk__in=['']` |
| 导出文件名 bytes 输出 | 移除 `.encode('utf-8')` |
| `SimpleListFilter` 不兼容 | 新增 `DjangoFilterWrapper` 桥接类 |
| 导出范围控制 | 新增 `export_default_scope` / `export_fixed_scope` 配置 |

### 3.4 django-formtools

| 变更 | 修复 |
|------|------|
| `django.contrib.formtools` 分离为独立包 | 改为 `from formtools.wizard.*` 导入 |

---

## 四、Python 3 清理

| 清理项 | 数量 | 操作 |
|--------|------|------|
| `from __future__ import ...` | 15 处 | 全部移除 |
| `six` 库 | 31 处 import + 分支 | 全部移除，直接使用 Python 3 原生类型 |
| `cls_str = str if six.PY3 else str` | 13 处 | 替换为 `str` |

---

## 五、布尔字段与详情页显示修复

| 文件 | 修复 |
|------|------|
| `util.py` | `boolean_icon()` 添加文字标签（是/否/未知），`text-error` → `text-danger` |
| `views/detail.py` | `ResultField` 设置 `allow_tags=True` |
| `views/list.py` | `ResultItem` 设置 `allow_tags=True` |

---

## 六、全局配置模块（新增）

在项目根目录创建 `xadmin_conf.py`，由 `xadmin.autodiscover()` 自动加载。

### 6.1 应用/模型排序

```python
from xadmin.views.base import CommAdminView

CommAdminView.apps_order = {
    "company": 1,
    "tasks": 2,
    "documents": 4,
}

CommAdminView.models_order = {
    "company.Company": 1,
    "company.CustomerGroup": 5,
}
```

### 6.2 菜单样式

```python
CommAdminView.menu_style = "accordion"   # 手风琴折叠
# CommAdminView.menu_style = "default"   # 默认展开（不设此行即为默认）
```

### 6.3 自定义菜单分组 (`menu_groups`)

打破 Django app 结构，自由组织菜单树，支持二级和三级结构：

```python
CommAdminView.menu_groups = [
    {
        "title": "客户管理",          # 一级标题
        "icon": "fa fa-users",        # 图标（可选，默认 fa-chevron-right）
        "order": 1,                   # 排序（可选）
        "models": [                   # 二级直连模型列表
            "company.company",
            "company.customergroup",
        ],
    },
    {
        "title": "任务中心",
        "groups": [                   # 三级嵌套子组
            {
                "title": "待办任务",
                "icon": "fa fa-list",
                "models": ["tasks.task"],
            },
        ],
    },
]
```

#### `menu_groups` 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `title` | `str` | 是 | 菜单显示名称 |
| `icon` | `str` | 否 | Font Awesome 类。未设则一级/二级默认 `fa fa-chevron-right`，三级默认 `fa fa-circle-o` |
| `order` | `int` | 否 | 排序，越小越靠前。未设则按列表顺序 |
| `models` | `list[str]` | 否 | 模型引用，格式 `"app_label.modelname"`（全小写） |
| `groups` | `list[dict]` | 否 | 二级子组列表，同组内 `models` 和 `groups` 可混用 |

#### 混合模式

`menu_groups` 只覆盖声明了的模型。**未覆盖的模型**自动按 `app_label` 分组兜底，保持向后兼容。

#### 排序规则

- `menu_groups` 内的模型顺序由 `models` 列表的**书写顺序**决定
- `models_order` 仅对**自动分组兜底**的模型生效

---

## 七、模板与交互增强

### 7.1 手风琴折叠

- 一级面板点击标题展开/折叠，同级互斥（`data-parent` 手风琴模式）
- 二级子组点击标题独立展开/折叠，不受手风琴限制
- 当前页面路径自动展开对应的一级面板和二级子组（`check_selected` 递归传播 `selected` 状态）
- 二级子组箭头折叠时朝右 ▶，展开时旋转 90° 朝下 ▼，0.2s CSS transition

### 7.2 缩进层级

```
客户管理                       ← 一级 (panel-heading ~15px)
    ▶ 基础信息                 ← 二级子组 (padding-left: 28px)
        公司                    ← 三级模型 (padding-left: 48px)
        集团表                  ← 三级模型 (padding-left: 48px)
    文档                       ← 二级直连模型 (padding-left: 28px)
```

### 7.3 图标默认规则

| 层级 | 未配置 icon 的默认值 |
|------|---------------------|
| 一级（顶级组） | `fa fa-chevron-right` ▶ |
| 二级（子组标题 / 直连模型） | `fa fa-chevron-right` ▶ |
| 三级（子组内模型） | `fa fa-circle-o` ○ |

---

## 八、改动文件清单

### xadmin 内部修改（升级兼容）

| 文件 | 主要改动 |
|------|----------|
| `xadmin/__init__.py` | `Settings` 类，`XADMIN_CONF` 加载 |
| `xadmin/sites.py` | 插件合并、视图创建、URL 生成 |
| `xadmin/models.py` | `force_str/smart_str` 导入迁移 |
| `xadmin/util.py` | 自定义 `force_str/smart_str`，`FieldDoesNotExist`，`boolean_icon`，`NestedObjects` |
| `xadmin/widgets.py` | `ChoiceWidget` 兼容，`force_str` 迁移 |
| `xadmin/filters.py` | `FieldDoesNotExist` 路径，`force_str` 迁移 |
| `xadmin/apps.py` | `default = True` 替代 `default_app_config` |
| `xadmin/views/base.py` | `classonlymethod` 自定义实现，`inspect.signature` 替代 `getfullargspec`，移除 `use_l10n`，`get_nav_menu()` 新增 `menu_groups` 逻辑 |
| `xadmin/views/list.py` | `allow_tags` 布尔显示，`FieldDoesNotExist` |
| `xadmin/views/edit.py` | `modelform_defines_fields` 替代，`flatatt` 来源修正 |
| `xadmin/views/detail.py` | `ResultField.allow_tags`，`ALL_FIELDS` |
| `xadmin/views/form.py` | `Pointer` 属性访问 |
| `xadmin/views/delete.py` | `get_deleted_objects` 签名 |
| `xadmin/views/dashboard.py` | 模型获取，小部件 |

### xadmin 插件修改

| 文件 | 主要改动 |
|------|----------|
| `xadmin/plugins/sitemenu.py` | 回退读取 `admin_view.menu_style` 配置 |
| `xadmin/plugins/xversion.py` | reversion 6.x 兼容 |
| `xadmin/plugins/inline.py` | `modelform_defines_fields`，`Pointer`，`flatatt` |
| `xadmin/plugins/filters.py` | `FieldDoesNotExist`，`do_filter` 拼写 |
| `xadmin/plugins/relate.py` | `LOOKUP_SEP`，`remote_field` |
| `xadmin/plugins/export.py` | `force_str`，`NullBooleanField` |
| `xadmin/plugins/importexport.py` | django-import-export v4 适配 |
| `xadmin/plugins/ajax.py` | `ErrorDict`，`flatatt` |
| `xadmin/plugins/editable.py` | `force_str` |
| `xadmin/plugins/comments.py` | django-contrib-comments 兼容 |
| `xadmin/plugins/actions.py` | `get_deleted_objects` |
| `xadmin/plugins/sortablelist.py` | `context_instance` 移除 |
| `xadmin/plugins/wizard.py` | `smart_str` |
| `xadmin/plugins/relfield.py` | `remote_field` |
| `xadmin/plugins/batch.py`, `auth.py`, `ajax.py`, `chart.py`, `bookmark.py`, `multiselect.py`, `aggregation.py` 等 | `force_str/smart_str` 导入迁移 |

### 模板修改

| 文件 | 改动 |
|------|------|
| `xadmin/templates/xadmin/includes/sitemenu_accordion.html` | 三级渲染、折叠子组、CSS 缩进与动画 |
| `xadmin/templates/xadmin/includes/sitemenu_default.html` | 三级渲染、mobile 适配 |

### 项目配置（新增）

| 文件 | 用途 |
|------|------|
| `xadmin_conf.py` | 全局菜单配置（`menu_style`、`menu_groups`、`apps_order`、`models_order`） |
| `xadmin_conf说明.md` | 菜单系统使用说明 |

