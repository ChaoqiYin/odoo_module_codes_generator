# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
import os

SQL_MODEL_DICT = dict()


class BaseModel(object):
    def __init__(self, table_name):
        # 根据table的name创建相应的class并在dict中创建键值对
        self.table_name = table_name
        self.description = None
        SQL_MODEL_DICT[table_name] = self
        self.fields = {}

    def search_field(self, field_name):
        if field_name in self.fields:
            return self.fields[field_name]
        else:
            return None

    def create_model_files(self, path):
        py_path = os.path.join(path, '%s.py' % self.table_name.replace('.', '_'))
        with open(py_path, 'w') as f:
            f.writelines([
                "from odoo import models, fields\n\n\n",
                "class {}(models.Model):\n".format(
                    ''.join(list(map(lambda x: x.capitalize(), self.table_name.split('.'))))),
                " " * 4 + "_name = '{}'\n".format(self.table_name)
            ])
            if self.description is not None:
                f.write("    _description = '{}'\n".format(self.description))
            if len(self.fields) > 0:
                f.write('\n')
                f.writelines([
                    " " * 4 + "{}\n".format(
                        self.fields[field_key].get_field_word()) for field_key in self.fields
                ])

    def create_view_files(self, path):
        view_path = os.path.join(path, '%s_view.xml' % self.table_name.replace('.', '_'))
        with open(view_path, 'w') as f:
            tree_code = ""
            form_code = ""
            if len(self.fields) > 0:
                for field_key in self.fields:
                    tree_code += " " * 20 + "<field name=\"{}\"/>\n".format(self.fields[field_key].name)
                    form_code += " " * 24 + "<field name=\"{}\"/>\n".format(self.fields[field_key].name)
            f.writelines([
                "<?xml version=\"1.0\" encoding=\"utf-8\" ?>",
                "<odoo>\n",
                " " * 4 + "<data>\n",
                # tree的xml代码
                " " * 8 + "<record id=\"{}_tree\" model=\"ir.ui.view\">\n".format(self.table_name.replace('.', '_')),
                " " * 12 + "<field name=\"name\">{}_tree</field>\n".format(self.table_name.replace('.', '_')),
                " " * 12 + "<field name=\"model\">{}</field>\n".format(self.table_name),
                " " * 12 + "<field name=\"arch\" type=\"xml\">\n",
                " " * 16 + "<tree create=\"1\" edit=\"1\" delete=\"1\">\n",
                tree_code,
                " " * 16 + "</tree>\n",
                " " * 12 + "</field>\n",
                " " * 8 + "</record>\n\n",
                # form的xml代码
                " " * 8 + "<record id=\"{}_form\" model=\"ir.ui.view\">\n".format(self.table_name.replace('.', '_')),
                " " * 12 + "<field name=\"name\">{}_form</field>\n".format(self.table_name.replace('.', '_')),
                " " * 12 + "<field name=\"model\">{}</field>\n".format(self.table_name),
                " " * 12 + "<field name=\"arch\" type=\"xml\">\n",
                " " * 16 + "<form create=\"1\" edit=\"1\" delete=\"1\">\n",
                " " * 20 + "<group>\n",
                form_code,
                " " * 20 + "</group>\n",
                " " * 16 + "</form>\n",
                " " * 12 + "</field>\n",
                " " * 8 + "</record>\n\n",
                # act_window的xml代码
                " " * 8 + "<record id=\"act_{}\" model=\"ir.actions.act_window\">\n".format(
                    self.table_name.replace('.', '_')),
                " " * 12 + "<field name=\"name\">act_{}</field>\n".format(self.table_name.replace('.', '_')),
                " " * 12 + "<field name=\"res_model\">{}</field>\n".format(self.table_name),
                " " * 12 + "<field name=\"view_mode\">tree,form</field>\n",
                " " * 8 + "</record>\n",
                " " * 4 + "</data>\n",
                "</odoo>\n",
            ])
