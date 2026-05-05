使用opencode+deepseek4-pro对xadmin[https://github.com/sshwsfc/xadmin]升级，使其支持python3.12+django4.2，同时对标记为废弃、但未正式删除的的api全部做了调整

Thinking: The user is asking me to create an anchored summary from the conversation history. Let me review the entire conversation and extract the key information.
The conversation covers:
1. Fixing a typo in xadmin filters plugin (do_filte → do_filter)
2. Making Django SimpleListFilter compatible with xadmin by creating DjangoFilterWrapper
3. Fixing django-import-export v4 API compatibility in importexport.py
4. Multiple field name changes (file_format → format, input_format → format)
5. Empty _selected_actions causing ValueError
6. Configuring export scope defaults and fixed scope
Let me organize this into the template structure.
Goal
- 让 xadmin 与 Django 4.2 + Python 3.12 + django-import-export 4.3 完全兼容，修复自定义 Django SimpleListFilter 不生效和导出功能的各种问题。
Constraints & Preferences
- 不删除或大规模重写原有 xadmin 代码，最小侵入式修复
- 保持原有内置简易导出 (export.py) 与 django-import-export 插件 (importexport.py) 共存
- 支持在 adminx 类中配置导出默认值和固定范围
Progress
Done
- 修复 xadmin/filters.py 中 3 处 do_filte → do_filter 拼写错误
- 在 xadmin/plugins/filters.py 新增 DjangoFilterWrapper 类，桥接 Django SimpleListFilter 到 xadmin 接口
- 修复 xadmin/plugins/filters.py 中 is_used 属性缺失（回退使用 used_parameters）
- 修复 xadmin/plugins/importexport.py 中 ImportForm/ExportForm 构造签名（v4 新增 resources 参数）
- 修复字段名变更：file_format → format（ExportForm）、input_format → format（ImportForm/ConfirmImportForm）
- 移除 force_str 改为 Python 3 原生 bytes.decode()，移除 mimetype 兼容代码
- 修复 get_export_filename 中 verbose_name.encode('utf-8') 导致 bytes 输出的问题
- 修复 _selected_actions 为空时 pk__in=[''] 造成的 ValueError
- 添加 export_default_scope 和 export_fixed_scope 支持，修改对应模板
In Progress
- export_fixed_scope 可能未生效，用户反馈导出时仍有一堆选项（待排查是否因模板缓存或 export_items 字段干扰）
Blocked
- (none)
Key Decisions
- SimpleListFilter 兼容方案：用 DjangoFilterWrapper 包装而非修改 Django 源码，提供 do_filter、choices、__str__ 等 xadmin 期望的接口
- _p_ 前缀参数在 wrapper 的 choices() / query_string() 中统一处理
- export_fixed_scope 通过 getattr(self, 'export_fixed_scope', None) 读取，作用于 ExportMenuPlugin.block_top_toolbar 和 ExportMixin.get_export_queryset
Next Steps
- 排查 export_fixed_scope 为何未生效（需重启服务器？模板未重载？export_items 空字段干扰？）
- 确认用户是否同时设置了 list_export = () 隐藏内置导出按钮
- 可能需要过滤模板中 export_items 字段（v4 新增但无选项的空字段，label 仍会显示）
Critical Context
- Django 版本：4.2.0，django-import-export 版本：4.3.14
- ExportForm v4 字段：['resource', 'format', 'export_items']
- ImportForm v4 字段：['resource', 'import_file', 'format']
- ConfirmImportForm v4 字段：['import_file_name', 'original_file_name', 'format', 'resource']
- RowResult.IMPORT_TYPE_* 常量类型已从 int 变为 str（如 'new'），且 Result.totals 键也是字符串，旧代码用它们访问恰好兼容
- LogEntry.objects.log_action() 在 Django 4.2 中仍可用
- 导出模板路径：xadmin/blocks/model_list.top_toolbar.importexport.export.html
Relevant Files
- xadmin/filters.py — xadmin 过滤器基类（修复 do_filte 拼写）
- xadmin/plugins/filters.py — 过滤器插件（新增 DjangoFilterWrapper，兼容 is_used 和 queryset）
- xadmin/plugins/importexport.py — django-import-export 插件（v4 API 适配、导出范围配置）
- xadmin/templates/xadmin/blocks/model_list.top_toolbar.importexport.export.html — 导出弹窗模板（scope 默认值/固定值）
- tasks/filter.py — 自定义 CountryFilter / AnnualReviewStatusFilter（Django SimpleListFilter 子类）
- tasks/adminx.py — CompanyAnnualReviewProxyAdmin 配置

全部修复完成，逐项总结如下：
修复汇总
#	文件	问题	修复方式
1	views/base.py	classonlymethod 在 Django 4.0 移除	自定义 classonlymethod 描述符替代
2	views/list.py, util.py, plugins/filters.py, plugins/aggregation.py	FieldDoesNotExist 从 django.core.exceptions 移除	改为 from django.db.models.fields import FieldDoesNotExist
3	util.py, plugins/relate.py	LOOKUP_SEP 从 sql.query 迁移	改为 from django.db.models.constants import LOOKUP_SEP
4	util.py	django.utils.simplejson 在 Django 4.x 移除	直接 import json
5	views/base.py	Context.autoescape/use_l10n/use_tz	经验证 Django 4.2 中仍有效，无需修改
6	views/edit.py, plugins/inline.py	modelform_defines_fields 在 Django 4.1 移除	手动检查 _meta.fields 替代
7	plugins/xversion.py	reversion 2→6 API 变更	3 个兼容函数：_get_deleted_versions, _get_version_object_data, _get_versions_for_object
8	__init__.py	crispy-forms CRISPY_CLASS_CONVERTERS	格式仍兼容，无需修改
9	views/detail.py, views/delete.py, plugins/sortablelist.py	__all__→ALL_FIELDS, get_deleted_objects 签名, context_instance→context	全部修正
10	全量审查	smart_text, render_to_response, django.conf.urls.url 等	已全部确认兼容

弃用修复汇总
库	弃用项	影响版本	修复
Django 4.2	default_app_config 在 __init__.py	3.2 弃用, 5.0 移除	改为 apps.py 中 default = True
Django 4.2	django.template.Context 类	3.0 弃用, 5.0 移除	移除 4 处引用，改用 dict
Django 4.2	use_l10n 模板上下文属性	4.0 弃用, 5.0 移除	改为 getattr(context, 'use_l10n', True)
Django 4.2	RequestContext / Context 导入	3.0 弃用, 5.0 移除	重写 get_context_dict()，移除 RequestContext 依赖
Python 3	from __future__ import ... (15处)	Python 3 无效	全部移除
Python 3	six 库 (PY2/PY3 分支)	Python 3 永远为 True	移除 31 处 six.PY3/six.PY2 + 全部 import six
Python 3	cls_str = str if six.PY3 else str (13处)	死代码	全部替换为直接用 str
crispy-forms 2.x	flatatt 从 crispy_forms.utils 移除	2.0 移除	改为 from django.forms.utils import flatatt
reversion 6.x	get_deleted, _object_version	5.0 API 变更	已加 compat 桥接函数