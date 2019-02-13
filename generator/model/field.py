# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
import re


class BaseField(object):
    def __init__(self, name, string_name=None):
        self.name = name
        self.string_name = string_name
        self.default = None
        self.required = False
        self.field_type = None

    def get_field_word(self):
        field_info = ''
        add_num = 0
        if self.string_name is not None:
            field_info += 'string=\'{}\''.format(self.string_name)
            add_num += 1
        if self.default is not None:
            field_info += '{}default=\'{}\''.format(', ' if add_num != 0 else '', self.default)
            add_num += 1
        if self.required is True:
            field_info += '{}required=True'.format(', ' if add_num != 0 else '')
            add_num += 1
        field_word = '{} = fields.{}({})'.format(self.name, self.field_type, field_info)
        return field_word


class StringField(BaseField):
    def __init__(self, name, string_name=None):
        super().__init__(name, string_name)
        self.field_type = 'Char'


class TextField(BaseField):
    def __init__(self, name):
        super().__init__(name)
        self.field_type = 'Text'


class IntField(BaseField):
    def __init__(self, name, string_name=None):
        super().__init__(name, string_name)
        self.field_type = 'Integer'

    def get_field_word(self):
        field_word = super().get_field_word()
        if self.default is not None:
            default_info = 'default={}'.format(str(int(self.default)))
            field_word = re.sub(r"default=\'(.*?)\'", default_info, field_word)
        return field_word


class FloatField(BaseField):
    def __init__(self, name, string_name=None):
        super().__init__(name, string_name)
        self.field_type = 'Float'

    def get_field_word(self):
        field_word = super().get_field_word()
        if self.default is not None:
            default_info = 'default={}'.format(self.default)
            field_word = re.sub(r"default=\'.*?\'", default_info, field_word)
        return field_word


class BoolField(BaseField):
    '''
    布尔field
    '''
    def __init__(self, name, string_name=None):
        super().__init__(name, string_name)
        self.field_type = 'Bool'

    def get_field_word(self):
        field_word = super().get_field_word()
        if self.default is not None:
            default_info = 'default={}'.format(str(float(self.default)))
            field_word = re.sub(r"default=\'.*?\'", default_info, field_word)
        return field_word


class DateField(BaseField):
    '''
    日期field
    '''
    def __init__(self, name, string_name=None):
        super().__init__(name, string_name)
        self.field_type = 'Date'


class DateTimeField(BaseField):
    '''
    时间field
    '''
    def __init__(self, name):
        super().__init__(name)
        self.field_type = 'Datetime'


class Many2oneField(BaseField):
    '''
    many2one字段
    '''
    def __init__(self, name, to_model, string_name=None):
        super().__init__(name, string_name)
        self.to_model = to_model
        self.on_delete = None
        self.field_type = 'Many2one'

    def get_field_word(self):
        field_info = ''
        field_info += '\'{}\''.format(self.to_model)
        if self.string_name is not None:
            field_info += ', string=\'{}\''.format(self.string_name)
        if self.default is not None:
            field_info += ', default=\'{}\''.format(self.default)
        if self.required is True:
            field_info += ', required=True'
        if self.on_delete is not None:
            field_info += ', ondelete=\'{}\''.format(self.on_delete)
        field_word = '{} = fields.{}({})'.format(self.name, self.field_type, field_info)
        return field_word


class One2manyField(BaseField):
    '''
    one2many字段
    '''
    def __init__(self, name, to_model, to_field, string_name=None):
        super().__init__(name, string_name)
        self.to_model = to_model
        self.to_field = to_field
        self.field_type = 'One2many'

    def get_field_word(self):
        field_info = ''
        field_info += '\'{}\', \'{}\''.format(self.to_model, self.to_field)
        if self.string_name is not None:
            field_info += ', string=\'{}\''.format(self.string_name)
        field_word = '{} = fields.{}({})'.format(self.name, self.field_type, field_info)
        return field_word


class Many2manyField(BaseField):
    '''
    many2many字段
    '''
    def __init__(self, name, to_model, relation, field1, field2, string_name=None):
        super().__init__(name, string_name)
        self.to_model = to_model
        self.relation = relation
        self.field1 = field1
        self.field2 = field2
        self.field_type = 'Many2many'

    def get_field_word(self):
        field_info = ''
        field_info += '\'{}\', \'{}\', \'{}\', \'{}\''.format(self.to_model, self.relation, self.field1, self.field2)
        if self.string_name is not None:
            field_info += ', string=\'{}\''.format(self.string_name)
        if self.required is True:
            field_info += ', required=True'
        field_word = '{} = fields.{}({})'.format(self.name, self.field_type, field_info)
        return field_word


class BinaryField(BaseField):
    def __init__(self, name, string_name=None):
        super().__init__(name, string_name)
        self.field_type = 'Binary'
