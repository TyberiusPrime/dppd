import sys, setuptools, tokenize, os; sys.argv[0] = 'setup.py'; __file__='setup.py';
f=getattr(tokenize, 'open', open)(__file__);
code=f.read().replace('\r\n', '\n');
f.close();
exec(compile(code, __file__, 'exec'))

