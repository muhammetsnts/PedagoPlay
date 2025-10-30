// DOM elements
const form = document.getElementById("activityForm");
const submitBtn = document.getElementById("submitBtn");
const btnText = document.querySelector(".btn-text");
const btnLoading = document.querySelector(".btn-loading");
const resultsContainer = document.getElementById('results');
const activitiesContent = document.getElementById("activitiesContent");
const errorContainer = document.getElementById('error');
const errorMessage = document.getElementById("errorMessage");

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    // hide previous results
    hideError();
    hideResults();
    setLoading(true);

    try {
        // get form data
        const formData = getFormData();

        // validate form data
        if (!validateFormData(formData)) {
            throw new Error("Please fill in all required fields correctly.");
        }

        // make API request
        const response = await fetch("/api/activities", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        // check if response is OK
        if (!response.ok) {
            throw new Error(`HTTPS error! status: ${response.status}`);
        }

        const responseText = await response.text();
        let data;
        
        try {
            data = JSON.parse(responseText);
        }
        catch (parseError) {
            console.error("Response text:", responseText);
            throw new Error("Invalid JSON response from server");
        }

        if (data.success) {
            showResults(data.activities);
            // console.log(data.activities)
        }
        else {
            throw new Error(data.error || "Failed to get activities");
        }

    }

    catch (error) {
        console.error("Error:", error);
        showError(error.message || "Oops! Something went wrong. Please try again.")
    }

    finally {
        setLoading(false)
    }
})


// hide error
function hideError() {
    errorContainer.style.display = "none";
}

// hide results
function hideResults() {
    resultsContainer.style.display = "none";
}

// set loading
function setLoading(loading) {
    if (loading) {
        submitBtn.disabled = true;
        btnText.style.display = "none";
        btnLoading.style.display = "inline";
    }
    else {
        submitBtn.disabled = false;
        btnText.style.display = "inline";
        btnLoading.style.display = "none";
    }
}

// get form data
function getFormData() {
    const numChildren = parseInt(document.getElementById("numChildren").value);
    const agesInput = document.getElementById("ages").value;
    const ages = agesInput.split(",").map(age => parseInt(age.trim())).filter(age => !isNaN(age));
    const weather = document.getElementById("weather").value;
    const location = document.getElementById("location").value;
    const specialCases = document.getElementById("specialCases").value;

    return {
        num_children: numChildren,
        ages: ages,
        weather: weather,
        location: location,
        special_cases: specialCases || "No special case."
    };
}

function validateFormData(data) {
    if (!data.num_children || data.numChildren <1) {
        alert('Please enter a valid number of children (at least 1).');
        return false;
    }

    if (!data.ages || data.ages.length === 0) {
        alert('Please enter valid ages for the children.');
        return false;
    }

    if (data.ages.some(age => age <0 || age > 18)) {
        alert('Please enter realistic ages for children (0-18 years).');
        return false;
    }

    if (!data.weather || !data.location) {
        alert('Please fill in weather and location information.');
        return false;
    }

    return true;
}

// show error
function showError(message) {
    errorMessage.textContent = message;
    errorContainer.style.display = "block";
    errorContainer.scrollIntoView({behavior:"smooth"});
}

function showResults(activities) {
    resultsContainer.style.display = "block";
    activitiesContent.innerHTML = activities;
    resultsContainer.scrollIntoView({behavior:"smooth"});
    submitBtn.style.display = "none";
}

// clear results
function clearResults () {
    hideResults();
    form.reset();
    submitBtn.style.display = "inline";

    // set default values
    document.getElementById("numChildren").value = 1;
    document.getElementById("ages").value = "4";
    document.getElementById("weather").value = "sunny";
    document.getElementById("location").value = "Yverdon-les-Bains";
    document.getElementById("specialCases").value = "No special case.";
}

// Clear error
function clearError() {
    hideError();
}

function playClickSound() {
    // Simple click sound for submit button
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