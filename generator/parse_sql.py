# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
import os
import re
import sqlparse
import queue
from sqlparse.sql import Identifier, Parenthesis

from .model.model import BaseModel, SQL_MODEL_DICT
from .model.field import (StringField, TextField, IntField, FloatField, BoolField, DateField, DateTimeField, BinaryField,
                         Many2oneField, One2manyField, Many2manyField)
from .thread_pool import ThreadPool

def get_content(obj):
    '''
    获取解析内容，判断对象是文件还是路径
    :param obj:
    :return:
    '''
    if hasattr(obj, 'read') is True:
        return obj.read().encode('utf8')
    else:
        with open(obj, 'r') as f:
            content = f.read()
        return content


def get_field_class(name, field_type):
    '''
    根据field_type分配不同的field_class
    :param name:
    :param field_type:
    :return:
    '''
    if field_type in ['varchar255', 'char255']:
        return StringField(name)
    elif field_type in ['text']:
        return TextField(name)
    elif field_type in ['int', 'int2', 'int4', 'int8']:
        return IntField(name)
    elif field_type in ['float4', 'float8']:
        return FloatField(name)
    elif field_type in ['bool']:
        return BoolField(name)
    elif field_type in ['date']:
        return DateField(name)
    elif field_type in ['time0']:
        return DateTimeField(name)
    elif field_type in ['bytea']:
        return BinaryField(name)
    else:
        return None


class Parse(object):
    def __init__(self, sql_path):
        f_content = get_content(sql_path)  # 获取文件内容
        self.sql_tree = sqlparse.parse(f_content.strip().replace('\n', ''))  # 获取sql树
        self._get_model()
        self.model = SQL_MODEL_DICT

    def _get_model(self):
        for statement in self.sql_tree:
            self._parse_tokens(statement)

    def _parse_tokens(self, statement):
        '''
        解析相应的sql语句，创建对应的model
        :param statement:
        :return:
        '''
        # 创建table
        if re.match(r'CREATE TABLE.*', statement.value) is not None:
            self._parse_for_create_model(statement)
        # 添加表注释
        elif re.match(r'COMMENT ON TABLE.*?IS.*', statement.value) is not None:
            self._parse_for_comment_table(statement)
        # 添加字段注释
        elif re.match(r'COMMENT ON COLUMN.*?IS.*', statement.value) is not None:
            self._parse_for_comment_model(statement)
        # 添加外键关系
        elif re.match(r'ALTER TABLE.*?ADD CONSTRAINT.*?FOREIGN KEY.*?REFERENCES.*', statement.value) is not None:
            self._parse_for_constraint_model(statement)

    @staticmethod
    def _parse_for_create_model(statement):
        '''
        解析时创建相应的model和field
        :param statement:
        :return:
        '''
        create_fields = {}
        for token in statement.tokens:
            if isinstance(token, Identifier) is True and token.value != '':
                table_name = token.value.replace('"', '')
                # 创建model
                BaseModel(token.value.replace('"', ''))
            # 插入句, 插入字段信息
            elif isinstance(token, Parenthesis) is True and token.value != '':
                insert_sqls = token.value.replace('(', '').replace(')', '').split(',')
                for insert_sql in insert_sqls:
                    insert_sql_list = insert_sql.split(' ')
                    field_name = insert_sql_list[0].replace('"', '')
                    # 主键字段不做操作
                    if 'PRIMARY KEY' not in insert_sql and field_name.lower() != 'id':
                        field_class = get_field_class(field_name, insert_sql_list[1])
                        if field_class is not None:
                            # 必填字段
                            if 'NOT NULL' in insert_sql:
                                field_class.required = True
                            # 字段默认值
                            elif 'DEFAULT' in insert_sql:
                                field_class.default = insert_sql_list[insert_sql_list.index('DEFAULT') + 1]
                            create_fields[field_name] = field_class
        # fields与model绑定
        SQL_MODEL_DICT[table_name].fields = create_fields

    @staticmethod
    def _parse_for_comment_table(statement):
        '''
        解析时根据传入的值修改model的描述description
        :param statement:
        :return:
        '''
        comment_group = re.search(r'COMMENT ON TABLE (.*?) IS (.*?);', statement.value)
        assert comment_group is not None
        groups = comment_group.groups()
        model_name = groups[0].replace('\"', '').replace('\'', '')
        description_name = groups[1].replace('\"', '').replace('\'', '')
        SQL_MODEL_DICT[model_name].description = description_name

    @staticmethod
    def _parse_for_comment_model(statement):
        '''
        解析时根据传入的值修改field的描述string_name
        :param statement:
        :return:
        '''
        comment_group = re.search(r'COMMENT ON COLUMN (.*?) IS (.*?);', statement.value)
        assert isinstance(statement.tokens[6], Identifier) is True and comment_group is not None
        relation = comment_group.groups()[0].replace('"', '').replace('\'', '').split('.')
        model_name = relation[0]
        field_name = relation[1]
        field_string_name = comment_group.groups()[1].replace('"', '').replace('\'', '')
        SQL_MODEL_DICT[model_name].search_field(field_name).string_name = field_string_name

    @staticmethod
    def _parse_for_constraint_model(statement):
        '''
        解析时根据传入的值修改相应的model对应的field为m2o/o2m/m2m类型
        :param statement:
        :return:
        '''
        constraint_group = re.search(
            r'ALTER TABLE (.*?) ADD CONSTRAINT (.*?) FOREIGN KEY (.*?) REFERENCES (.*?) \((.*?)\).*;', statement.value)
        assert isinstance(statement.tokens[10], Identifier) is True and constraint_group is not None
        groups = constraint_group.groups()
        current_table_name = groups[0].replace('"', '').replace('\'', '')
        current_field_name = groups[2].replace('"', '').replace('\'', '').replace('(', '').replace(')', '')
        relation_table_name = groups[3].replace('"', '').replace('\'', '')
        relation_name = groups[1].replace('"', '').replace('\'', '')
        # m2m关系relation开头用m2m_
        if re.match(r'm2m.*', relation_name) is not None:
            relation_field_name = groups[4].replace('"', '').replace('\'', '')
            # 变更原有field为m2m的field
            try:
                m2m_field = SQL_MODEL_DICT[current_table_name].fields[current_field_name]
                to_model_m2m_field = SQL_MODEL_DICT[relation_table_name].fields[relation_field_name]
            except KeyError:
                raise Warning('m2m field can\'t be the <id>')
            m2m_field.__class__ = Many2manyField
            m2m_field.field_type = 'Many2many'
            m2m_field.to_model = relation_table_name
            m2m_field.relation = relation_name
            m2m_field.field1 = current_table_name
            m2m_field.field2 = relation_table_name
            # 在对应的model中变更m2m的field
            to_model_m2m_field.__class__ = Many2manyField
            to_model_m2m_field.field_type = 'Many2many'
            to_model_m2m_field.to_model = relation_table_name
            to_model_m2m_field.relation = relation_name
            to_model_m2m_field.field1 = relation_table_name
            to_model_m2m_field.field2 = current_table_name
        # m2o关系
        else:
            # 变更原有field为m2o的field
            try:
                m2o_field = SQL_MODEL_DICT[current_table_name].fields[current_field_name]
            except KeyError:
                raise Warning('m2o field can\'t be the <id>')
            m2o_field.__class__ = Many2oneField
            m2o_field.field_type = 'Many2one'
            m2o_field.to_model = relation_table_name
            if 'ON DELETE' in statement.value:
                on_delete_value_word_list = statement.value.replace('ON DELETE', 'ONDELETE').split(' ')
                m2o_field.on_delete = on_delete_value_word_list[on_delete_value_word_list.index('ONDELETE') + 1]
            else:
                m2o_field.on_delete = None
            # 在对应的model中添加o2m的field
            o2m_field_name = '%s_ids' % current_table_name
            o2m_field = One2manyField(o2m_field_name, current_table_name, current_field_name)
            SQL_MODEL_DICT[relation_table_name].fields[o2m_field_name] = o2m_field

    @staticmethod
    def check_file(path, is_dir=True):
        '''
        检查路径文件/文件夹是否存在
        :param path:
        :param is_dir: 目标路径是否为文件夹
        :return:
        '''
        if is_dir is True:
            if os.path.exists(path) is False and os.path.isdir(path) is False:
                os.makedirs(path)
            return path
        else:
            if os.path.exists(path) is False and os.path.isfile(path) is False:
                open(path, 'w').close()
            return path

    def create_files(self, path, thread_num=2):
        '''
        生成module文件
        :param path:
        :return:
        '''
        module_path = self.check_file(os.path.join(path, 'odoo_module'))
        models_path = self.check_file(os.path.join(module_path, 'models'))
        views_path = self.check_file(os.path.join(module_path, 'views'))
        work_queue = queue.Queue()
        for model_key in self.model:
            work_queue.put((self.model[model_key].create_model_files, (models_path,), {}))
            work_queue.put((self.model[model_key].create_view_files, (views_path,), {}))
        pool = ThreadPool(work_queue, thread_num)
        pool.join_all()
        print('all done, the file_path is "%s"' % module_path)

