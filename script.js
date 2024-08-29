async function analyzeTranscript() {
    const transcript = document.getElementById('transcriptInput').value;

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: transcript })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok.');
        }

        const result = await response.json();
        displayResults(result);
    } catch (error) {
        console.error('There was a problem with the fetch operation:', error);
    }
}

function displayResults(result) {
    const requirementsList = document.querySelector("#customerRequirements ul");
    const policiesList = document.querySelector("#companyPolicies ul");
    const objectionsList = document.querySelector("#customerObjections ul");

    requirementsList.innerHTML = result.has_requirements ? '<li>Requirement found</li>' : '<li>No requirements found</li>';
    policiesList.innerHTML = result.has_policies ? '<li>Policy discussed</li>' : '<li>No policies discussed</li>';
    objectionsList.innerHTML = result.has_objections ? '<li>Objection raised</li>' : '<li>No objections raised</li>';

    const output = document.getElementById('output');
    const resultText = result.prediction;
    const predictionDiv = document.createElement('div');
    predictionDiv.textContent = `Prediction: ${resultText}`;
    output.appendChild(predictionDiv);
}
