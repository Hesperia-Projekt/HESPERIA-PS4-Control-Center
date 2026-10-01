#!/usr/bin/env python3
"""Local-first PS4 control center; remote install needs GoldHEN RPI on port 12800 or 12801."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import unquote, urlparse
from email.utils import formatdate
import concurrent.futures, hashlib, ipaddress, json, mimetypes, os, re, shutil, socket, sys, threading, time, urllib.error, urllib.request, webbrowser

if getattr(sys, 'frozen', False):
    # PyInstaller's one-file payload is extracted to _MEIPASS. Keep user data
    # beside a portable project when present, otherwise in a sibling data dir.
    RESOURCE_ROOT = Path(getattr(sys, '_MEIPASS', Path(sys.executable).resolve().parent))
    EXE_DIR = Path(sys.executable).resolve().parent
    BASE = EXE_DIR.parent if (EXE_DIR.parent/'02_WEB_UI').is_dir() else EXE_DIR/'HESPERIA_Data'
    WEB, CFG, RETRO = RESOURCE_ROOT/'02_WEB_UI', RESOURCE_ROOT/'04_CONFIG'/'sources.json', RESOURCE_ROOT/'09_RETRO'
else:
    BASE = Path(__file__).resolve().parents[1]
    WEB, CFG, RETRO = BASE/'02_WEB_UI', BASE/'04_CONFIG'/'sources.json', BASE/'09_RETRO'
DL, USB, LOG = BASE/'07_DOWNLOADS', BASE/'08_USB_EXPORT', BASE/'10_LOGS'
LIB = BASE/'09_RETRO'/'LIBRARY'
DOWNLOAD_INDEX = DL/'download_index.json'
PORT, RPI_PORTS = 8088, (12800,12801)
UA = {'User-Agent': 'HESPERIA-PS4-Control-Center-v19'}
STATE, STATE_LOCK = {'ps4': None, 'queue': [], 'last_scan': [], 'started': int(time.time()), 'jobs': {}, 'transfers': []}, threading.Lock()
for folder in (DL, USB, LOG, LIB): folder.mkdir(parents=True, exist_ok=True)

def cfg(): return json.loads(CFG.read_text(encoding='utf-8'))
def read_download_index():
    try: return json.loads(DOWNLOAD_INDEX.read_text(encoding='utf-8'))
    except (OSError,json.JSONDecodeError): return {}
def remember_download(item_id,path):
    entry={'file':path.name,'bytes':path.stat().st_size,'sha256':sha256(path),'updated':int(time.time())}
    with STATE_LOCK:
        index=read_download_index(); index[item_id]=entry
        temporary=DOWNLOAD_INDEX.with_suffix('.json.part')
        temporary.write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8')
        temporary.replace(DOWNLOAD_INDEX)
def sha256(path):
    digest=hashlib.sha256()
    with open(path,'rb') as handle:
        for block in iter(lambda:handle.read(1024*1024),b''): digest.update(block)
    return digest.hexdigest()
def local_ip():
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    try: sock.connect(('8.8.8.8',80)); return sock.getsockname()[0]
    except OSError: return '127.0.0.1'
    finally: sock.close()
def local_ipv4_addresses():
    candidates={local_ip()}
    try:
        candidates.update(info[4][0] for info in socket.getaddrinfo(socket.gethostname(),None,socket.AF_INET) if info[4][0] != '127.0.0.1')
    except OSError: pass
    return sorted(ip for ip in candidates if ipaddress.ip_address(ip).is_private)
def local_ip_for_peer(peer_ip,peer_port):
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    try:
        sock.connect((peer_ip,int(peer_port)))
        address=sock.getsockname()[0]
        return address if address!='0.0.0.0' else local_ip()
    except OSError: return local_ip()
    finally: sock.close()
def fetch_json(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=25) as response: return json.loads(response.read().decode('utf-8'))
def latest_asset(repo,pattern):
    release=fetch_json(f'https://api.github.com/repos/{repo}/releases/latest'); regex=re.compile(pattern)
    for asset in release.get('assets',[]):
        if regex.search(asset.get('name','')): return {'name':asset['name'],'url':asset['browser_download_url'],'tag':release.get('tag_name',''),'size':asset.get('size')}
    return None
def download(url,destination,progress=None):
    temporary=destination.with_suffix(destination.suffix+'.part')
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=180) as response,open(temporary,'wb') as output:
            total=int(response.headers.get('Content-Length','0') or 0); received=0; started=time.monotonic()
            while True:
                block=response.read(1024*1024)
                if not block: break
                output.write(block); received+=len(block)
                if progress:
                    elapsed=max(time.monotonic()-started,.001); speed=received/elapsed
                    progress(received,total,speed,(total-received)/speed if total and speed else None)
        temporary.replace(destination)
    finally: temporary.unlink(missing_ok=True)
    return destination
def start_download_job(ids):
    job_id=str(int(time.time()*1000)); job={'id':job_id,'state':'queued','created':int(time.time()),'items':[]}
    with STATE_LOCK: STATE['jobs'][job_id]=job
    def runner():
        with STATE_LOCK: job['state']='running'
        for item in cfg()['items']:
            if item['id'] not in set(ids): continue
            record={'id':item['id'],'name':item['name'],'state':'resolving','received':0,'total':0,'speed':0,'eta':None}
            with STATE_LOCK: job['items'].append(record)
            try:
                asset=latest_asset(item['github_repo'],item.get('asset_regex',r'\.pkg$')) if item.get('github_repo') else None
                url=asset['url'] if asset else item.get('url'); name=asset['name'] if asset else item.get('filename')
                if not url or not name: raise RuntimeError('Keine nutzbare Downloadquelle')
                target=DL/Path(name).name
                if target.exists():
                    remember_download(item['id'],target)
                    record.update({'state':'already_downloaded','file':target.name,'received':target.stat().st_size,'total':target.stat().st_size}); continue
                record.update({'state':'downloading','file':target.name})
                def update(received,total,speed,eta):
                    with STATE_LOCK: record.update({'received':received,'total':total,'speed':round(speed,1),'eta':round(eta,1) if eta is not None else None})
                download(url,target,update); remember_download(item['id'],target); record.update({'state':'done','received':target.stat().st_size,'total':target.stat().st_size,'speed':0,'eta':0})
            except Exception as error: record.update({'state':'failed','error':str(error)})
        with STATE_LOCK: job['state']='done'; job['finished']=int(time.time())
        log_event('download',{'job':job_id,'items':job['items']})
    threading.Thread(target=runner,name=f'download-{job_id}',daemon=True).start()
    return job
def tcp_open(ip,port,timeout=.25):
    try:
        with socket.create_connection((ip,port),timeout=timeout): return True
    except OSError: return False
def rpi_api_port(ip,timeout=1.5):
    payload=json.dumps({'title_id':'CUSA00000'}).encode('utf-8')
    for port in RPI_PORTS:
        if not tcp_open(ip,port,timeout): continue
        request=urllib.request.Request(f'http://{ip}:{port}/api/is_exists',data=payload,headers={'Content-Type':'application/json'},method='POST')
        try:
            with urllib.request.urlopen(request,timeout=timeout) as response:
                if response.status==200: return port
        except urllib.error.HTTPError as error:
            if error.code not in (404,405): return port
        except (OSError,urllib.error.URLError): continue
    return None
def probe(ip):
    ports={str(port):tcp_open(ip,port,.8 if port in RPI_PORTS else .35) for port in (2121,9090,9020,9021,*RPI_PORTS)}
    rpi_port=rpi_api_port(ip) if any(ports[str(port)] for port in RPI_PORTS) else None
    # API verification is authoritative; don't let the earlier short TCP
    # probe leave a confirmed port rendered as closed in the UI.
    if rpi_port: ports[str(rpi_port)]=True
    if any(ports.values()): return {'ip':ip,'ports':ports,'remote_installer':bool(rpi_port),'rpi_port':rpi_port,'confidence':'install-ready' if rpi_port else 'candidate'}
def scan_ps4():
    subnets=set()
    for address in local_ipv4_addresses():
        try: subnets.add(ipaddress.ip_network(address+'/24',strict=False))
        except ValueError: continue
    hosts={str(host) for network in subnets for host in network.hosts() if str(host) not in local_ipv4_addresses()}
    with concurrent.futures.ThreadPoolExecutor(max_workers=96) as executor: found=[result for result in executor.map(probe,sorted(hosts)) if result]
    with STATE_LOCK: STATE['last_scan']=found
    return found
def package_url(filename,peer_ip,peer_port):
    from urllib.parse import quote
    return f'http://{local_ip_for_peer(peer_ip,peer_port)}:{PORT}/packages/{quote(filename)}'
def rpi_install(ps4_ip,port,package):
    # RPI's direct mode requires an array named "packages". The PS4 then
    # streams the PKG itself from the local HESPERIA HTTP server.
    payload=json.dumps({'type':'direct','packages':[package_url(package.name,ps4_ip,port)]}).encode('utf-8')
    request=urllib.request.Request(f'http://{ps4_ip}:{port}/api/install',data=payload,headers={'Content-Type':'application/json',**UA},method='POST')
    with urllib.request.urlopen(request,timeout=12) as response:
        raw=response.read().decode('utf-8',errors='replace')
        try: result=json.loads(raw)
        except json.JSONDecodeError: result={'raw':raw[:500]}
        return {'http_status':response.status,'response':result,'task_id':result.get('task_id') if isinstance(result,dict) else None}
def log_event(event,data):
    with open(LOG/'activity.jsonl','a',encoding='utf-8') as handle: handle.write(json.dumps({'at':time.strftime('%Y-%m-%dT%H:%M:%S'),'event':event,**data},ensure_ascii=False)+'\n')

class Handler(SimpleHTTPRequestHandler):
    server_version='HESPERIA/19'
    def log_message(self,fmt,*args): log_event('http',{'message':fmt%args})
    def translate_path(self,path):
        requested=unquote(urlparse(path).path)
        root,relative=(DL,requested.removeprefix('/packages/')) if requested.startswith('/packages/') else (WEB,requested.lstrip('/') or 'index.html')
        candidate=(root/relative).resolve()
        return str(candidate if candidate.is_relative_to(root.resolve()) else root/'__invalid__')
    def _json(self,value,status=200):
        payload=json.dumps(value,ensure_ascii=False).encode('utf-8'); self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Cache-Control','no-store'); self.send_header('Content-Length',str(len(payload))); self.end_headers(); self.wfile.write(payload)
    def _body(self):
        size=int(self.headers.get('Content-Length','0'))
        if size>1024*1024: raise ValueError('Anfrage ist zu groß')
        return json.loads(self.rfile.read(size) or b'{}')
    def send_head(self):
        if not urlparse(self.path).path.startswith('/packages/'):
            return super().send_head()
        path=Path(self.translate_path(self.path))
        try: source=open(path,'rb')
        except OSError:
            self.send_error(404,'Package not found'); return None
        size=os.fstat(source.fileno()).st_size; start=0; end=size-1; status=200
        requested=self.headers.get('Range')
        if requested:
            match=re.fullmatch(r'bytes=(\d*)-(\d*)',requested.strip(),re.IGNORECASE)
            if not match or size==0:
                source.close(); self.send_response(416); self.send_header('Content-Range',f'bytes */{size}'); self.send_header('Content-Length','0'); self.end_headers(); return None
            first,last=match.groups()
            if first:
                start=int(first); end=int(last) if last else size-1
                if start>=size or end<start:
                    source.close(); self.send_response(416); self.send_header('Content-Range',f'bytes */{size}'); self.send_header('Content-Length','0'); self.end_headers(); return None
                end=min(end,size-1)
            else:
                suffix=int(last or 0)
                if suffix<=0:
                    source.close(); self.send_response(416); self.send_header('Content-Range',f'bytes */{size}'); self.send_header('Content-Length','0'); self.end_headers(); return None
                start=max(0,size-suffix); end=size-1
            status=206
        length=max(0,end-start+1); source.seek(start)
        self._range_start=start; self._range_length=length
        self.send_response(status)
        self.send_header('Content-Type','application/octet-stream' if path.suffix.lower()=='.pkg' else (mimetypes.guess_type(path.name)[0] or 'application/octet-stream'))
        self.send_header('Last-Modified',formatdate(os.fstat(source.fileno()).st_mtime,usegmt=True))
        self.send_header('Accept-Ranges','bytes'); self.send_header('Content-Length',str(length)); self.send_header('Cache-Control','no-cache')
        if status==206: self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
        self.end_headers(); return source
    def copyfile(self, source, outputfile):
        requested=urlparse(self.path).path
        if not requested.startswith('/packages/'):
            return super().copyfile(source,outputfile)
        filename=Path(self.translate_path(self.path)).name
        total=Path(self.translate_path(self.path)).stat().st_size
        range_start=getattr(self,'_range_start',0); range_length=getattr(self,'_range_length',total)
        transfer={'id':str(time.time_ns()),'file':filename,'ip':self.client_address[0],'bytes':0,'total':total,'range_start':range_start,'range_length':range_length,'speed':0,'eta':None,'state':'sending','started':time.time()}
        with STATE_LOCK: STATE['transfers'].append(transfer); STATE['transfers']=STATE['transfers'][-256:]
        started=time.monotonic(); last_time=started; last_bytes=0
        try:
            remaining=range_length
            while remaining>0:
                block=source.read(min(256*1024,remaining))
                if not block: break
                outputfile.write(block)
                remaining-=len(block)
                now=time.monotonic()
                interval=max(now-last_time,.001)
                with STATE_LOCK: transfer['bytes']+=len(block)
                if interval>=.35 or transfer['bytes']==range_length:
                    speed=(transfer['bytes']-last_bytes)/interval
                    with STATE_LOCK: transfer.update({'speed':round(speed,1),'eta':round((range_length-transfer['bytes'])/speed,1) if speed>0 else None})
                    last_time=now; last_bytes=transfer['bytes']
            with STATE_LOCK: transfer.update({'state':'done' if transfer['bytes']==range_length else 'incomplete','eta':0 if transfer['bytes']==range_length else None,'speed':round(transfer['bytes']/max(time.monotonic()-started,.001),1),'finished':time.time()})
        except OSError as error:
            with STATE_LOCK: transfer.update({'state':'interrupted','error':str(error)[:160],'finished':time.time()})
    def do_GET(self):
        path=urlparse(self.path).path
        if path=='/api/status':
            downloads=[{'name':item.name,'size':item.stat().st_size,'pkg':item.suffix.lower()=='.pkg'} for item in DL.iterdir() if item.is_file() and not item.name.endswith('.part')]
            with STATE_LOCK:
                state={key:STATE[key] for key in ('ps4','queue','last_scan','started')}
                state['transfers']=[dict(item) for item in STATE['transfers']]
            return self._json({'ok':True,'version':'19.0','http_port':PORT,'local_url':f'http://127.0.0.1:{PORT}','lan_url':f'http://{local_ip()}:{PORT}','local_ips':local_ipv4_addresses(),'downloads':downloads,**state})
        if path=='/api/catalog':
            # Return local catalog immediately. GitHub checks happen only after
            # the user asks to download a package, so the first render is fast.
            c=cfg(); return self._json({'items':c['items'],'presets':c.get('presets',{}),'sources':'local catalog; live release lookup starts on download'})
        if path=='/api/discover': return self._json({'local_ip':local_ip(),'candidates':scan_ps4(),'note':'RPI wird auf TCP-Port 12800 und 12801 geprüft.'})
        if path.startswith('/api/jobs/'):
            job_id=path.rsplit('/',1)[-1]
            with STATE_LOCK: job=STATE['jobs'].get(job_id)
            return self._json(job if job else {'error':'Download-Auftrag nicht gefunden'},200 if job else 404)
        if path=='/api/queue':
            with STATE_LOCK: return self._json({'queue':STATE['queue'],'ps4':STATE['ps4']})
        return super().do_GET()
    def do_POST(self):
        try:
            path=urlparse(self.path).path
            if path=='/api/import':
                name=Path(unquote(urlparse(self.path).query.removeprefix('name='))).name
                if not name.lower().endswith('.pkg'): return self._json({'error':'Nur .pkg-Dateien können importiert werden.'},400)
                size=int(self.headers.get('Content-Length','0'))
                if size<=0: return self._json({'error':'Leere Datei.'},400)
                destination=DL/name; temporary=destination.with_suffix(destination.suffix+'.part'); received=0
                try:
                    with open(temporary,'wb') as output:
                        while received<size:
                            block=self.rfile.read(min(1024*1024,size-received))
                            if not block: raise ConnectionError('Upload unterbrochen')
                            output.write(block); received+=len(block)
                    temporary.replace(destination)
                finally: temporary.unlink(missing_ok=True)
                log_event('import',{'file':name,'bytes':received})
                return self._json({'ok':True,'file':name,'bytes':received,'sha256':sha256(destination)})
            body,path=self._body(),path
            if path=='/api/download':
                wanted=[item['id'] for item in cfg()['items'] if item['id'] in set(body.get('ids',[]))]
                if not wanted: return self._json({'error':'Keine gültigen Pakete ausgewählt.'},400)
                return self._json(start_download_job(wanted),202)
            if path=='/api/connect':
                ip=str(body.get('ip','')).strip()
                try: ipaddress.ip_address(ip)
                except ValueError: return self._json({'ok':False,'error':'Ungültige PS4-IP'},400)
                rpi_port=rpi_api_port(ip); ready=bool(rpi_port); pc_ip=local_ip_for_peer(ip,rpi_port or RPI_PORTS[0]); entry={'ip':ip,'port':rpi_port,'remote_installer':ready,'pc_ip':pc_ip,'pc_url':f'http://{pc_ip}:{PORT}','connected_at':int(time.time())}
                with STATE_LOCK: STATE['ps4']=entry if ready else None
                log_event('connect',entry)
                open_rpi_ports=[port for port in RPI_PORTS if tcp_open(ip,port)]
                error=None if ready else ('TCP-Port '+', '.join(map(str,open_rpi_ports))+' ist offen, aber die RPI-API antwortet nicht passend. RPI auf der PS4 öffnen und PC/PS4 im selben LAN prüfen.' if open_rpi_ports else 'Kein RPI-Port 12800/12801 offen. Remote Package Installer auf der PS4 starten; PC und PS4 müssen im selben LAN sein.')
                return self._json({'ok':ready,'ps4':entry if ready else None,'open_rpi_ports':open_rpi_ports,'error':error},200 if ready else 409)
            if path=='/api/rpi/progress':
                ip=str(body.get('ip','')); task_id=body.get('task_id')
                try: ipaddress.ip_address(ip)
                except ValueError: return self._json({'error':'Ungültige PS4-IP'},400)
                port=int(body.get('port',RPI_PORTS[0]));
                if port not in RPI_PORTS: return self._json({'error':'Ungültiger RPI-Port'},400)
                request=urllib.request.Request(f'http://{ip}:{port}/api/get_task_progress',data=json.dumps({'task_id':task_id}).encode(),headers={'Content-Type':'application/json'},method='POST')
                with urllib.request.urlopen(request,timeout=8) as response: raw=response.read().decode('utf-8',errors='replace')
                normalized=re.sub(r'(:\s*)0x([0-9a-fA-F]+)(?=\s*[,}])',lambda match:match.group(1)+str(int(match.group(2),16)),raw)
                try: progress=json.loads(normalized)
                except json.JSONDecodeError: progress={'raw':raw[:2000]}
                with STATE_LOCK:
                    for task in STATE.get('rpi_tasks',[]):
                        if str(task.get('task_id'))==str(task_id): task.update({'progress':progress,'last_update':int(time.time())})
                return self._json({'ok':True,'progress':progress})
            if path=='/api/download-rpi':
                rpi_url=body.get('url')
                if rpi_url not in ('https://pkg-zone.com/details/Fltz00003',): return self._json({'error':'RPI wird nur über die geprüfte Paketquelle geöffnet.'},400)
                return self._json({'ok':True,'url':rpi_url,'message':'Die Originalquelle stellt keine Binärdatei direkt bereit. Öffne dort den RPI-Eintrag und lade die PKG-Datei manuell herunter.'})
            if path=='/api/export':
                selected_ids=set(body.get('ids',[]))
                selected_files={Path(str(name)).name for name in body.get('files',[])}
                export_root=USB/('HESPERIA_USB_INSTALL_'+time.strftime('%Y%m%d_%H%M%S'))
                pkg_dir, data_dir=export_root/'PKG', export_root/'DATA'
                pkg_dir.mkdir(parents=True); data_dir.mkdir(parents=True)
                copied=[]; missing_items=[]
                for item in cfg()['items']:
                    if item['id'] not in selected_ids: continue
                    entry=read_download_index().get(item['id'])
                    if not entry:
                        missing_items.append(item['name']); continue
                    source=DL/Path(entry['file']).name
                    if not source.is_file(): continue
                    target=(pkg_dir if source.suffix.lower()=='.pkg' else data_dir)/source.name
                    shutil.copy2(source,target)
                    copied.append({'id':item['id'],'file':target.relative_to(export_root).as_posix(),'bytes':target.stat().st_size,'sha256':sha256(target)})
                for name in selected_files:
                    source=DL/name
                    if source.is_file() and source.suffix.lower()=='.pkg':
                        target=pkg_dir/source.name
                        if not target.exists(): shutil.copy2(source,target)
                        if not any(entry['file']==target.relative_to(export_root).as_posix() for entry in copied):
                            copied.append({'id':'local_pkg','file':target.relative_to(export_root).as_posix(),'bytes':target.stat().st_size,'sha256':sha256(target)})
                bootstrap=pkg_dir/'Remote_Package_Installer.pkg'
                if bootstrap.exists():
                    bootstrap_note='Remote Package Installer wurde gefunden und liegt unter PKG/ bereit.'
                else:
                    bootstrap_note='Für die einmalige RPI-Einrichtung die rechtmäßig bezogene Datei Remote_Package_Installer.pkg in diesen PKG-Ordner kopieren und auf der PS4 über den normalen Package Installer installieren.'
                (export_root/'README_INSTALLATION.txt').write_text(
                    'HESPERIA USB-Auswahl\n\n1. GoldHEN auf der eigenen PS4 aktivieren.\n2. USB-Stick einstecken und die PKGs unter PKG über den normalen Package Installer installieren.\n3. Für LAN-Automatisierung Remote Package Installer einmalig installieren und auf der PS4 starten.\n4. Danach HESPERIA am PC/PS4-Browser öffnen, PS4 suchen, Auswahl herunterladen und automatisch übergeben.\n\n'+bootstrap_note+'\n\nDatenbanken unter DATA sind keine installierbaren PKGs.\n',encoding='utf-8')
                (export_root/'MANIFEST.json').write_text(json.dumps(copied,ensure_ascii=False,indent=2),encoding='utf-8')
                log_event('usb_export',{'count':len(copied),'ids':list(selected_ids)})
                return self._json({'ok':True,'path':str(export_root),'files':copied,'not_downloaded':missing_items,'bootstrap_note':bootstrap_note})
            if path=='/api/install':
                requested=[Path(str(name)).name for name in body.get('files',[])]
                selected_ids=set(body.get('ids',[]))
                download_index=read_download_index(); missing=[]
                for item in cfg()['items']:
                    if item['id'] not in selected_ids: continue
                    entry=download_index.get(item['id'])
                    if entry: requested.append(Path(entry['file']).name)
                    else: missing.append(item['name'])
                requested=list(dict.fromkeys(requested))
                with STATE_LOCK: ps4=STATE['ps4']
                if not ps4: return self._json({'ok':False,'error':'Keine installierbereite PS4 verbunden.'},409)
                if missing: return self._json({'ok':False,'error':'Diese Auswahl bitte zuerst herunterladen: '+', '.join(missing)},409)
                if not requested: return self._json({'ok':False,'error':'Keine heruntergeladenen oder importierten Dateien ausgewählt.'},400)
                packages=[DL/name for name in requested]; invalid=[item.name for item in packages if not item.is_file() or item.suffix.lower()!='.pkg']
                if invalid: return self._json({'ok':False,'error':'Nur vorhandene .pkg-Dateien können übergeben werden.','invalid':invalid},400)
                submitted=[]
                for package in packages:
                    record={'file':package.name,'url':package_url(package.name,ps4['ip'],ps4['port']),'state':'submitting','at':int(time.time())}
                    try: record.update({'state':'submitted','remote':rpi_install(ps4['ip'],ps4['port'],package)})
                    except (OSError,urllib.error.URLError,urllib.error.HTTPError) as error: record.update({'state':'failed','error':str(error)})
                    submitted.append(record)
                with STATE_LOCK: STATE['queue']=(submitted+STATE['queue'])[:50]
                log_event('install',{'ps4':ps4['ip'],'items':submitted}); return self._json({'ok':all(item['state']=='submitted' for item in submitted),'items':submitted,'note':'Übergabe bestätigt. Den Fortschritt zeigt der Package Installer auf der PS4 an.'})
            return self._json({'error':'Unbekannter Endpunkt'},404)
        except Exception as error:
            log_event('error',{'error':repr(error)}); return self._json({'error':str(error)},500)

if __name__=='__main__':
    if not WEB.is_dir() or not CFG.is_file():
        raise RuntimeError(f'Programmdateien fehlen (Oberfläche: {WEB}, Konfiguration: {CFG}). Bitte EXE neu herunterladen oder Projektordner vollständig entpacken.')
    os.chdir(WEB)
    httpd=None
    for candidate in range(PORT, PORT+10):
        # On Windows SO_REUSEADDR may otherwise let two local servers claim the
        # same port. Always reserve a genuinely unused address first.
        if tcp_open('127.0.0.1',candidate,.15):
            continue
        try:
            httpd=ThreadingHTTPServer(('0.0.0.0',candidate),Handler)
            PORT=candidate
            break
        except OSError:
            continue
    if not httpd:
        raise RuntimeError('Kein freier Port zwischen 8088 und 8097 verfügbar.')
    pc_url=f'http://127.0.0.1:{PORT}'
    print('HESPERIA PS4 Control Center v19')
    print('PC :',pc_url)
    print('PS4:',', '.join(f'http://{address}:{PORT}' for address in local_ipv4_addresses()))
    print('Windows-Firewall beim ersten Start für private Netzwerke erlauben.')
    if os.environ.get('HESPERIA_NO_BROWSER') != '1': webbrowser.open(pc_url)
    try: httpd.serve_forever()
    except KeyboardInterrupt: pass
