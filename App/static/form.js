const uploadForm = document.querySelector('#uploadForm');
const urlForm = document.querySelector('#urlForm');
const toggleCheckbox = document.querySelector('#url-toggle');

function swapForms(e) {
	if (e.target.checked) {
		uploadForm.className = 'hidden';
		urlForm.className = '';
	} else {
		uploadForm.className = '';
		urlForm.className = 'hidden';
	}
}

toggleCheckbox.addEventListener('change', swapForms);
