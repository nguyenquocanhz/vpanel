/* VPS Panel - File Manager JS */
let currentPath='/',ctxTarget=null,editingPath='';
const FOLDER='<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="rgba(245,158,11,.2)" stroke="#f59e0b" stroke-width="1.5"><path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/></svg>';
const FILEX='<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" stroke-width="1.5"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/></svg>';

function showToast(m,t='success'){const c=document.getElementById('toastContainer');if(!c)return;const d=document.createElement('div');d.className='toast '+t;d.textContent=m;c.appendChild(d);setTimeout(()=>d.remove(),3500);}

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
    parts.forEach(p=>{acc+='/'+p;html+=`<span class="sep">/</span><a href="#" onclick="navigate('${acc}');return false;">${p}</a>`;});
    bc.innerHTML=html;
}

function renderGrid(items){
    const grid=document.getElementById('fileGrid');
    if(!items.length){grid.innerHTML='<p class="text-muted text-sm">Empty directory</p>';return;}
    grid.innerHTML=items.map(f=>`
        <div class="file-item" ondblclick="${f.is_dir?`navigate('${f.path}')`:`editFile('${f.path}')`}" oncontextmenu="showCtx(event,'${f.path}',${f.is_dir})">
            <div class="file-icon">${f.is_dir?FOLDER:FILEX}</div>
            <div class="file-name">${f.name}</div>
            <div class="file-meta">${f.is_dir?'Folder':f.size_human||''}</div>
        </div>`).join('');
}

function goUp(){if(currentPath==='/')return;navigate(currentPath.replace(/\/[^/]+\/?$/,'')||'/');}
function toggleUpload(){document.getElementById('uploadZone').classList.toggle('visible');}

async function uploadFiles(files){
    for(const file of files){
        const fd=new FormData();fd.append('file',file);
        try{const r=await Auth.apiFetch('/api/files/upload?directory='+encodeURIComponent(currentPath),{method:'POST',body:fd,isFormData:true});
        const d=await r.json();showToast(d.message||d.error,d.success?'success':'error');}catch(e){showToast(e.message,'error');}
    }
    navigate(currentPath);document.getElementById('uploadZone').classList.remove('visible');
}

async function editFile(path){
    try{const r=await Auth.apiFetch('/api/files/read?path='+encodeURIComponent(path));
    const d=await r.json();if(!d.success){showToast(d.error,'error');return;}
    editingPath=path;document.getElementById('editorTitle').textContent=path.split('/').pop();
    document.getElementById('editorContent').value=d.content;document.getElementById('editorOverlay').classList.add('active');
    }catch(e){showToast(e.message,'error');}
}

async function saveFile(){
    const content=document.getElementById('editorContent').value;
    try{const r=await Auth.apiFetch('/api/files/write',{method:'POST',body:JSON.stringify({path:editingPath,content})});
    const d=await r.json();showToast(d.message||d.error,d.success?'success':'error');if(d.success)closeEditor();
    }catch(e){showToast(e.message,'error');}
}

function closeEditor(){document.getElementById('editorOverlay').classList.remove('active');editingPath='';}

async function promptNewFolder(){const name=prompt('Folder name:');if(!name)return;
    try{const r=await Auth.apiFetch('/api/files/mkdir',{method:'POST',body:JSON.stringify({path:currentPath+'/'+name})});
    const d=await r.json();showToast(d.message||d.error,d.success?'success':'error');if(d.success)navigate(currentPath);
    }catch(e){showToast(e.message,'error');}
}

function showCtx(e,path,isDir){e.preventDefault();ctxTarget={path,isDir};
    const m=document.getElementById('ctxMenu');m.style.left=e.clientX+'px';m.style.top=e.clientY+'px';m.classList.add('active');}
document.addEventListener('click',()=>document.getElementById('ctxMenu').classList.remove('active'));

function ctxOpen(){if(ctxTarget.isDir)navigate(ctxTarget.path);else editFile(ctxTarget.path);}
function ctxEdit(){if(!ctxTarget.isDir)editFile(ctxTarget.path);}
async function ctxRename(){const name=prompt('New name:',ctxTarget.path.split('/').pop());if(!name)return;
    try{const r=await Auth.apiFetch('/api/files/rename',{method:'POST',body:JSON.stringify({path:ctxTarget.path,new_name:name})});
    const d=await r.json();showToast(d.message||d.error,d.success?'success':'error');if(d.success)navigate(currentPath);}catch(e){showToast(e.message,'error');}
}
async function ctxDelete(){if(!confirm('Delete '+ctxTarget.path+'?'))return;
    try{const r=await Auth.apiFetch('/api/files/delete',{method:'POST',body:JSON.stringify({path:ctxTarget.path})});
    const d=await r.json();showToast(d.message||d.error,d.success?'success':'error');if(d.success)navigate(currentPath);}catch(e){showToast(e.message,'error');}
}

const uz=document.getElementById('uploadZone');
document.addEventListener('dragover',e=>{e.preventDefault();uz.classList.add('visible','dragover');});
document.addEventListener('dragleave',e=>{if(!e.relatedTarget)uz.classList.remove('dragover');});
document.addEventListener('drop',e=>{e.preventDefault();uz.classList.remove('dragover');if(e.dataTransfer.files.length)uploadFiles(e.dataTransfer.files);});

document.addEventListener('DOMContentLoaded',()=>navigate('/'));
