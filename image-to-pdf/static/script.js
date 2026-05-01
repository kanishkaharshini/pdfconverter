const dropZone   = document.getElementById('dropZone');
const fileInput  = document.getElementById('fileInput');
const previewSection = document.getElementById('previewSection');
const previewGrid    = document.getElementById('previewGrid');
const optionsPanel   = document.getElementById('optionsPanel');
const convertBtn     = document.getElementById('convertBtn');
const successMsg     = document.getElementById('successMsg');
const fileCountEl    = document.getElementById('fileCount');

let selectedFiles = [];

// Click drop zone → open file picker
dropZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', e => addFiles([...e.target.files]));

// Drag and drop
dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('dragover'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
dropZone.addEventListener('drop', e => {
  e.preventDefault();
  dropZone.classList.remove('dragover');
  addFiles([...e.dataTransfer.files]);
});

function addFiles(files) {
  const valid = files.filter(f => /\.(jpg|jpeg|png|gif|bmp|webp)$/i.test(f.name));
  selectedFiles = [...selectedFiles, ...valid];
  renderPreviews();
}

function renderPreviews() {
  previewGrid.innerHTML = '';
  selectedFiles.forEach((file, i) => {
    const url = URL.createObjectURL(file);
    const div = document.createElement('div');
    div.className = 'preview-item';
    div.innerHTML = `
      <img src="${url}" alt="${file.name}">
      <button class="remove-btn" data-index="${i}">✕</button>
      <div class="file-name">${file.name}</div>
    `;
    previewGrid.appendChild(div);
  });

  previewGrid.querySelectorAll('.remove-btn').forEach(btn => {
    btn.addEventListener('click', e => {
      e.stopPropagation();
      selectedFiles.splice(Number(btn.dataset.index), 1);
      renderPreviews();
    });
  });

  const hasFiles = selectedFiles.length > 0;
  previewSection.style.display = hasFiles ? 'block' : 'none';
  optionsPanel.style.display   = hasFiles ? 'block' : 'none';
  convertBtn.style.display     = hasFiles ? 'block' : 'none';
  successMsg.style.display     = 'none';
  fileCountEl.textContent = `${selectedFiles.length} image${selectedFiles.length > 1 ? 's' : ''} selected`;
}

document.getElementById('clearBtn').addEventListener('click', () => {
  selectedFiles = [];
  renderPreviews();
});

convertBtn.addEventListener('click', async () => {
  if (!selectedFiles.length) return;

  // Show loading state
  convertBtn.disabled = true;
  document.getElementById('btnText').style.display = 'none';
  document.getElementById('btnLoader').style.display = 'inline';
  successMsg.style.display = 'none';

  const formData = new FormData();
  selectedFiles.forEach(f => formData.append('images', f));
  formData.append('page_size',    document.getElementById('pageSize').value);
  formData.append('orientation',  document.getElementById('orientation').value);
  formData.append('fit_mode',     document.getElementById('fitMode').value);
  formData.append('margin',       document.getElementById('margin').value);
  formData.append('bg_color',     document.getElementById('bgColor').value);
  formData.append('add_filename', document.getElementById('addFilename').checked);

  try {
    const res = await fetch('/convert', { method: 'POST', body: formData });
    if (!res.ok) {
      const err = await res.json();
      alert('Error: ' + err.error);
      return;
    }
    // Trigger download
    const blob = await res.blob();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'converted.pdf';
    a.click();
    successMsg.style.display = 'block';
  } catch (err) {
    alert('Something went wrong: ' + err.message);
  } finally {
    convertBtn.disabled = false;
    document.getElementById('btnText').style.display = 'inline';
    document.getElementById('btnLoader').style.display = 'none';
  }
});