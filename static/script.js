document.getElementById('predictionForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const submitBtn = document.getElementById('submitBtn');
    const resultCard = document.getElementById('resultCard');
    const resultTitle = document.getElementById('resultTitle');
    const resultDetails = document.getElementById('resultDetails');

    submitBtn.innerText = 'Analyzing Data...';
    submitBtn.disabled = true;

    const payload = {
        Age: document.getElementById('Age').value,
        BMI: document.getElementById('BMI').value,
        Glucose: document.getElementById('Glucose').value,
        Insulin: document.getElementById('Insulin').value,
        HOMA: document.getElementById('HOMA').value,
        Leptin: document.getElementById('Leptin').value,
        Adiponectin: document.getElementById('Adiponectin').value,
        Resistin: document.getElementById('Resistin').value,
        MCP1: document.getElementById('MCP1').value
    };

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok) {
            resultCard.classList.remove('hidden', 'healthy', 'danger');

            if (data.prediction === 1) {
                resultCard.classList.add('danger');
                resultTitle.innerText = '⚠️ HIGH RISK DETECTED';
                resultDetails.innerText = `Model Confidence: ${data.confidence}%`;
            } else {
                resultCard.classList.add('healthy');
                resultTitle.innerText = '✅ HEALTHY / LOW RISK';
                resultDetails.innerText = `Model Confidence: ${data.confidence}%`;
            }
        } else {
            alert(data.error || 'Prediction failed.');
        }
    } catch (error) {
        alert('Server communication error. Make sure app.py is running.');
    } finally {
        submitBtn.innerText = 'Predict Cancer Risk';
        submitBtn.disabled = false;
    }
});