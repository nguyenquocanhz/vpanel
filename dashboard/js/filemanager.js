/* VPS Panel - File Manager JS (Enhanced) */
let currentPath='/',ctxTarget=null,editingPath='',editorModified=false;

const FOLDER='<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="rgba(245,158,11,.2)" stroke="#f59e0b" stroke-width="1.5"><path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/></svg>';
const FILEX='<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" stroke-width="1.5"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/></svg>';

function showToast(m,t='success'){const c=document.getElementById('toastContainer');if(!c)return;const d=document.createElement('div');d.className='toast '+t;d.textContent=m;c.appendChild(d);setTimeout(()=>d.remove(),3500);}

/* ── Navigation ── */
async function navigate(path){
    currentPath=path||'/';
    try{
        const r=await Auth.apiFetch('/api/files/list?path='+encodeURIComponent(currentPath));
        if(!r)return;const d=await r.json();
        if(!d.success){showToast(d.error,'error');return;}
        currentPath=d.path;renderBreadcrumb(d.path);renderGrid(d.items);
    }catch(e){showToast(e.message,'error');}
}

function renderBreadcrumb(path){
    const bc=document.getElementById('breadcrumb');
    const parts=path.split('/').filter(Boolean);
    let html='<a href="#" onclick="navigate(\'/\');return false;">/</a>';
    let acc='';
    parts.forEach(p=>{acc+='/'+p;html+=`<span class="sep">›</span><a href="#" onclick="navigate('${acc}');return false;">${p}</a>`;});
    bc.innerHTML=html;
}

function renderGrid(items){
    const grid=document.getElementById('fileGrid');
    if(!items.length){grid.innerHTML='<p class="text-muted text-sm" style="padding:2rem;text-align:center">Empty directory</p>';return;}
    grid.innerHTML=items.map(f=>`
        <div class="file-item" ondblclick="itemDblClick(event,'${f.path}',${f.is_dir})" oncontextmenu="showCtx(event,'${f.path}',${f.is_dir},'${(f.permissions||'').replace(/'/g,'')}','${f.name}')" onclick="selectItem(event,this)">
            <div class="file-icon">${f.is_dir?FOLDER:FILEX}</div>
            <div class="file-name">${f.name}</div>
            <div class="file-meta">${f.is_dir?'Folder':f.size_human||''}</div>
        </div>`).join('');
}

function selectItem(e,el){
    if(e.button!==0)return;
    document.querySelectorAll('.file-item.selected').forEach(i=>i.classList.remove('selected'));
    el.classList.add('selected');
}

function itemDblClick(e,path,isDir){
    e.preventDefault();e.stopPropagation();
    if(isDir)navigate(path);else editFile(path);
}

function goUp(){if(currentPath==='/')return;navigate(currentPath.replace(/\/[^/]+\/?$/,'')||'/');}
function toggleUpload(){document.getElementById('uploadZone').classList.toggle('visible');}

/* ── Upload ── */
async function uploadFiles(files){
    for(const file of files){
        const fd=new FormData();fd.append('file',file);
        try{const r=await Auth.apiFetch('/api/files/upload?directory='+encodeURIComponent(currentPath),{method:'POST',body:fd,isFormData:true});
        const d=await r.json();showToast(d.message||d.error,d.success?'success':'error');}catch(e){showToast(e.message,'error');}
    }
    navigate(currentPath);document.getElementById('uploadZone').classList.remove('visible');
}

/* ── Editor ── */
async function editFile(path){
    try{const r=await Auth.apiFetch('/api/files/read?path='+encodeURIComponent(path));
    const d=await r.json();if(!d.success){showToast(d.error,'error');return;}
    editingPath=path;editorModified=false;
    document.getElementById('editorTitle').textContent=path.split('/').pop();
    document.getElementById('editorPath').textContent=path;
    const ta=document.getElementById('editorContent');
    ta.value=d.content;
    updateLineInfo(ta);
    document.getElementById('editorOverlay').classList.add('active');
    ta.focus();
    }catch(e){showToast(e.message,'error');}
}

function updateLineInfo(ta){
    const val=ta.value.substring(0,ta.selectionStart);
    const line=val.split('\n').length;
    const col=val.split('\n').pop().length+1;
    const total=ta.value.split('\n').length;
    document.getElementById('lineInfo').textContent=`Ln ${line}, Col ${col}`;
    document.getElementById('totalLines').textContent=`${total} lines • ${(ta.value.length/1024).toFixed(1)} KB`;
}

async function saveFile(){
    const content=document.getElementById('editorContent').value;
    try{const r=await Auth.apiFetch('/api/files/write',{method:'POST',body:JSON.stringify({path:editingPath,content})});
    const d=await r.json();showToast(d.message||d.error,d.success?'success':'error');
    if(d.success){editorModified=false;document.getElementById('editorTitle').textContent=editingPath.split('/').pop();}
    }catch(e){showToast(e.message,'error');}
}

function closeEditor(){
    if(editorModified&&!confirm('Unsaved changes. Close anyway?'))return;
    document.getElementById('editorOverlay').classList.remove('active');editingPath='';editorModified=false;
}

/* ── New Folder ── */
async function promptNewFolder(){const name=prompt('Folder name:');if(!name)return;
    try{const r=await Auth.apiFetch('/api/files/mkdir',{method:'POST',body:JSON.stringify({path:currentPath+'/'+name})});
    const d=await r.json();showToast(d.message||d.error,d.success?'success':'error');if(d.success)navigate(currentPath);
    }catch(e){showToast(e.message,'error');}
}

/* ── Context Menu ── */
function showCtx(e,path,isDir,perms,name){
    e.preventDefault();e.stopPropagation();
    ctxTarget={path,isDir,perms,name};
    const m=document.getElementById('ctxMenu');
    // Position with bounds check
    const x=Math.min(e.clientX,window.innerWidth-220);
    const y=Math.min(e.clientY,window.innerHeight-280);
    m.style.left=x+'px';m.style.top=y+'px';
    m.classList.add('active');
}

document.addEventListener('click',()=>document.getElementById('ctxMenu')?.classList.remove('active'));
document.addEventListener('contextmenu',e=>{
    if(!e.target.closest('.file-item'))document.getElementById('ctxMenu')?.classList.remove('active');
});

function ctxOpen(){if(!ctxTarget)return;if(ctxTarget.isDir)navigate(ctxTarget.path);else editFile(ctxTarget.path);}

function ctxEdit(){if(!ctxTarget||ctxTarget.isDir)return;editFile(ctxTarget.path);}

async function ctxRename(){
    if(!ctxTarget)return;
    const name=prompt('Rename to:',ctxTarget.name);
    if(!name||name===ctxTarget.name)return;
    try{const r=await Auth.apiFetch('/api/files/rename',{method:'POST',body:JSON.stringify({path:ctxTarget.path,new_name:name})});
    const d=await r.json();showToast(d.message||d.error,d.success?'success':'error');if(d.success)navigate(currentPath);}catch(e){showToast(e.message,'error');}
}

async function ctxDelete(){
    if(!ctxTarget)return;
    if(!confirm('Delete "'+ctxTarget.name+'"?\nPath: '+ctxTarget.path))return;
    try{const r=await Auth.apiFetch('/api/files/delete',{method:'POST',body:JSON.stringify({path:ctxTarget.path})});
    const d=await r.json();showToast(d.message||d.error,d.success?'success':'error');if(d.success)navigate(currentPath);}catch(e){showToast(e.message,'error');}
}

function ctxDownload(){
    if(!ctxTarget||ctxTarget.isDir)return;
    const token=localStorage.getItem('vpspanel_token');
    window.open('/api/files/download?path='+encodeURIComponent(ctxTarget.path));
}

/* ── Chmod Modal ── */
function ctxChmod(){
    if(!ctxTarget)return;
    document.getElementById('chmodPath').textContent=ctxTarget.name;
    document.getElementById('chmodInput').value='755';
    // Parse current permissions
    const p=ctxTarget.perms;
    if(p&&p.length>=10){
        const bits=[p[1]==='r',p[2]==='w',p[3]!=='-',p[4]==='r',p[5]==='w',p[6]!=='-',p[7]==='r',p[8]==='w',p[9]!=='-'];
        const ids=['or','ow','ox','gr','gw','gx','wr','ww','wx'];
        ids.forEach((id,i)=>{const cb=document.getElementById(id);if(cb)cb.checked=bits[i];});
        updateChmodPreview();
    }
    document.getElementById('chmodModal').classList.add('active');
}

function updateChmodPreview(){
    const o=(document.getElementById('or').checked?4:0)+(document.getElementById('ow').checked?2:0)+(document.getElementById('ox').checked?1:0);
    const g=(document.getElementById('gr').checked?4:0)+(document.getElementById('gw').checked?2:0)+(document.getElementById('gx').checked?1:0);
    const w=(document.getElementById('wr').checked?4:0)+(document.getElementById('ww').checked?2:0)+(document.getElementById('wx').checked?1:0);
    const mode=''+o+g+w;
    document.getElementById('chmodInput').value=mode;
    document.getElementById('chmodPreview').textContent=mode;
}

async function applyChmod(){
    const mode=document.getElementById('chmodInput').value.trim();
    if(!/^[0-7]{3,4}$/.test(mode)){showToast('Invalid mode','error');return;}
    try{const r=await Auth.apiFetch('/api/files/chmod',{method:'POST',body:JSON.stringify({path:ctxTarget.path,mode})});
    const d=await r.json();showToast(d.message||d.error,d.success?'success':'error');
    if(d.success){document.getElementById('chmodModal').classList.remove('active');navigate(currentPath);}
    }catch(e){showToast(e.message,'error');}
}

/* ── Drag & Drop ── */
const uz=document.getElementById('uploadZone');
if(uz){
    document.addEventListener('dragover',e=>{e.preventDefault();uz.classList.add('visible','dragover');});
    document.addEventListener('dragleave',e=>{if(!e.relatedTarget)uz.classList.remove('dragover');});
    document.addEventListener('drop',e=>{e.preventDefault();uz.classList.remove('dragover');if(e.dataTransfer.files.length)uploadFiles(e.dataTransfer.files);});
}

/* ── Keyboard Shortcuts ── */
document.addEventListener('keydown',e=>{
    if(e.key==='Escape'){
        document.getElementById('ctxMenu')?.classList.remove('active');
        document.getElementById('chmodModal')?.classList.remove('active');
    }
    // Ctrl+S in editor
    if(e.ctrlKey&&e.key==='s'&&editingPath){e.preventDefault();saveFile();}
});

/* ── Editor events ── */
document.addEventListener('DOMContentLoaded',()=>{
    navigate('/');
    const ta=document.getElementById('editorContent');
    if(ta){
        ta.addEventListener('input',()=>{
            editorModified=true;
            document.getElementById('editorTitle').textContent='● '+editingPath.split('/').pop();
            updateLineInfo(ta);
        });
        ta.addEventListener('click',()=>updateLineInfo(ta));
        ta.addEventListener('keyup',()=>updateLineInfo(ta));
        // Tab support
        ta.addEventListener('keydown',e=>{
            if(e.key==='Tab'){
                e.preventDefault();
                const s=ta.selectionStart,end=ta.selectionEnd;
                ta.value=ta.value.substring(0,s)+'    '+ta.value.substring(end);
                ta.selectionStart=ta.selectionEnd=s+4;
            }
        });
    }
});
