function searchMessages() {
		const searchTerm = document.getElementById('search-input').value;
		const resultsContainer = document.getElementById('search-results');

		if (!searchTerm) {
				resultsContainer.innerHTML = ''; // Clear results if search term is empty
				return;
		}

		fetch('/search', {
						method: 'POST',
						headers: {
								'Content-Type': 'application/x-www-form-urlencoded',
						},
						body: `search_term=${searchTerm}`,
				})
				.then(response => {
						 if (!response.ok) {
								throw new Error('Network response was not ok');
						}
						return response.json();

				})
				.then(results => {
						resultsContainer.innerHTML = ''; // Clear previous results
						if (results.error) { //Check for errors first
								resultsContainer.innerHTML = `<p>${results.error}</p>`; // Display error message if any

								return;
						}

						if (results.length === 0) {
								resultsContainer.innerHTML = '<p>No results found.</p>';
						} else {
								const ul = document.createElement('ul');
								results.forEach(result => {
										const li = document.createElement('li');
										const messageType = result.type.charAt(0).toUpperCase() + result.type.slice(1); // Capitalize message type
										li.innerHTML = `<p><strong>${messageType}: ${result.name}</strong> - ${result.text}</p><small>${result.time}</small>`;
										ul.appendChild(li);

								});
								resultsContainer.appendChild(ul);
						}
				})
				.catch(error => {
						resultsContainer.innerHTML = `<p>Error: ${error.message}</p>`; // More specific error messaging
				});

}