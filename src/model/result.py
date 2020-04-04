def ok(data=None, code='success', msg='success'):
    if data is None:
        return {'state': True, 'msg': msg}
    return {'state': True, 'code': code, 'msg': msg, 'data': data}


def fail(code='error', msg='error'):
    return {'state': False, 'code': code, 'msg': msg}
