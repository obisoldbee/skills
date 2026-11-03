"""Local isolated HTTP security tests; no provider calls."""
import hashlib,json,threading,time,unittest
from http.client import HTTPConnection
from urllib.parse import urlencode,urlsplit,parse_qs
from bridge import Handler,LimitedServer,b64,digest
from test_bridge import BridgeTests


class HTTPTests(BridgeTests):
    def setUp(self):
        super().setUp()
        self.server=LimitedServer(('127.0.0.1',0),Handler)
        self.server.bridge=self.b
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join()
        super().tearDown()

    def req(self,path,data=None,key=None,form=False):
        c=HTTPConnection('127.0.0.1',self.server.server_port,timeout=5)
        headers={}
        if key:headers['Authorization']='Bearer '+key
        body=None
        if data is not None:
            body=urlencode(data) if form else json.dumps(data)
            headers['Content-Type']='application/x-www-form-urlencoded' if form else 'application/json'
        c.request('POST' if data is not None else 'GET',path,body,headers)
        r=c.getresponse();result=(r.status,dict(r.getheaders()),r.read());c.close()
        return result

    def test_oauth_refresh_revoke_and_auth_isolation(self):
        redirect='https://chatgpt.com/test-callback'
        status,_,body=self.req('/register',{'redirect_uris':[redirect]})
        self.assertEqual(status,201);client=json.loads(body)['client_id']
        verifier='v'*48
        params={'client_id':client,'redirect_uri':redirect,'response_type':'code','code_challenge_method':'S256','code_challenge':b64(hashlib.sha256(verifier.encode()).digest()),'resource':self.b.base+'/mcp','scope':'bridge','state':'state','owner_key':'a'*48}
        status,headers,_=self.req('/authorize',params,form=True)
        self.assertEqual(status,303)
        code=parse_qs(urlsplit(headers['Location']).query)['code'][0]
        grant={'grant_type':'authorization_code','client_id':client,'redirect_uri':redirect,'code':code,'code_verifier':verifier,'resource':self.b.base+'/mcp'}
        status,_,body=self.req('/token',grant,form=True);self.assertEqual(status,200)
        tokens=json.loads(body)
        self.assertEqual(self.req('/token',grant,form=True)[0],400)
        rpc={'jsonrpc':'2.0','id':1,'method':'tools/list','params':{}}
        self.assertEqual(self.req('/mcp',rpc)[0],401)
        self.assertEqual(self.req('/mcp',rpc,'g'*48)[0],403)
        self.assertEqual(self.req('/mcp',rpc,tokens['access_token'])[0],200)
        self.assertEqual(self.req('/health')[0],401)
        self.assertEqual(self.req('/health',key='a'*48)[0],200)
        refresh={'grant_type':'refresh_token','client_id':client,'refresh_token':tokens['refresh_token'],'resource':self.b.base+'/mcp'}
        status,_,body=self.req('/token',refresh,form=True);self.assertEqual(status,200)
        fresh=json.loads(body)
        self.assertEqual(self.req('/token',refresh,form=True)[0],400)
        self.assertEqual(self.req('/admin/revoke',{},'a'*48)[0],200)
        self.assertEqual(self.req('/mcp',rpc,tokens['access_token'])[0],401)
        self.assertEqual(self.req('/mcp',rpc,fresh['access_token'])[0],401)
        self.assertEqual(self.req('/token',{**refresh,'refresh_token':fresh['refresh_token']},form=True)[0],400)
        self.assertEqual(self.b.db.execute('SELECT active FROM subscriptions').fetchone()[0],0)

    def test_expired_token_and_oversize(self):
        self.b.db.execute('INSERT INTO tokens VALUES(?,?,?,?)',(digest('expired'),'client','access',time.time()-1))
        rpc={'jsonrpc':'2.0','id':1,'method':'tools/list'}
        self.assertEqual(self.req('/mcp',rpc,'expired')[0],401)
        self.assertEqual(self.req('/messages',{'text':'x'*33000},'g'*48)[0],400)

    def test_scoped_callback_parts_and_retry(self):
        self.send(1)
        self.b.dispatch_one()
        callback=urlsplit(self.calls[-1][1]['callback_url']).path
        self.assertEqual(self.req(callback,{'action':'reply','text':'unclaimed'})[0],400)
        self.assertTrue(json.loads(self.req(callback,{'action':'claim'})[2])['claimed'])
        first={'action':'reply','part_index':0,'text':'first','end_of_turn':False}
        code,_,body=self.req(callback,first)
        self.assertEqual(code,200)
        self.assertFalse(json.loads(body)['end_of_turn'])
        self.assertTrue(json.loads(self.req(callback,first)[2])['duplicate'])
        last={'action':'reply','part_index':1,'text':'second','end_of_turn':True,'final':True}
        self.assertEqual(self.req(callback,last)[0],200)
        self.assertEqual(self.req('/grok/wrong-token',first)[0],401)
        self.assertEqual(self.req(callback,{**last,'part_index':2})[0],400)


if __name__=='__main__':unittest.main()
