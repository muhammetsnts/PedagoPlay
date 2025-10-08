// DOM Elements
const form = document.getElementById('activityForm');
const submitBtn = document.getElementById('submitBtn');
const btnText = document.querySelector('.btn-text');
const btnLoading = document.querySelector('.btn-loading');
const resultsContainer = document.getElementById('results');
const activitiesContent = document.getElementById('activitiesContent');
const errorContainer = document.getElementById('error');
const errorMessage = document.getElementById('errorMessage');

// Form submission handler
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Hide previous results/errors
    hideResults();
    hideError();
    
    // Show loading state
    setLoading(true);
    
    try {
        // Get form data
        const formData = getFormData();
        
        // Validate form data
        if (!validateFormData(formData)) {
            throw new Error('Please fill in all required fields correctly.');
        }
        
        // Make API request
        const response = await fetch('/api/activities', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        // Check if response is ok
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Check if response has content
        const responseText = await response.text();
        if (!responseText) {
            throw new Error('Empty response from server');
        }
        
        let data;
        try {
            data = JSON.parse(responseText);
        } catch (parseError) {
            console.error('Response text:', responseText);
            throw new Error('Invalid JSON response from server');
        }
        
        if (data.success) {
            showResults(data.activities);
        } else {
            throw new Error(data.error || 'Failed to get activities');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'Something went wrong. Please try again.');
    } finally {
        setLoading(false);
    }
});

// Get form data
function getFormData() {
    const numChildren = parseInt(document.getElementById('numChildren').value);
    const agesInput = document.getElementById('ages').value;
    const ages = agesInput.split(',').map(age => parseInt(age.trim())).filter(age => !isNaN(age));
    const weather = document.getElementById('weather').value;
    const location = document.getElementById('location').value;
    const specialCases = document.getElementById('specialCases').value;
    
    return {
        num_children: numChildren,
        ages: ages,
        weather: weather,
        location: location,
        special_cases: specialCases || "No special case."
    };
}

// Validate form data
function validateFormData(data) {
    if (!data.num_children || data.num_children < 1) {
        alert('Please enter a valid number of children (at least 1).');
        return false;
    }
    
    if (!data.ages || data.ages.length === 0) {
        alert('Please enter valid ages for the children.');
        return false;
    }
    
    if (data.ages.some(age => age < 0 || age > 18)) {
        alert('Please enter realistic ages for children (0-18 years).');
        return false;
    }
    
    if (!data.weather || !data.location) {
        alert('Please fill in weather and location information.');
        return false;
    }
    
    return true;
}

// Set loading state
function setLoading(loading) {
    if (loading) {
        submitBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoading.style.display = 'inline';
    } else {
        submitBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
    }
}

// Show results
function showResults(activities) {
    activitiesContent.textContent = activities;
    resultsContainer.style.display = 'block';
    resultsContainer.scrollIntoView({ behavior: 'smooth' });
}

// Hide results
function hideResults() {
    resultsContainer.style.display = 'none';
}

// Show error
function showError(message) {
    errorMessage.textContent = message;
    errorContainer.style.display = 'block';
    errorContainer.scrollIntoView({ behavior: 'smooth' });
}

// Hide error
function hideError() {
    errorContainer.style.display = 'none';
}

// Clear results
function clearResults() {
    hideResults();
    form.reset();
    // Set default values
    document.getElementById('numChildren').value = 1;
    document.getElementById('ages').value = '4';
    document.getElementById('weather').value = 'sunny';
    document.getElementById('location').value = 'Yverdon-les-Bains';
    document.getElementById('specialCases').value = 'No special case.';
}

// Clear error
function clearError() {
    hideError();
}

// Add some fun animations and interactions
document.addEventListener('DOMContentLoaded', function() {
    // Add floating animation to the title
    const title = document.querySelector('.title');
    if (title) {
        title.style.animation = 'float 3s ease-in-out infinite';
    }
    
    // Add hover effects to form inputs
    const inputs = document.querySelectorAll('.form-input, .form-select, .form-textarea');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.style.transform = 'scale(1.02)';
        });
        
        input.addEventListener('blur', function() {
            this.style.transform = 'scale(1)';
        });
    });
    
    // Add click animation to buttons
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
        });
    });
});

// Add floating animation keyframes
const style = document.createElement('style');
style.textContent = `
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .form-input:focus,
    .form-select:focus,
    .form-textarea:focus {
        transform: scale(1.02) translateY(-2px) !important;
    }
`;
document.head.appendChild(style);

// Add some fun sound effects (optional - can be removed if not needed)
function playClickSound() {
    // Simple click sound using Web Audio API
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
    oscillator.frequency.exponentialRampToValueAtTime(400, audioContext.currentTime + 0.1);
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.1);
}

// Add click sound to submit button
submitBtn.addEventListener('click', playClickSound);
