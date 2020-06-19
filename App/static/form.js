const uploadForm = document.querySelector('#uploadForm');
const urlForm = document.querySelector('#urlForm');
const toggleBtn = document.querySelector('#toggleForm');
const formHolder = document.querySelector('#formHolder');

function swapForms(e) {
	console.log(e);
	if (e.target.innerHTML === 'URL?') {
		toggleBtn.innerHTML = 'Upload Image?';
		uploadForm.className = 'hidden';
		urlForm.className = '';
	} else {
		toggleBtn.innerHTML = 'URL?';
		uploadForm.className = '';
		urlForm.className = 'hidden';
	}
}

toggleBtn.addEventListener('click', swapForms);
