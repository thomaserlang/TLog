# coding=UTF-8
import re
import json
from tornado.escape import to_unicode
from wtforms import Form, TextField, TextAreaField, PasswordField, validators, ValidationError

class Base(Form):
  def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
    if formdata is not None and not hasattr(formdata, 'getlist'):
        formdata = _TornadoArgumentsWrapper(formdata)
    Form.__init__(self, formdata, obj=obj, prefix=prefix, **kwargs)

class Login(Base):
    email = TextField('Email', [
        validators.Required(),
    ])
    password = PasswordField('Password', [
        validators.Required(),
    ])

class Signup(Base):
    name = TextField('Name', [
        validators.Required(),
        validators.Length(min=1, max=45),
    ])
    email = TextField('Email', [
        validators.Required(),
        validators.Length(min=1, max=45),
    ])
    password = PasswordField('Password', [
        validators.Required(),
    ])
    confirm = PasswordField('Repeat password', [
        validators.EqualTo('password', message='Passwords must match'),
    ])

class Filter(Base):

    name = TextField('Name', [
        validators.Length(min=1, max=45)
    ])
    data = TextAreaField('Filter JSON', [
        validators.Required(),
    ])

    def validate_data(form, field):
        try:
            json.loads(field.data)
        except:
            raise ValidationError('Must be valid JSON!')

class Team(Base):

    name = TextField('Name', [
        validators.Length(min=1, max=45)
    ])

class _TornadoArgumentsWrapper(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError

    def getlist(self, key):
        try:
            values = []
            if not isinstance(self[key], list):
                self[key] = [self[key]]
            for v in self[key]:
                v = to_unicode(v)
                if isinstance(v, unicode):
                    v = re.sub(r"[\x00-\x08\x0e-\x1f]", " ", v)
                values.append(v)

            values.reverse()
            return values
        except KeyError:
            raise AttributeError