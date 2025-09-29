import os, torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification

def _find_model_dir():
    env = os.getenv("SC_MODEL_DIR")
    if env and Path(env).exists():
        return Path(env)

    here = Path(__file__).resolve()
    candidates = [
    
        here.parent.parent / "ml_models" / "final_model",
        
        here.parents[2] / "ml_models" / "final_model",
    ]
    for c in candidates:
        if c.exists():
            return c

    raise RuntimeError("Model folder not found. Tried: " + " | ".join(str(c) for c in candidates))

MODEL_DIR = _find_model_dir()

_TOKENIZER = None
_MODEL = None
_DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

CUSTOM_ID2LABEL = {
    0: "Certificates_Documents",
    1: "Courses_Training",
    2: "Facilities_Logistics",
    3: "Finance_Admin",
    4: "IT_Support"
}

def _get_id2label(model):
    
    cfg_map = getattr(model.config, "id2label", None)
    if isinstance(cfg_map, dict) and cfg_map:

        vals = [str(v) for v in cfg_map.values()]
        if not any(v.startswith("LABEL_") for v in vals):
  
            return {int(k): v for k, v in cfg_map.items()}
    return CUSTOM_ID2LABEL

def _load_once():
    global _TOKENIZER, _MODEL
    if _TOKENIZER is not None and _MODEL is not None:
        return _TOKENIZER, _MODEL

    
    _TOKENIZER = AutoTokenizer.from_pretrained(str(MODEL_DIR), local_files_only=True)
    _MODEL = AutoModelForSequenceClassification.from_pretrained(str(MODEL_DIR), local_files_only=True)
    _MODEL.to(_DEVICE)
    _MODEL.eval()
    return _TOKENIZER, _MODEL

@torch.inference_mode()
def predict_category(text: str):
    tok, model = _load_once()
    enc = tok(text, truncation=True, padding=True, max_length=256, return_tensors="pt")
    enc = {k: v.to(_DEVICE) for k, v in enc.items()}
    logits = model(**enc).logits
    probs = torch.softmax(logits, dim=-1).squeeze(0)
    score, pred_id = torch.max(probs, dim=-1)
    label_map = _get_id2label(model)
    label = label_map.get(int(pred_id), f"class_{int(pred_id)}")

    return {"label": label, "score": float(score)}

# <div id="ai-result" class="hidden">
#             <p id="ai-meta" class="font-medium"></p>
#             <p id="ai-summary" class="mt-1 text-sm text-gray-700"></p>
#             <div id="ai-steps" class="mt-2"></div>
#             <div id="ai-verify" class="mt-4"></div>
#             <!-- actions appear after analysis -->
#             <div id="ai-actions" class="hidden mt-4 flex gap-3">
#               <button type="button" id="open-ticket-btn" class="btn-primary hidden"
#                       onclick="revealForm('nontech')">Open Ticket</button>
#               <button type="button" id="escalate-btn" class="btn-primary hidden"
#                       onclick="revealForm('tech')">Escalate to Support</button>
#             </div>
#           </div>
#         </div>
#       </div>

#       <!-- 2) FULL FORM (HIDDEN until student chooses action) -->
#       <div id="full-form" class="card hidden">
#         <div class="card-header">
#           <h3 class="text-base font-semibold">Query Form</h3>
#         </div>
#         <div class="p-6">
#           <form id="queryForm" method="POST" action="">
#             {% csrf_token %}

#             <!-- hidden ai fields that get posted -->
#             <input type="hidden" name="ai_is_technical" id="ai_is_technical" />
#             <input type="hidden" name="ai_category"     id="ai_category" />
#             <input type="hidden" name="ai_record_id"    id="ai_record_id" />

#             <div class="space-y-6">
#               <div>
#                 <label for="category" class="block text-sm font-medium text-gray-700 mb-1">Query Category</label>
#                 <select id="category" name="category" class="w-full border-gray-300 rounded-md shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-20">
#                   <option value="">Select a category</option>
#                   <option value="IT_Support">IT Support</option>
#                   <option value="Facilities_Logistics">Maintenance / Facilities</option>
#                   <option value="Finance_Admin">Finance & Admin</option>
#                   <option value="Certificates_Documents">Certificates & Documents</option>
#                   <option value="Courses_Training">Courses & Training</option>
#                 </select>
#               </div>

#               <div>
#                 <label for="subject" class="block text-sm font-medium text-gray-700 mb-1">Subject</label>
#                 <input type="text" id="subject" name="title" placeholder="Brief title for your query" class="w-full border-gray-300 rounded-md shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-20">
#               </div>

#               <div>
#                 <label for="priority" class="block text-sm font-medium text-gray-700 mb-1">Priority</label>
#                 <select id="priority" name="priority" class="w-full border-gray-300 rounded-md shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-20">
#                   <option value="Low">Low</option>
#                   <option value="Medium" selected>Medium</option>
#                   <option value="High">High</option>
#                 </select>
#               </div>

#               <div>
#                 <label for="description" class="block text-sm font-medium text-gray-700 mb-1">Description</label>
#                 <textarea id="description" name="description" rows="6" placeholder="Please provide details about your query" class="w-full border-gray-300 rounded-md shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-20"></textarea>
#               </div>

#               <div>
#                 <label for="file-upload" class="block text-sm font-medium text-gray-700 mb-1">Attachments (Optional)</label>
#                 <div class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
#                   <div class="space-y-1 text-center">
#                     <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true">
#                       <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4h-12m4-12v8m0 0v4m0 0h12a4 4 0 00.01-1v-7m-4 0h-12" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
#                     </svg>
#                     <div class="flex text-sm text-gray-600">
#                       <label for="file-upload" class="relative cursor-pointer rounded-md font-medium text-primary hover:text-primary">
#                         <span>Upload a file</span>
#                         <input id="file-upload" name="file-upload" type="file" class="sr-only">
#                       </label>
#                       <p class="pl-1">or drag and drop</p>
#                     </div>
#                     <p class="text-xs text-gray-500">PNG, JPG, PDF up to 10MB</p>
#                   </div>
#                 </div>
#               </div>
# <div class="flex items-start">
#                 <div class="flex items-center h-5">
#                   <input id="terms" name="terms" type="checkbox" class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded">
#                 </div>
#                 <div class="ml-3 text-sm">
#                   <label for="terms" class="font-medium text-gray-700">I acknowledge that my query will be reviewed by the appropriate department staff</label>
#                 </div>
#               </div>

#               <div class="flex justify-end space-x-3">
#                 <a href="{% url 'student_dashboard' %}" class="btn-ghost">Cancel</a>
#                 <button id="submitBtn" type="submit" class="btn-primary">Submit Query</button>
#               </div>
"""
  <script>
    // CSRF helper
    function getCookie(name){
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop().split(';').shift();
    }

    // reveal the full form after the student chooses to open/escalate
    function revealForm(mode){
      const full = document.getElementById('full-form');
      const aiDesc = document.getElementById('ai_description');
      const formDesc = document.getElementById('description');
      const submitBtn = document.getElementById('submitBtn');

      // copy description from AI box into the real form
      formDesc.value = aiDesc.value || '';

      // label the submit button
      submitBtn.textContent = (mode === 'tech') ? 'Escalate to Support' : 'Open Ticket';

      full.classList.remove('hidden');
      // scroll into view nicely
      setTimeout(() => full.scrollIntoView({ behavior:'smooth', block:'start' }), 50);
    }

    (function(){
      const runBtn   = document.getElementById('ai-run');
      const statusEl = document.getElementById('ai-status');
      const box      = document.getElementById('ai-result');
      const meta     = document.getElementById('ai-meta');
      const summary  = document.getElementById('ai-summary');
      const stepsBox = document.getElementById('ai-steps');
      const verifyBox= document.getElementById('ai-verify');
      const aiDesc   = document.getElementById('ai_description');

      const nonTechBtn = document.getElementById('open-ticket-btn');
      const techBtn    = document.getElementById('escalate-btn');
      const actions    = document.getElementById('ai-actions');

      // hidden fields on the real form
      const hidTech  = document.getElementById('ai_is_technical');
      const hidCat   = document.getElementById('ai_category');
      const hidId    = document.getElementById('ai_record_id');

      function renderSteps(steps){
        stepsBox.innerHTML = '';
        if (!Array.isArray(steps) || !steps.length) return;

        const title = document.createElement('div');
        title.className = 'font-semibold mt-2';
        title.textContent = 'Steps to apply';
        stepsBox.appendChild(title);

        const ol = document.createElement('ol');
        ol.className = 'list-decimal pl-6 text-sm text-gray-700 space-y-2';
        steps.forEach(s => {
          const li = document.createElement('li');

          // s can be a string or { text, commands }
          const text   = (typeof s === 'string') ? s : (s.text || '');
          const cmds   = (typeof s === 'object' && Array.isArray(s.commands)) ? s.commands : [];

          li.textContent = text;

          if (cmds.length){
            const pre = document.createElement('pre');
            pre.className = 'mt-1 bg-gray-50 border rounded p-2 text-xs overflow-x-auto';
            pre.textContent = cmds.join('\n');
            li.appendChild(pre);
          }

          ol.appendChild(li);
        });
        stepsBox.appendChild(ol);
      }

      function renderVerify(list){
        verifyBox.innerHTML = '';
        if (!Array.isArray(list) || !list.length) return;

        const title = document.createElement('div');
        title.className = 'font-semibold mt-4';
        title.textContent = 'Verify';
        verifyBox.appendChild(title);

        const ul = document.createElement('ul');
        ul.className = 'list-disc pl-6 text-sm text-gray-700';
        list.forEach(v => {
          const li = document.createElement('li');
          li.textContent = v;
          ul.appendChild(li);
        });
        verifyBox.appendChild(ul);
      }

      runBtn.addEventListener('click', async () => {
        const text = (aiDesc.value || '').trim();
        if (!text) { alert('Please enter your description first.'); return; }

        runBtn.disabled = true;
        statusEl.textContent = 'Thinking…';
        box.classList.add('hidden');
        actions.classList.add('hidden');
        nonTechBtn.classList.add('hidden');
        techBtn.classList.add('hidden');
        stepsBox.innerHTML = '';
        verifyBox.innerHTML = '';   // clear verify area between runs
        summary.textContent = '';
        meta.textContent = '';

        try {
          const res = await fetch("{% url 'student_ai_analyze' %}", {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-CSRFToken": getCookie("csrftoken") },
            body: JSON.stringify({ text })
          });

        try {
          const clfResp = await fetch("{% url 'classify_api' %}", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({ text })
          });
          const clf = await clfResp.json();
          if (!clfResp.ok) throw new Error(clf.detail || clf.error || "Classification failed");

          document.getElementById('pred-cat').textContent =
            `${clf.label} (${(clf.score * 100).toFixed(1)}%)`;

         
          document.getElementById('ai_category').value = clf.label;
          const sel = document.getElementById('category');
          if (sel) sel.value = clf.label;
        } catch (e) {
          document.getElementById('pred-cat').textContent = '—';
          console.error(e);
        }


          const data = await res.json();
          if (!res.ok) throw new Error(data.detail || data.error || "Request failed");

          const ui = data.ui || {};
          meta.textContent    = `Category: ${ui.category || '—'} | Technical: ${ui.is_technical ? 'true' : 'false'}`;
          summary.textContent = ui.summary || '';

          // render steps + verify
          renderSteps(ui.steps || []);
          renderVerify(ui.verify || []);

          // set hidden fields for submission
          hidTech.value = ui.is_technical ? 'true' : 'false';
          //hidCat.value  = ui.category || '';
          hidId.value   = ui.ai_record_id || '';

          // show correct action
          actions.classList.remove('hidden');
          if (ui.is_technical === false) {
            nonTechBtn.classList.remove('hidden');   // Open Ticket
          } else {
            techBtn.classList.remove('hidden');      // Escalate
          }

          box.classList.remove('hidden');
          statusEl.textContent = 'Ready';
        } catch (e) {
          statusEl.textContent = 'Error: ' + (e.message || e);
        } finally {
          runBtn.disabled = false;
        }
      });
    })();
  </script>

"""