"""Small lossless-atom KiCad S-expression helpers, following R14 tooling."""
import json,re
class Atom:
 def __init__(self,raw):self.raw=raw;self.value=json.loads(raw)if raw.startswith('"')else raw
def atom(s):return Atom(str(s))
def string(s):return Atom(json.dumps(str(s),ensure_ascii=False))
def parse(text):
 stack=[];root=None
 for t in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^()\s]+',text):
  if t=='(':
   n=[]
   if stack:stack[-1].append(n)
   stack.append(n)
  elif t==')':
   n=stack.pop()
   if not stack:assert root is None;root=n
  else:stack[-1].append(Atom(t))
 assert not stack and root;return root
def tag(n):return n[0].value if isinstance(n,list)and n and isinstance(n[0],Atom)else''
def children(n,t):return[v for v in n if isinstance(v,list)and tag(v)==t]
def child(n,t):return next((v for v in n if isinstance(v,list)and tag(v)==t),None)
def value(n,t):
 c=child(n,t);return c[1].value if c else None
def prop(n,name):return next((v[2].value for v in children(n,'property')if v[1].value==name),None)
def dump(n,depth=0):
 if isinstance(n,Atom):return n.raw
 flat='('+' '.join(dump(v,99)for v in n)+')'
 if depth>=99 or len(flat)<155:return flat
 return '('+'\n'.join(('  '*(depth+1)if i else'')+dump(v,depth+1)for i,v in enumerate(n))+')'
def write(p,n):p.write_text(dump(n)+'\n')
